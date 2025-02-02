from typing import List
from app.models import PersonalizedFinetunedAIModel
from app.models import general_ai_model
from app.services.reply.helper import clean_xml_tags, extract_reply_from_prompt, find_system_message, prettify_conversation_history, reflect_reply
from app.services.reply.logger import create_logger, debug
from app.services.reply.prompt import add_fullstop_to_reply_prompt, fix_reply_prompt, generate_plan_prompt, generate_reply_from_plan_prompt, rephrase_reply_prompt, stringify_personality_traits, stringify_rag
from app.types import ExtendedConversationMessage
from app.services.rag.rag import rag_pipeline
from app.util.supabase.service import get_profile_id_from_ft_model_id, get_profile_id_from_user_id, get_user_id_from_ft_model_id
from app.services.personality.personality import personality_traits_pipeline

# Pipeline for replying the text based on user's chat input

# CURRENT: RAG PIPELINE + PERSONALITY TRAITS, optional params for rag, reply, and <br> usage
def reply_pipeline(conversation_history: List[ExtendedConversationMessage], ft_model_id: str, soul_name: str, additional_prompt: str | None, apikey: str | None, with_rag: bool, with_personality: bool, with_br: bool) -> str:
    # TODO logger_id as identifier for the pipeline call, return to the caller
    log_time, log_steps, log, logger_id = create_logger()
    
    log_steps("Initialization")
    log(f"with_rag: {with_rag}, with_personality: {with_personality}, with_br: {with_br}")
    personalized_ft_ai_model = PersonalizedFinetunedAIModel(apikey)
    prettified_conversation_history = prettify_conversation_history(conversation_history, soul_name)
    
    system_message = find_system_message(conversation_history)
    ai_chat_completion_history = []
    if system_message:
        ai_chat_completion_history.append(system_message)

    log_time("Initialization")
    
    # RAG Stuff from Personal Knowledge Base can be done here
    # WARNING For now, only Rizky has access to RAG
    knowledge = None
    knowledge_string = ""

    if with_rag:
        log_steps("RAG")
        try:
            # if soul_name contains "rizky"
            if "rizky" in soul_name.lower():
                knowledge = rag_pipeline(prettified_conversation_history)
            if knowledge is not None and knowledge.strip():
                knowledge_string = stringify_rag(knowledge=knowledge)
        except Exception as e:
            log(f"Error in RAG: {e}")
            log("Skipping RAG due to an Error")
        log_time("RAG")
        if knowledge is not None and knowledge.strip():
            log("Retrieved Knowledge:")
            log(knowledge)
        else:
            log("No Knowledge found")
    else:
        log("Skipping RAG: with_rag is false")

    # ---------- END OF RAG STUFF ----------


    # Let LLM check personality traits sampling past conversation history
    personality_traits = None
    personality_traits_string = ""

    if with_personality:
        log_steps("Personality")
        # Hardcoded Rizky
        if "rizky" in soul_name.lower():
            personality_traits = personality_traits_pipeline(get_profile_id_from_user_id(user_id="baf9d68e-12b8-4336-af62-f6f8e28e95f3"))
        # Non Rizky will check the db for personality traits
        else:
            profile_id = get_profile_id_from_ft_model_id(ft_model_id)
            if profile_id is not None:
                personality_traits = personality_traits_pipeline(profile_id=profile_id)
        if personality_traits is not None:
            personality_traits_string = stringify_personality_traits(personality_traits)
        log_time("Personality")
        log("Retrieved:")
        log(personality_traits)
    else:
        log("with_personality is false, skipping personality traits")
    debug(personality_traits_string)
    # ---------- END OF PERSONALITY TRAITS STUFF ----------


    log_steps("Generate Plan")
    # Plan -- Use a Strong General AI model to Plan and Generate the Initial Response
    plan_prompt_1 = generate_plan_prompt(soul_name, personality_traits_string, knowledge_string, prettified_conversation_history)
    # When crafting plan, add additional prompt from frontend if needed
    if additional_prompt is not None:
        plan_prompt_1 += "\n\nGiven this hint: \n" + additional_prompt
    ai_chat_completion_history.append({"role": "user", "content": plan_prompt_1})
    # call the General AI Model to generate the plan
    out_plan_1 = general_ai_model.generate_text(ai_chat_completion_history)
    ai_chat_completion_history.append({"role": "assistant", "content": out_plan_1})
    log_time("Generate Plan")
    log("Generated Plan:")
    log(out_plan_1)
    
    
    log_steps("Generate Reply")
    
    # Experimental try using FT to generate the reply
    plan_prompt_2 = generate_reply_from_plan_prompt(extract_reply_from_prompt(prompt=out_plan_1, reply_tag="Plan"))
    ai_chat_completion_history.append({"role": "user", "content": plan_prompt_2})
    out_plan_2 = personalized_ft_ai_model.generate_text(ai_chat_completion_history, ft_model_id)
    ai_chat_completion_history.append({"role": "assistant", "content": out_plan_2})
    reply_str = extract_reply_from_prompt(out_plan_2)
    log_time("Generate Reply")
    log("Conversation history:")
    log(prettified_conversation_history)
    log("Generated Reply:")
    log(reply_str)
    
    # br will be added by general AI
    if with_br:
        br_chat_conversation_history = []
        log_steps("Add Line Break")
        act_prompt_br = add_fullstop_to_reply_prompt(sentence=reply_str, fullstop="<br>")
        br_chat_conversation_history.append({"role": "user", "content": act_prompt_br})
        # Let general AI choose the fullstop
        out_act_2 = general_ai_model.generate_text(br_chat_conversation_history)
        rephrased_reply_2 = extract_reply_from_prompt(out_act_2, reply_tag="Sentence")
        reply = rephrased_reply_2
        log_time("Add Line Break")
        log("Added line break:")
        log(reply)
    else:
        reply = reply_str
    

    log_steps("Reflect")
    # Reflect -- Use a Strong General AI model to reflect on the response.
    message_is_good, ai_chat_completion_history = reflect_reply(reply, ai_chat_completion_history, general_ai_model)

    log_time("Reflect")
    log("Message is good? " + str(message_is_good))

    message_is_fixed = False
    iterations = 1
    while not message_is_good and iterations <= 3:
        message_is_fixed = True
        fix_prompt_1 = fix_reply_prompt()

        ai_chat_completion_history.append({"role": "user", "content": fix_prompt_1})
        # fix the reply using general model
        out_fix = general_ai_model.generate_text(ai_chat_completion_history)
        fixed_reply = extract_reply_from_prompt(out_fix, "FixedReply")

        message_is_good, ai_chat_completion_history = reflect_reply(fixed_reply, ai_chat_completion_history, general_ai_model)
        log_steps(f"fix iteration {iterations}", False)
        log_time(f"fix iteration {iterations}", False)
        log("Message is good (y/n)? " + str(message_is_good))
        log("Fixed Reply:\n" + str(fixed_reply))
        iterations += 1
        
    # prepare the final ai response
    out_message = fixed_reply if message_is_fixed else reply
    log_time("total", False)
    log("Final")
    out_message = clean_xml_tags(out_message)
    log(out_message)
    
    return out_message, logger_id

