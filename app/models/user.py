from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    firebase_uid: str
    email: EmailStr
    username: str
    languages: List[str] = []
    created_at: datetime = datetime.now()
    last_login: Optional[datetime] = None
    is_active: bool = True