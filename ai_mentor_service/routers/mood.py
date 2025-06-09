from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import MoodLog
from schemas import MoodLogCreate, MoodLogRead
from database import AsyncSessionLocal

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=MoodLogRead)
async def create_mood_log(mood: MoodLogCreate, db: AsyncSession = Depends(get_db)):
    db_log = MoodLog(**mood.dict())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log
