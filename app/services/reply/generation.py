import time
import random
from app.logger import get_logger
from app.types import (
    Message,
    ConversationHistory,
    Profile,
    GenerationDecision,
    GenerationResponse,
)
from app.services.reply.prompt import generate_should_reply_prompt
from app.services.rag.rag import rag_pipeline
from app.models import general_ai_model

logger = get_logger("generation")


def get_example_conversation_history(message: Message) -> ConversationHistory:
    """
    Temporary function to get example conversation history.
    To be replaced with actual implementation.
    """
    logger.info("Getting example conversation history")
    return ConversationHistory(
        messages=[
            Message(
                content="So, we are going to solve the problem of is it ethical to use AI to copy a digital identity. I think it is not because the digital identity is not a physical object.",
                role="user",
                sender_name="Alice",
                timestamp="2024-02-02T10:00:00Z",
            ),
            Message(
                content="Well, I think it is ethical to use AI to copy a digital identity, under the case that the person being copied agrees to it.",
                role="assistant",
                sender_name="Banghao Chi",
                timestamp="2024-02-02T10:00:05Z",
            ),
            message,
        ]
    )

def get_conversation_history(message: Message) -> ConversationHistory:
    """
    Get the conversation history from the database.
    """
    logger.info("Getting conversation history from the database")
    return get_example_conversation_history(message)


def get_example_profile(person_name: str) -> Profile:
    """
    Temporary function to get example profile.
    To be replaced with actual implementation.
    """
    logger.info(f"Getting example profile for {person_name}")
    return Profile(
        personality_traits=f"{person_name} is a very kind...",
        communication_style=f"{person_name} doesn't use period a lot...",
    )


def get_profile(message: Message) -> Profile:
    """
    Get the profile from the database.
    """
    logger.info("Getting profile from the database")
    return get_example_profile(message.sender_name)


def should_reply_to_message(
    message: Message,
    conversation_history: ConversationHistory,
    profile: Profile,
    name: str,
    rag_results: str,
) -> GenerationDecision:
    """
    Ask LLM whether to reply to the message based on current context
    """
    logger.info("Determining if message should be replied to")

    prompt = generate_should_reply_prompt(message, name, conversation_history, profile, rag_results)

    response = general_ai_model.generate_text([{"role": "user", "content": prompt}])
    try:
        import json

        decision = json.loads(response)
        return GenerationDecision(**decision)
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        return GenerationDecision(
            should_reply=False, reason="Error in processing decision"
        )


def generate_response(
    message: Message,
    conversation_history: ConversationHistory,
    profile: Profile,
    name: str,
) -> GenerationResponse:
    """
    Main response generation pipeline
    """
    start_time = time.time()
    logger.info("Starting response generation pipeline")

    # Step 1: Get relevant facts using RAG
    try:
        rag_results = rag_pipeline(
            "\n".join(
                [
                    f"{msg.sender_name} ({msg.role}): {msg.content}"
                    for msg in conversation_history.messages
                ]
            ),
            name,
        )
        logger.info("RAG results retrieved successfully")
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {e}")
        rag_results = None

    # Step 2: Determine if we should reply with all the context
    decision = should_reply_to_message(message, conversation_history, profile, name, rag_results)
    if not decision.should_reply:
        logger.info(f"Decided not to reply: {decision.reason}")
        return GenerationResponse(
            response="", should_reply=False, reason=decision.reason
        )

    # Step 3: Generate the response using all available context
    prompt = f"""You are a person named <Name>{name}</Name>, not an assistant. You are chatting with other people on a real-time chat app just like a normal human would, not an assistant. Given the following context, generate a reply message that matches the person's personality, communication style, and factual information.

Profile:
Personality: {profile.personality_traits}
Communication Style: {profile.communication_style}

{f"Relevant Context from Knowledge Base:{chr(10)}{rag_results}" if rag_results else ""}

Complete Conversation History:
{chr(10).join([f"{msg.sender_name} ({msg.role}): {msg.content}" for msg in conversation_history.messages])}

Latest Message from {message.sender_name}:
{message.content}

When generating the reply message, follow these guidelines:
1. Generate a natural response that matches the profile.
2. Use the factual information to make the response more accurate if applicable.
3. Use the communication style to make the response more natural.
4. Use the personality to make the response more engaging.
5. Use the latest message from {message.sender_name} to make the response more relevant.
6. Your reply message should be mostly a single sentence. If you need to say more, do so in an appropriate manner with two or three sentences at most.

Generate a natural response that matches the profile and return only the reply message, do not include any preamble or explanation. Now, start generating the reply message:"""
    
    end_time = time.time()
    logger.info(f"Time taken to generate prompt: {end_time - start_time} seconds")
    if end_time - start_time < 3:
        sleep_time = random.uniform(2, 4)
        time.sleep(sleep_time)
        logger.info(f"Sleeping for {sleep_time} seconds since it's too fast")

    try:
        response = general_ai_model.generate_text([{"role": "user", "content": prompt}])
        logger.info("Response generated successfully")
        return GenerationResponse(response=response, should_reply=True, reason=None)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return GenerationResponse(
            response="",
            should_reply=False,
            reason=f"Error generating response: {str(e)}",
        )


if __name__ == "__main__":
    # Set up test message
    test_message = Message(
        content="I think you make a good point about consent. But what about the potential misuse of such technology?",
        role="user",
        sender_name="Charlie",
        timestamp="2024-02-02T10:00:10Z",
    )

    # Test assistant name
    assistant_name = "Banghao Chi"

    print("\n=== Testing Generation Pipeline ===\n")

    print("1. Getting conversation history...")
    conversation_history = get_conversation_history(test_message)
    print("\nConversation History:")
    for msg in conversation_history.messages:
        print(f"{msg.sender_name} ({msg.role}): {msg.content}")

    print("\n2. Getting assistant profile...")
    profile = get_profile(test_message)
    print(f"\nProfile for {assistant_name}:")
    print(f"Personality: {profile.personality_traits}")
    print(f"Communication Style: {profile.communication_style}")

    print("\n3. Generating response...")
    response = generate_response(
        message=test_message,
        conversation_history=conversation_history,
        profile=profile,
        name=assistant_name,
    )

    print("\nGeneration Results:")
    print(f"Should Reply: {response.should_reply}")
    if response.should_reply:
        print(f"Response: {response.response}")
    else:
        print(f"Reason for not replying: {response.reason}")
