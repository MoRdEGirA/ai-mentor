from fastapi import APIRouter
from pydantic import BaseModel
from services.llm_feedback import generate_feedback_text

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    name: str
    mood: dict

class FeedbackResponse(BaseModel):
    text: str

@router.post("/", response_model=FeedbackResponse)
async def generate_feedback(data: FeedbackRequest):
    text = generate_feedback_text(data.name, data.mood)
    return {"text": text}
