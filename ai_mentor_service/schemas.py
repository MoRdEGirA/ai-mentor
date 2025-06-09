from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MoodLogBase(BaseModel):
    score_stress: int
    score_anxiety: int
    score_positive: int
    score_energy: int
    comment: Optional[str] = None

class MoodLogCreate(MoodLogBase):
    student_id: int

class MoodLogRead(MoodLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class StudentBase(BaseModel):
    telegram_id: str
    name: Optional[str] = None
    motivation_type: Optional[str] = None
    mood_score: Optional[int] = 0
    eng_level: Optional[str] = None
    interest_topics: Optional[str] = None
    preferred_time: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int
    created_at: datetime
    last_active_at: datetime
    mood_logs: List[MoodLogRead] = []

    class Config:
        orm_mode = True


class ContentBase(BaseModel):
    topic: str
    level: str
    text: str
    content_type: str

class ContentRead(ContentBase):
    id: int

    class Config:
        orm_mode = True

class FeedbackRequest(BaseModel):
    telegram_id: str
    assignment_id: int
    answers: List[str]

class MotivationRequest(BaseModel):
    name: str
    mood: dict
    total_completed: int

class MotivationResponse(BaseModel):
    text: str
