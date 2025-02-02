from joblib import Memory, expires_after
from dotenv import load_dotenv
from app.util.supabase.service import get_profile_id_from_user_id
import os
from supabase import create_client, Client

load_dotenv(override=True)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

memory = Memory("cachedir")

@memory.cache(cache_validation_callback=expires_after(seconds=10*60)) # 10 minutes
def personality_traits_pipeline(profile_id: str) -> str | None:    
    response = (
        supabase.table("personality_scores")
        .select("description")
        .eq("profile_id", profile_id)
        .execute()
    )
    response_text = ""

    for result in response.data:
        response_text += result["description"] + ", "

    return response_text


if __name__ == "__main__":
    print(personality_traits_pipeline(get_profile_id_from_user_id(user_id="baf9d68e-12b8-4336-af62-f6f8e28e95f3"))) 
    print(personality_traits_pipeline("12")) 
    print(personality_traits_pipeline("13")) 
    print(personality_traits_pipeline("14")) 
    print(personality_traits_pipeline("15")) 
    print(personality_traits_pipeline("16")) 
    print(personality_traits_pipeline("17")) 
