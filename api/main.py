"""
FastAPI Application for GenAI Multi-Agent Orchestration System.

Exposes the multi-agent system via REST API with:
- POST /query - Execute user intent through orchestrator
- GET /tasks - List all tasks
- GET /events - List all events
- GET /notes - List all notes
- Health check and system status endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents import OrchestratorAgent, TaskAgent, CalendarAgent, NotesAgent
from db import init_database, DatabaseManager
from utils import Config
from tools import TaskTool, CalendarTool, NotesTool


# ==================== Request/Response Models ====================

class QueryRequest(BaseModel):
    """Request model for /query endpoint."""
    user_input: str = Field(..., min_length=1, max_length=500, description="User query")
    include_trace: bool = Field(False, description="Include execution trace in response")


class QueryResponse(BaseModel):
    """Response model for /query endpoint."""
    status: str
    workflow_id: str
    message: str
    intents: List[str]
    actions_count: int
    results_count: int
    actions: Optional[List] = None
    results: Optional[List] = None
    trace: Optional[dict] = None


class TaskModel(BaseModel):
    """Task data model."""
    title: str
    description: str
    priority: int
    due_date: Optional[datetime] = None
    status: str = "pending"


class EventModel(BaseModel):
    """Event data model."""
    title: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    participants: Optional[List[str]] = None


class NoteModel(BaseModel):
    """Note data model."""
    title: str
    content: str
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Task response model."""
    id: int
    title: str
    description: str
    priority: int
    status: str
    due_date: Optional[datetime]
    created_at: datetime


class EventResponse(BaseModel):
    """Event response model."""
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    participants: Optional[List[str]]
    created_at: datetime


class NoteResponse(BaseModel):
    """Note response model."""
    id: int
    title: str
    content: str
    tags: Optional[List[str]]
    created_at: datetime


class SystemStatus(BaseModel):
    """System status model."""
    status: str
    version: str
    agents: int
    database_loaded: bool
    uptime: datetime


# ==================== Dependency Injection ====================

def get_orchestrator() -> OrchestratorAgent:
    """
    Get orchestrator instance with registered agents.
    
    Returns:
        OrchestratorAgent: Configured orchestrator with all agents registered
    """
    orchestrator = OrchestratorAgent(max_memory=50)
    orchestrator.register_agent(TaskAgent())
    orchestrator.register_agent(CalendarAgent())
    orchestrator.register_agent(NotesAgent())
    return orchestrator


# ==================== FastAPI Application ====================

