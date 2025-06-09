

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Student, MoodLog, Assignment
from services.llm_feedback import generate_motivation
from database import get_db
from database import AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/")
async def get_motivation(telegram_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.execute(
        select(MoodLog).where(MoodLog.student_id == student.id).order_by(MoodLog.created_at.desc())
    )
    mood = result.scalars().first()
    mood_dict = {
        "score_stress": mood.score_stress if mood else None,
        "score_anxiety": mood.score_anxiety if mood else None,
        "score_positive": mood.score_positive if mood else None,
        "score_energy": mood.score_energy if mood else None
    }

    result = await db.execute(
        select(Assignment).where(Assignment.student_id == student.id, Assignment.status == "completed")
    )
    total_completed = len(result.scalars().all())

    motivation_text = generate_motivation(student.name or "студент", mood_dict, total_completed)

    return {"text": motivation_text}
