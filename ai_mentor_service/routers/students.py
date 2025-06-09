from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Student
from schemas import StudentCreate, StudentRead, StudentBase
from database import AsyncSessionLocal
from sqlalchemy.orm import selectinload

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=StudentBase)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

@router.get("/{telegram_id}", response_model=StudentRead)
async def read_student(telegram_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.mood_logs))
        .where(Student.telegram_id == telegram_id)
    )
    db_student = result.scalars().first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@router.patch("/{telegram_id}")
async def update_student(telegram_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.telegram_id == telegram_id))
    db_student = result.scalars().first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in data.items():
        setattr(db_student, key, value)
    await db.commit()
    return {"status": "ok"}