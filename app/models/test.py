from pydantic import BaseModel
from typing import List

class LanguageTest(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    topic: str
    difficulty: str