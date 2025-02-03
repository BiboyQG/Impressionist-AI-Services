from typing import List, Dict
import openai
from fastapi import HTTPException
from app.config import Config

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
        

general_ai_model = GeneralAIModel(Config.OPENAI_API_KEY, Config.MODEL_NAME)