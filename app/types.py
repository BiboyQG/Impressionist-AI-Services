from typing import List, Optional, Dict
from pydantic import BaseModel


class Message(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    sender_name: str  # Name of the person who sent the message
    timestamp: Optional[str] = None


class ConversationHistory(BaseModel):
    messages: List[Message]


class Profile(BaseModel):
    personality_traits: str
    communication_style: str


class GenerationDecision(BaseModel):
    should_reply: bool
    reason: str


class GenerationResponse(BaseModel):
    response: str
    should_reply: bool
    reason: Optional[str] = None
