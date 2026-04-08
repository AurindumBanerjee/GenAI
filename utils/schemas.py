"""
Pydantic schemas for request/response validation.
Defines data models for Tasks, Events, and Notes.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any


# ============================================================================
# Task Schemas
# ============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    priority: int = Field(default=0, ge=0, le=3, description="Priority level: 0=low, 1=medium, 2=high, 3=urgent")
    status: str = Field(default="pending", description="Task status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project report",
                "description": "Finish Q1 project report",
                "due_date": "2026-04-15T17:00:00",
                "priority": 2,
                "status": "pending"
            }
        }


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None


# ============================================================================
# Event Schemas
# ============================================================================

class EventCreate(BaseModel):
    """Schema for creating a new event."""
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    participants: Optional[List[str]] = Field(None, description="List of participant emails/names")
    location: Optional[str] = Field(None, description="Event location")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Team Standup",
                "description": "Daily team synchronization",
                "start_time": "2026-04-08T10:00:00",
                "end_time": "2026-04-08T10:30:00",
                "participants": ["alice@example.com", "bob@example.com"],
                "location": "Conference Room A"
            }
        }


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    participants: Optional[List[str]]
    location: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: Optional[List[str]] = None
    location: Optional[str] = None


# ============================================================================
# Note Schemas
# ============================================================================

class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: Optional[str] = Field(None, max_length=255, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    tags: Optional[List[str]] = Field(None, description="List of tags for organization")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI System Design",
                "content": "Multi-agent architecture with orchestrator pattern",
                "tags": ["ai", "architecture", "design"]
            }
        }


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: int
    title: Optional[str]
    content: str
    tags: Optional[List[str]]
    embedding: Optional[Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


# ============================================================================
# Generic Response Schemas
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response wrapper."""
    status: str = "success"
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Generic error response wrapper."""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
