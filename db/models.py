"""
Database models using SQLAlchemy ORM.
Defines the core entities: Tasks, Events, and Notes.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    """
    Represents a task entity with title, description, priority, and status.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0)  # 0-low, 1-medium, 2-high, 3-urgent
    status = Column(String(50), default="pending", index=True)  # pending, in_progress, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


class Event(Base):
    """
    Represents a calendar event with start/end times and participants.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    participants = Column(JSON, nullable=True)  # List of participant email/names
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', start_time='{self.start_time}')>"


class Note(Base):
    """
    Represents a note with content, tags, and optional embeddings for semantic search.
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # List of tags for organization
    embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}')>"
