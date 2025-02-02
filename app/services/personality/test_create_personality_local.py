# from joblib import Memory, expires_after
# memory = Memory("cachedirTest")
import random
import re
from app.models import general_ai_model

def extract_personality_trait(personality_traits: str) -> str:
    match = re.search(r"<PersonalityTraits>(.*?)</PersonalityTraits>", personality_traits)
    return match.group(1) if match else None

# @memory.cache(cache_validation_callback=expires_after(seconds=5*60)) # 5 minutes
def f(jsonl_path):
    # open the file 
    lines = []
    with open(jsonl_path, "r") as f:
        # read the file line by line 
        for line in f:
            lines.append(line)

    # get 15 random lines from the file
    conversation_history = random.sample(lines, 15)

    aspects = ["Gregariousness", "Assertiveness", "Sympathy", "Altruism", "Self-Discipline", "Anxiety", "Self-Consciousness", "Imagination", "Emotionality", "Cheerfulness"]
    low_markers = ["introverted", "timid", "unsympathetic", "unkind", "undisciplined", "relaxed", "unselfconscious", "unimaginative", "unreflective", "gloomy"]
    high_markers = ["extraverted", "bold", "sympathetic", "kind", "self-disciplined", "tense", "self-conscious", "imaginative", "reflective", "cheerful"]
    output = ""

    for (aspect, low_marker, high_marker) in zip(aspects, low_markers, high_markers):
        prompt = '''
Given a conversation history

<ConversationHistory>
{conversation_history}
</ConversationHistory>

Please rate the {aspect} aspect within a scale from 1 to 9 where
1 = "extremely {low_marker}", 
2 = "very {low_marker}",
3 = "{low_marker}",
4 = "a bit {low_marker}",
5 = "neither {low_marker} nor {high_marker}", 
6 = "a bit {high_marker}",
7 = "{high_marker}",
8 = "very {high_marker}",
9 = "extremely {high_marker}", 

Only answer starting with <PersonalityTraits> and ends with </PersonalityTraits>
Translate the number to the corresponding description.

For example
<PersonalityTraits>
neither {low_marker} nor {high_marker}
</PersonalityTraits>
'''.format(conversation_history="\n".join(conversation_history), aspect=aspect, low_marker=low_marker, high_marker=high_marker)

        out_text = general_ai_model.generate_text([{"role": "user", "content": prompt}])
        output += extract_personality_trait(out_text) + ", "

    return output



if __name__ == "__main__":
    # traits1 = f("/Users/notwatermango/Developer/Code/tka-projects/Soulink-Data-Processing-Services/Data/rizky_messages.jsonl")
    # print(traits1)
    # traits2 = f("/Users/notwatermango/Developer/Code/tka-projects/Soulink-Data-Processing-Services/Data/rizky_messages.jsonl")
    # print(traits2)
    # print(traits3)
    traits3 = f("/Users/notwatermango/Developer/Code/tka-projects/Soulink-Data-Processing-Services/Data/rizky_messages.jsonl")


# RESPONSES
# <PersonalityTraits>
# A bit friendly, Extraverted, Talkative, A bit timid, A bit unassertive, A bit active, A bit unenergetic, A bit unadventurous, Very cheerful, Trustful, Moral, Honest, A bit kind, Generous, Altruistic, Cooperative, A bit humble, Very sympathetic, Unselfish, Agreeable, A bit self-efficacious, A bit messy, Responsible, Hardworking, A bit self-disciplined, Neither impractical nor practical, A bit extravagant, Organized, Conscientious, Thorough, Relaxed, At ease, Easygoing, Calm, Patient, Happy, A bit self-conscious, A bit level-headed, Discontented, Emotionally stable, Imaginative, Creative, Artistically appreciative, Aesthetic, Reflective, Emotionally aware, Curious, A bit spontaneous, Intelligent, Analytical, Sophisticated, Socially progressive
# </PersonalityTraits>

# <PersonalityTraits>
# Very friendly, Extraverted, Talkative, A bit bold, Assertive, A bit active, A bit unenergetic, A bit adventurous and daring, Very cheerful, Trustful, Moral, Honest, A bit kind, Generous, Altruistic, Cooperative, A bit self-important, Very sympathetic, Unselfish, Agreeable, Self-efficacious, A bit messy, Responsible, Hardworking, A bit self-disciplined, Neither impractical nor practical, A bit extravagant, Organized, Conscientious, Thorough, Relaxed, Calm, Happy, A bit self-conscious, A bit level-headed, Discontented, Emotionally stable, Imaginative, Creative, Artistically appreciative, Aesthetic, A bit reflective, Emotionally aware, Curious, Spontaneous, Intelligent, Analytical, Sophisticated, Socially progressive
# </PersonalityTraits>

# <PersonalityTraits>
# A bit friendly, A bit extraverted, Talkative, Neither timid nor bold, Assertive, Active, A bit unenergetic, A bit unadventurous, Cheerful, Trustful, Moral, Honest, Kind, Generous, Altruistic, Cooperative, A bit self-important, Sympathetic, Unselfish, Agreeable, Self-efficacious, Orderly, Responsible, Hardworking, Self-disciplined, Practical, Thrifty, Organized, Conscientious, Thorough, Relaxed, At ease, Easygoing, Calm, Patient, Happy, A bit self-conscious, Level-headed, Discontented, Emotionally stable, Imaginative, Creative, Artistically appreciative, Aesthetic, Reflective, Emotionally aware, Curious, Spontaneous, Intelligent, Analytical, Sophisticated, Socially progressive
# </PersonalityTraits>

# '''
# A bit friendly, Extraverted, Talkative, A bit timid, A bit unassertive, A bit active, Very cheerful, ...

# Very extraverted, a bit sympathetic, kind, neither undisciplined nor self-disciplined, relaxed, a bit unselfconscious ...


# neither unimaginative nor imaginative, a bit unreflective, very cheerful.

# Trustful, Honest, A bit kind, Generous, Cooperative, A bit humble, Very sympathetic, Agreeable, A bit self-efficacious, A bit messy, Responsible, Hardworking, A bit self-disciplined, Neither impractical nor practical, Easygoing, Calm, Patient, Happy, A bit self-conscious, Aesthetic, Reflective, Emotionally aware, Curious, A bit spontaneous, Intelligent, Analytical, Sophisticated, Socially progressive
# '''

# Gregariousness
# introverted
# extraverted

# Assertiveness
# timid

# st = '''


# Friend: Living life I see


# Friend: Lots of activities hiking
# Person: Yeah! Making new friends, enjoying nature!




# Friend: Oh wow that sounds exciting tho


# Is the generated reply:
# 1. correct to {Person}'s
# Personality Traits?
# 2. adhere to {Person}'s
# Stylometric Features?
# 3. truthful to {Person}'s
# Biographical Facts?


# '''



# Draft for screenshots
# test = '''

# You are a person named <Name>{Person}</Name>. 
# Given a conversation history that consist of 

# <Messages>
# {Messages}
# </Messages>. 

# Generate a reply to the conversation



# '''

#     personality_traits_stringzzz = '''
# Given your personality traits

# <Personality traits>
# {personality_traits}
# </Personality traits>

# '''

#     knowledge_stringzzzzz = '''
# Given the knowledge below

# <Knowledge>
# {knowledge}
# </Knowledge>
# '''

#     teszzzz = '''
# Is the generated reply:
# 1. adhere to {person}'s Linguistic Cues?
# 2. truthful to {person}'s 
# Personal Facts?
# 3. correct to {person}'s Personality Trait? 
# '''




