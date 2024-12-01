from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TestQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    topic: str
    difficulty: str

class LanguageTest(BaseModel):
    user_id: str
    chat_id: str
    questions: List[TestQuestion]
    language: str
    level: str
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    results: Optional[dict] = None