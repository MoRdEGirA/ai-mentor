from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Achievement, Student, StudentAchievement
from database import AsyncSessionLocal
from datetime import datetime

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

DEFAULT_ACHIEVEMENTS = [
    {
        "name": "Новичок",
        "description": "Вы зарегистрировались в системе. Добро пожаловать!",
        "icon": "🌱"
    },
    {
        "name": "Энтузиаст",
        "description": "Вы запросили дополнительное задание. Отличный настрой!",
        "icon": "🔥"
    },
    {
        "name": "3 дня подряд",
        "description": "Вы работали с ботом три дня подряд. Продолжайте в том же духе!",
        "icon": "📆"
    },
    {
        "name": "Марафонец",
        "description": "Вы выполнили 5 заданий за один день. Невероятно продуктивно!",
        "icon": "🏃‍♂️"
    },
    {
        "name": "Сильный духом",
        "description": "Вы прошли задание, даже находясь в состоянии усталости.",
        "icon": "🧘"
    },
    {
        "name": "Финишёр",
        "description": "Вы выполнили все задания по выбранной теме. Цель достигнута!",
        "icon": "🏁"
    },
    {
        "name": "Всё по плану",
        "description": "Вы завершили 7 заданий по расписанию. Отличная дисциплина!",
        "icon": "🗓️"
    },
    {
        "name": "Обратная связь",
        "description": "Вы получили первое сообщение с обратной связью от бота.",
        "icon": "💬"
    },
    {
        "name": "Настроение зафиксировано",
        "description": "Вы впервые прошли тест на эмоциональное состояние.",
        "icon": "📊"
    },
    {
        "name": "Прокачка",
        "description": "Вы повысили уровень сложности заданий. Настоящий рост!",
        "icon": "📈"
    },
    {
        "name": "Непрерывность",
        "description": "Вы не пропустили ни одного дня за неделю.",
        "icon": "🔁"
    },
    {
        "name": "Любопытный ум",
        "description": "Вы сменили тему обучения. Новые горизонты!",
        "icon": "🧠"
    },
    {
        "name": "Советник",
        "description": "Вы дали системе обратную связь о задании.",
        "icon": "📝"
    }
]

async def ensure_default_achievements(db: AsyncSession):
    for default in DEFAULT_ACHIEVEMENTS:
        result = await db.execute(select(Achievement).where(Achievement.name == default["name"]))
        if not result.scalars().first():
            db.add(Achievement(**default))
    await db.commit()

@router.get("/", response_model=list[dict])
async def get_all_achievements(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Achievement))
    return [
        {"id": a.id, "name": a.name, "description": a.description, "icon": a.icon}
        for a in result.scalars().all()
    ]

@router.get("/{achievement_id}", response_model=dict)
async def get_achievement(achievement_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalars().first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return {
        "id": achievement.id,
        "name": achievement.name,
        "description": achievement.description,
        "icon": achievement.icon
    }

from sqlalchemy.orm import selectinload

@router.get("/students/{telegram_id}/achievements", response_model=list[dict])
async def get_student_achievements(telegram_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.achievements).selectinload(StudentAchievement.achievement))
        .where(Student.telegram_id == telegram_id)
    )
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return [
        {
            "name": sa.achievement.name,
            "description": sa.achievement.description,
            "icon": sa.achievement.icon,
            "received_at": sa.received_at
        }
        for sa in student.achievements
    ]


@router.post("/assign")
async def assign_achievement(telegram_id: str, achievement_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = result.scalars().first()
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    existing = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id == student.id, StudentAchievement.achievement_id == achievement_id)
    )
    if existing.scalars().first():
        return {"status": "already assigned"}

    sa = StudentAchievement(student_id=student.id, achievement_id=achievement.id, received_at=datetime.utcnow())
    db.add(sa)
    await db.commit()
    return {"status": "assigned"}
