from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    timestamp: str = str(datetime.now())
    language: str

class Chat(BaseModel):
    user_id: str
    language: str
    level: Optional[str]
    title: Optional[str]
    messages: List[Message] = []
    created_at: str = str(datetime.now())
    updated_at: str = str(datetime.now())
    is_active: bool = True