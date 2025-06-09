from fastapi import FastAPI
from database import init_db, AsyncSessionLocal
from routers import students, mood, assignments, achievements, motivation
from routers.achievements import ensure_default_achievements

app = FastAPI()

app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(mood.router, prefix="/mood_logs", tags=["Mood Logs"])
app.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
app.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
app.include_router(motivation.router, prefix="/motivation", tags=["Motivation"])

@app.on_event("startup")
async def on_startup():
    await init_db()
    async with AsyncSessionLocal() as db:
        await ensure_default_achievements(db)
