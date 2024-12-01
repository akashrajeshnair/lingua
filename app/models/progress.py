# app/models/progress.py - New file
from pydantic import BaseModel
from datetime import datetime

class Progress(BaseModel):
    user_id: str
    language: str
    level: str
    xp_points: int = 0
    messages_sent: int = 0
    last_interaction: datetime = datetime.now()