app = FastAPI(
    title="GenAI Multi-Agent Orchestration API",
    description="REST API for multi-agent task management system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for state management
_start_time: datetime = datetime.utcnow()
_initialized: bool = False


# ==================== Initialization ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database and system on startup."""
    global _initialized
    try:
        init_database(Config.get_database_url())
        _initialized = True
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# ==================== Health & Status Endpoints ====================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy" if _initialized else "initializing",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/status", tags=["System"], response_model=SystemStatus)
async def get_status():
    """
    Get complete system status.
    
    Returns:
        SystemStatus: Detailed system status information
    """
    uptime = datetime.utcnow() - _start_time
    return SystemStatus(
        status="active" if _initialized else "initializing",
        version="2.0.0",
        agents=3,  # Task, Calendar, Notes
        database_loaded=_initialized,
        uptime=uptime
    )


# ==================== Main Query Endpoint ====================

@app.post("/query", tags=["Query"], response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Execute user query through orchestrator.
    
    Detects intents, routes to appropriate agents, and executes workflow.
    
    Args:
        request: QueryRequest with user_input
        orchestrator: Injected orchestrator instance
        
    Returns:
        QueryResponse: Structured response with workflow results
        
    Raises:
        HTTPException: If query execution fails
    """
    try:
        # Handle user request
        response = orchestrator.handle_request(request.user_input)
        
        if not response.get("execution_plan"):
            raise HTTPException(
                status_code=400,
                detail="Could not generate execution plan for request"
            )
        
        # Execute workflow
        result = orchestrator.execute_plan(response["execution_plan"])
        
        # Prepare response
        query_response = QueryResponse(
            status=result["status"],
            workflow_id=result["workflow_id"],
            message=result["message"],
            intents=response["intents"],
            actions_count=len(result["actions"]),
            results_count=len(result["results"]),
            actions=result["actions"] if request.include_trace else None,
            results=result["results"] if request.include_trace else None,
            trace=orchestrator.get_execution_trace(result["workflow_id"])[-1:] 
                  if request.include_trace else None
        )
        
        return query_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


# ==================== Task Endpoints ====================

@app.get("/tasks", tags=["Tasks"], response_model=dict)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[int] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100, description="Result limit")
):
    """
    List all tasks with optional filtering.
    
    Args:
        status: Optional task status filter
        priority: Optional priority filter
        limit: Maximum results to return
        
    Returns:
        dict: Tasks list with metadata
    """
    try:
        result = TaskTool.list_tasks(
            status=status,
            priority=priority,
            limit=limit
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "count": result["count"],
            "data": result["data"],
            "filters": {
                "status": status,
                "priority": priority,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@app.get("/tasks/{task_id}", tags=["Tasks"], response_model=dict)
async def get_task(task_id: int):
    """
    Get specific task by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        dict: Task details
    """
    try:
        result = TaskTool.get_task(task_id)
        
        if result["status"] != "success":
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "status": "success",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


@app.post("/tasks", tags=["Tasks"], response_model=dict)
async def create_task(task: TaskModel):
    """
    Create new task.
    
    Args:
        task: Task data
        
    Returns:
        dict: Created task with ID
    """
    try:
        result = TaskTool.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "message": "Task created successfully",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks/overdue", tags=["Tasks"], response_model=dict)
async def get_overdue_tasks():
    """
    Get all overdue tasks.
    
    Returns:
        dict: List of overdue tasks
    """
    try:
        result = TaskTool.get_overdue_tasks()
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "count": result["count"],
            "data": result["data"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overdue tasks: {str(e)}")


# ==================== Event Endpoints ====================

@app.get("/events", tags=["Events"], response_model=dict)
async def list_events(
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Result limit")
):
    """
    List all events with optional date filtering.
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum results to return
        
    Returns:
        dict: Events list with metadata
    """
    try:
        result = CalendarTool.list_events(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "count": result["count"],
            "data": result["data"],
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")


@app.get("/events/{event_id}", tags=["Events"], response_model=dict)
async def get_event(event_id: int):
    """
    Get specific event by ID.
    
    Args:
        event_id: Event ID
        
    Returns:
        dict: Event details
    """
    try:
        result = CalendarTool.get_event(event_id)
        
        if result["status"] != "success":
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "status": "success",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")


@app.post("/events", tags=["Events"], response_model=dict)
async def create_event(event: EventModel):
    """
    Create new event.
    
    Args:
        event: Event data
        
    Returns:
        dict: Created event with ID
    """
    try:
        result = CalendarTool.schedule_event(
            title=event.title,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location or "",
            participants=event.participants or [],
            check_conflicts=True
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=409 if "conflict" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return {
            "status": "success",
            "message": "Event created successfully",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@app.get("/events/available", tags=["Events"], response_model=dict)
async def check_availability(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)")
):
    """
    Check availability in time slot.
    
    Args:
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        
    Returns:
        dict: Availability status and conflicts
    """
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        
        result = CalendarTool.check_availability(start, end)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "available": result.get("available", True),
            "conflicts": result.get("conflicts", []),
            "time_slot": {
                "start": start_time,
                "end": end_time
            }
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check availability: {str(e)}")


# ==================== Notes Endpoints ====================

@app.get("/notes", tags=["Notes"], response_model=dict)
async def list_notes(
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter"),
    limit: int = Query(50, ge=1, le=100, description="Result limit")
):
    """
    List all notes with optional tag filtering.
    
    Args:
        tags: Optional comma-separated tags to filter
        limit: Maximum results to return
        
    Returns:
        dict: Notes list with metadata
    """
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        
        result = NotesTool.list_notes(
            tags=tag_list,
            limit=limit
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "count": result["count"],
            "data": result["data"],
            "filters": {
                "tags": tag_list,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list notes: {str(e)}")


@app.get("/notes/{note_id}", tags=["Notes"], response_model=dict)
async def get_note(note_id: int):
    """
    Get specific note by ID.
    
    Args:
        note_id: Note ID
        
    Returns:
        dict: Note details
    """
    try:
        result = NotesTool.get_note(note_id)
        
        if result["status"] != "success":
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {
            "status": "success",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get note: {str(e)}")


@app.post("/notes", tags=["Notes"], response_model=dict)
async def create_note(note: NoteModel):
    """
    Create new note.
    
    Args:
        note: Note data
        
    Returns:
        dict: Created note with ID
    """
    try:
        result = NotesTool.create_note(
            title=note.title,
            content=note.content,
            tags=note.tags or []
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "message": "Note created successfully",
            "data": result["data"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")


@app.get("/notes/search", tags=["Notes"], response_model=dict)
async def search_notes(
    query: str = Query(..., min_length=1, description="Search query"),
    search_type: str = Query("keyword", regex="^(keyword|tag)$", description="Search type")
):
    """
    Search notes by keyword or tag.
    
    Args:
        query: Search query
        search_type: Search type (keyword or tag)
        
    Returns:
        dict: Matching notes
    """
    try:
        result = NotesTool.search_notes(
            query=query,
            search_type=search_type
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "count": result["count"],
            "data": result["data"],
            "query": query,
            "search_type": search_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search notes: {str(e)}")


# ==================== Orchestrator Endpoints ====================

@app.get("/orchestrator/memory", tags=["Orchestrator"], response_model=dict)
async def get_memory(
    limit: int = Query(10, ge=1, le=50, description="Number of recent interactions"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get orchestrator interaction memory.
    
    Args:
        limit: Maximum interactions to return
        orchestrator: Injected orchestrator instance
        
    Returns:
        dict: Recent interactions
    """
    try:
        memory = orchestrator.get_memory(limit=limit)
        return {
            "status": "success",
            "count": len(memory),
            "interactions": memory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")


@app.get("/orchestrator/trace/{workflow_id}", tags=["Orchestrator"], response_model=dict)
async def get_workflow_trace(
    workflow_id: str,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get execution trace for specific workflow.
    
    Args:
        workflow_id: Workflow ID
        orchestrator: Injected orchestrator instance
        
    Returns:
        dict: Workflow execution trace
    """
    try:
        traces = orchestrator.get_execution_trace()
        matching_trace = [t for t in traces if t["workflow_id"] == workflow_id]
        
        if not matching_trace:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "status": "success",
            "trace": matching_trace[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace: {str(e)}")


# ==================== Demo Workflows ====================

@app.post("/demo/workflows", tags=["Demo"], response_model=dict)
async def run_demo_workflow(
    case: int = Query(1, ge=1, le=4, description="Demo case number (1-4)"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Run demo workflows to showcase system capabilities.
    
    Demo Cases:
    - Case 1: "Schedule meeting tomorrow at 3 PM and create a task"
    - Case 2: "What are my tasks tomorrow?"
    - Case 3: "Store note about project AI"
    - Case 4: "Find notes about AI"
    
    Args:
        case: Demo case number (1-4)
        orchestrator: Injected orchestrator instance
        
    Returns:
        dict: Demo results
    """
    demos = {
        1: "Schedule meeting tomorrow at 3 PM and create a task",
        2: "What are my tasks tomorrow?",
        3: "Store note about project AI",
        4: "Find notes about AI"
    }
    
    if case not in demos:
        raise HTTPException(status_code=400, detail="Case must be 1-4")
    
    try:
        user_input = demos[case]
        
        # Handle request
        response = orchestrator.handle_request(user_input)
        
        if not response.get("execution_plan"):
            raise HTTPException(
                status_code=400,
                detail="Could not generate execution plan"
            )
        
        # Execute workflow
        result = orchestrator.execute_plan(response["execution_plan"])
        
        return {
            "status": "success",
            "demo_case": case,
            "user_input": user_input,
            "workflow_id": result["workflow_id"],
            "intents": response["intents"],
            "actions_count": len(result["actions"]),
            "results_count": len(result["results"]),
            "message": result["message"],
            "actions": result["actions"],
            "results": result["results"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo execution failed: {str(e)}")


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with custom format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with custom format."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": f"Internal server error: {str(exc)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting GenAI API Server...")
    print("📖 Documentation available at http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
