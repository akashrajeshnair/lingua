from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    timestamp: datetime = datetime.now()
    language: str

class Chat(BaseModel):
    user_id: str
    language: str
    level: Optional[str]
    title: Optional[str]
    messages: List[Message] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    is_active: bool = True