# models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    name = Column(String)
    motivation_type = Column(String)
    mood_score = Column(Integer, default=0)
    eng_level = Column(String)
    interest_topics = Column(String)
    preferred_time = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow)

    assignments = relationship("Assignment", back_populates="student")
    mood_logs = relationship("MoodLog", back_populates="student")
    achievements = relationship("StudentAchievement", back_populates="student")
    motivational_messages = relationship("MotivationalMessage", back_populates="student")
    responses = relationship("AssignmentResponse", back_populates="student")


class MoodLog(Base):
    __tablename__ = 'mood_logs'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    score_stress = Column(Integer)
    score_anxiety = Column(Integer)
    score_positive = Column(Integer)
    score_energy = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="mood_logs")


class Content(Base):
    __tablename__ = 'content'

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    subtopic = Column(String, nullable=True)    
    level = Column(String)
    text = Column(Text)
    content_type = Column(String)   
    source = Column(String, default="manual")   
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assignments = relationship("Assignment", back_populates="content")


class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    status = Column(String, default="pending")  
    presentation_mode = Column(String, default="normal")
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="assignments")
    content = relationship("Content", back_populates="assignments")
    responses = relationship("AssignmentResponse", back_populates="assignment")


class AssignmentResponse(Base):
    __tablename__ = 'assignment_responses'

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    answers = Column(JSON)
    feedback = Column(Text)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

    assignment = relationship("Assignment", back_populates="responses")
    student = relationship("Student", back_populates="responses")


class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    icon = Column(String)

    student_achievements = relationship("StudentAchievement", back_populates="achievement")


class StudentAchievement(Base):
    __tablename__ = 'student_achievements'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    received_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="student_achievements")


class MotivationalMessage(Base):
    __tablename__ = 'motivational_messages'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    text = Column(Text)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="motivational_messages")
