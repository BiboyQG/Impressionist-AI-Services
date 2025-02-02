from typing import List, Dict
import openai
from fastapi import HTTPException
from app.config import Config
from app.services.reply.logger import debug

class GeneralAIModel:
    def __init__(self, api_key: str, model_name: str):
        openai.api_key = api_key
        self.model_name = model_name

    def generate_text(self, conversation_history: List[Dict[str, str]]) -> str:
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=conversation_history,
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# TODO refactor this from PersonalBot-Backend Repo
class PersonalizedFinetunedAIModel:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_text(self, conversation_history: List[Dict[str, str]], ft_model_id: str) -> str:
        try:
            debug("DEBUG PERSONALIZED FINETUNED AI MODEL")
            debug(conversation_history)
            response = openai.chat.completions.create(
                model=ft_model_id,
                messages=conversation_history,
                temperature=0
            )
            debug("RESPONSE FROM PERSONALIZED FINETUNED AI MODEL")
            debug(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class FastAIModel:
    def __init__(self, api_key: str, model_name: str):
        openai.api_key = api_key
        self.model_name = model_name

    def generate_text(self, conversation_history: List[Dict[str, str]]) -> str:
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=conversation_history,
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


general_ai_model = GeneralAIModel(Config.OPENAI_API_KEY, Config.GEN_MODEL_NAME)
fast_ai_model = FastAIModel(Config.OPENAI_API_KEY, Config.FAST_MODEL_NAME)