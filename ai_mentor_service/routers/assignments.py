from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Student, Content, Assignment, MoodLog
from services.llm_generator import generate_assignment_content
import datetime
from services.llm_feedback import generate_feedback_text
from schemas import FeedbackRequest
import json
router = APIRouter(tags=["Assignments"])

@router.post("/generate")
async def generate_assignment(telegram_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    student = result.scalars().first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    topic = student.interest_topics or "tenses"
    level = student.eng_level or "A2"

    existing = await db.execute(
        select(Assignment).where(
            Assignment.student_id == student.id,
            Assignment.status == "pending"
        )
    )
    if existing.scalars().all():
        return {"status": "already_exists"}

    mood_query = await db.execute(
        select(MoodLog).where(MoodLog.student_id == student.id).order_by(MoodLog.created_at.desc())
    )
    mood = mood_query.scalars().first()

    presentation_mode = "normal"
    if mood:
        if mood.score_stress >= 7 or mood.score_anxiety >= 7 or mood.score_energy <= 3:
            presentation_mode = "light"
        elif mood.score_positive >= 7 and mood.score_energy >= 7:
            presentation_mode = "challenge"

    generated = generate_assignment_content(topic=topic, level=level)
    if not generated or not generated.get("exercise"):
        raise HTTPException(status_code=500, detail="Generation failed")

    content = Content(
        topic=generated["topic"],
        subtopic=generated.get("subtopic"),
        level=generated["level"],
        text=json.dumps({
            "theory": generated["theory"],
            "exercise": generated["exercise"],
            "questions": generated["questions"]
        }),
        content_type="generated",
        source="llm"
    )
    db.add(content)
    await db.flush()

    assignment = Assignment(
        student_id=student.id,
        content_id=content.id,
        status="pending",
        assigned_at=datetime.datetime.utcnow(),
        presentation_mode=presentation_mode
    )
    db.add(assignment)
    await db.commit()

    return {"status": "created", "assignment_id": assignment.id, "presentation_mode": presentation_mode}

@router.get("/by_student/{student_id}")
async def get_assignments_by_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Assignment).where(Assignment.student_id == student_id).order_by(Assignment.assigned_at.desc())
    )
    assignments = result.scalars().all()
    return [
        {
            "id": a.id,
            "status": a.status,
            "presentation_mode": a.presentation_mode
        }
        for a in assignments
    ]

@router.get("/{assignment_id}")
async def get_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    content_result = await db.execute(select(Content).where(Content.id == assignment.content_id))
    content = content_result.scalars().first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        content_data = json.loads(content.text)
    except Exception:
        content_data = {"text": content.text}

    return {
        "id": assignment.id,
        "status": assignment.status,
        "presentation_mode": assignment.presentation_mode,
        "content": content_data
    }

@router.patch("/{assignment_id}/complete")
async def complete_assignment(assignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalars().first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = "completed"
    assignment.completed_at = datetime.datetime.utcnow()
    await db.commit()
    return {"status": "completed"}

@router.post("/feedback")
async def get_feedback(request: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    telegram_id = request.telegram_id
    assignment_id = request.assignment_id
    answers = request.answers
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Получаем задание
    result = await db.execute(select(Assignment).where(Assignment.id == assignment_id))
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Получаем контент
    result = await db.execute(select(Content).where(Content.id == assignment.content_id))
    content = result.scalars().first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Получаем настроение
    result = await db.execute(
        select(MoodLog).where(MoodLog.student_id == student.id).order_by(MoodLog.created_at.desc())
    )
    mood = result.scalars().first()

    feedback_text = await generate_feedback_text(
        answers=answers,
        student_name=student.name or "студент",
        level=student.eng_level or "A2",
        presentation_mode=assignment.presentation_mode,
        mood=mood
    )

    return {"feedback": feedback_text}
