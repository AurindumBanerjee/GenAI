# GenAI API Documentation

## Overview

FastAPI-based REST API for the GenAI Multi-Agent Orchestration System. The API exposes all system capabilities via HTTP endpoints with automatic interactive documentation.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience command
python api/main.py
```

### 3. Access Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)

---

## Core Endpoints

### 1. Query Endpoint (POST /query)

Execute user intent through the multi-agent orchestrator.

**Request:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Schedule a meeting tomorrow at 3 PM and create a task",
    "include_trace": true
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "user_input": "Schedule meeting and create task",
        "include_trace": True
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Workflow ID: {result['workflow_id']}")
print(f"Message: {result['message']}")
print(f"Actions executed: {result['actions_count']}")
```

**Response:**
```json
{
  "status": "completed",
  "workflow_id": "WF-20240115143022-001",
  "message": "Workflow completed: 2 actions, 2 results",
  "intents": ["calendar", "task"],
  "actions_count": 2,
  "results_count": 2,
  "actions": [
    {
      "step": 1,
      "agent": "CalendarAgent",
      "intent": "calendar",
      "timestamp": "2024-01-15T14:30:22.234567"
    },
    {
      "step": 2,
      "agent": "TaskAgent",
      "intent": "task",
      "timestamp": "2024-01-15T14:30:23.345678"
    }
  ],
  "results": [
    {
      "step": 1,
      "status": "completed",
      "data": {
        "id": 1,
        "event_id": 101,
        "title": "Meeting"
      }
    },
    {
      "step": 2,
      "status": "completed",
      "data": {
        "id": 42,
        "task_id": 201,
        "title": "Follow-up task"
      }
    }
  ]
}
```

---

## Task Management Endpoints

### GET /tasks

List all tasks with optional filtering.

```bash
# List all tasks
curl "http://localhost:8000/tasks"

# Filter by status
curl "http://localhost:8000/tasks?status=pending"

# Filter by priority
curl "http://localhost:8000/tasks?priority=1&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "id": 1,
      "title": "Complete report",
      "description": "Q1 analysis",
      "priority": 1,
      "status": "completed",
      "due_date": "2024-02-15T23:59:59",
      "created_at": "2024-01-15T10:00:00"
    }
  ],
  "filters": {
    "status": null,
    "priority": null,
    "limit": 50
  }
}
```

### GET /tasks/{task_id}

Get specific task by ID.

```bash
curl "http://localhost:8000/tasks/1"
```

### POST /tasks

Create new task.

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement API",
    "description": "Build FastAPI server",
    "priority": 1,
    "due_date": "2024-02-28T23:59:59",
    "status": "pending"
  }'
```

### GET /tasks/overdue

Get all overdue tasks.

```bash
curl "http://localhost:8000/tasks/overdue"
```

---

## Event Management Endpoints

### GET /events

List all events with optional date filtering.

```bash
# List all events
curl "http://localhost:8000/events"

# Filter by date
curl "http://localhost:8000/events?start_date=2024-02-01&end_date=2024-02-28"
```

### GET /events/{event_id}

Get specific event by ID.

```bash
curl "http://localhost:8000/events/1"
```

### POST /events

Create new event with conflict detection.

```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2024-02-15T14:00:00",
    "end_time": "2024-02-15T15:00:00",
    "location": "Conference Room A",
    "participants": ["alice@example.com", "bob@example.com"]
  }'
```

### GET /events/available

Check availability in time slot.

```bash
curl "http://localhost:8000/events/available?start_time=2024-02-15T14:00:00&end_time=2024-02-15T15:00:00"
```

**Response:**
```json
{
  "status": "success",
  "available": true,
  "conflicts": [],
  "time_slot": {
    "start": "2024-02-15T14:00:00",
    "end": "2024-02-15T15:00:00"
  }
}
```

---

## Notes Management Endpoints

### GET /notes

List all notes with optional tag filtering.

```bash
# List all notes
curl "http://localhost:8000/notes"

# Filter by tags
curl "http://localhost:8000/notes?tags=important,urgent"
```

### GET /notes/{note_id}

Get specific note by ID.

```bash
curl "http://localhost:8000/notes/1"
```

### POST /notes

Create new note.

```bash
curl -X POST "http://localhost:8000/notes" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project AI Notes",
    "content": "Implementation strategy for AI module",
    "tags": ["ai", "project", "important"]
  }'
```

### GET /notes/search

Search notes by keyword or tag.

```bash
# Keyword search
curl "http://localhost:8000/notes/search?query=architecture&search_type=keyword"

# Tag search
curl "http://localhost:8000/notes/search?query=ai&search_type=tag"
```

---

## Orchestrator Endpoints

### GET /orchestrator/memory

Get orchestrator interaction memory.

```bash
curl "http://localhost:8000/orchestrator/memory?limit=10"
```

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "interactions": [
    {
      "workflow_id": "WF-20240115143022-001",
      "timestamp": "2024-01-15T14:30:22.123456",
      "user_input": "Schedule meeting and create task",
      "intents": ["calendar", "task"],
      "actions_count": 2,
      "results_count": 2
    }
  ]
}
```

### GET /orchestrator/trace/{workflow_id}

Get execution trace for specific workflow.

```bash
curl "http://localhost:8000/orchestrator/trace/WF-20240115143022-001"
```

---

## Demo Workflows

### POST /demo/workflows

Run predefined demo workflows.

**Case 1: Multi-step scheduling**
```bash
curl -X POST "http://localhost:8000/demo/workflows?case=1"
# "Schedule meeting tomorrow at 3 PM and create a task"
```

**Case 2: Query tasks**
```bash
curl -X POST "http://localhost:8000/demo/workflows?case=2"
# "What are my tasks tomorrow?"
```

**Case 3: Store note**
```bash
curl -X POST "http://localhost:8000/demo/workflows?case=3"
# "Store note about project AI"
```

**Case 4: Search notes**
```bash
curl -X POST "http://localhost:8000/demo/workflows?case=4"
# "Find notes about AI"
```

---

## System Status Endpoints

### GET /health

Quick health check.

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:22.123456"
}
```

### GET /status

Complete system status.

```bash
curl "http://localhost:8000/status"
```

**Response:**
```json
{
  "status": "active",
  "version": "2.0.0",
  "agents": 3,
  "database_loaded": true,
  "uptime": "0:15:30.123456"
}
```

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "status": "error",
  "error": "Descriptive error message",
  "timestamp": "2024-01-15T14:30:22.123456"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `409`: Conflict (e.g., event scheduling conflict)
- `500`: Internal server error

---

## Python API Client Example

```python
import requests
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8000"

class GenAIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    # Query endpoint
    def query(self, user_input: str, include_trace=False):
        response = requests.post(
            f"{self.base_url}/query",
            json={"user_input": user_input, "include_trace": include_trace}
        )
        return response.json()
    
    # Task endpoints
    def list_tasks(self, status=None, priority=None):
        response = requests.get(
            f"{self.base_url}/tasks",
            params={"status": status, "priority": priority}
        )
        return response.json()
    
    def create_task(self, title, description, priority=3, due_date=None):
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date
            }
        )
        return response.json()
    
    # Event endpoints
    def list_events(self, start_date=None, end_date=None):
        response = requests.get(
            f"{self.base_url}/events",
            params={"start_date": start_date, "end_date": end_date}
        )
        return response.json()
    
    def schedule_event(self, title, start_time, end_time, participants=None):
        response = requests.post(
            f"{self.base_url}/events",
            json={
                "title": title,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "participants": participants or []
            }
        )
        return response.json()
    
    def check_availability(self, start_time, end_time):
        response = requests.get(
            f"{self.base_url}/events/available",
            params={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        )
        return response.json()
    
    # Note endpoints
    def list_notes(self, tags=None):
        response = requests.get(
            f"{self.base_url}/notes",
            params={"tags": tags}
        )
        return response.json()
    
    def create_note(self, title, content, tags=None):
        response = requests.post(
            f"{self.base_url}/notes",
            json={
                "title": title,
                "content": content,
                "tags": tags or []
            }
        )
        return response.json()
    
    def search_notes(self, query, search_type="keyword"):
        response = requests.get(
            f"{self.base_url}/notes/search",
            params={"query": query, "search_type": search_type}
        )
        return response.json()

# Usage Example
client = GenAIClient()

# Schedule meeting and create task
result = client.query("Schedule meeting tomorrow at 3 PM and create a task")
print(f"Workflow ID: {result['workflow_id']}")
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")

# List tasks
tasks = client.list_tasks()
print(f"Total tasks: {tasks['count']}")

# Check availability
tomorrow = datetime.utcnow() + timedelta(days=1)
start = tomorrow.replace(hour=15, minute=0)
end = tomorrow.replace(hour=16, minute=0)

availability = client.check_availability(start, end)
print(f"Available: {availability['available']}")

# Create note
note = client.create_note(
    title="Project AI",
    content="Implementation strategy",
    tags=["ai", "project"]
)
print(f"Note created: {note['data']['id']}")
```

---

## Advanced Features

### Execution Tracing

Request execution trace to debug workflow execution:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Schedule meeting and create task",
    "include_trace": true
  }'
```

The response includes:
- `actions`: All executed actions with timestamps
- `results`: All collected results per step
- `trace`: Complete workflow execution audit trail

### Conflict Detection for Events

When scheduling events, conflicts are automatically detected:

```json
{
  "status": "error",
  "error": "Time slot conflicts with 1 existing event(s)",
  "timestamp": "2024-01-15T14:30:22.123456"
}
```

### Memory Management

The orchestrator maintains an interaction memory (configurable):

```bash
# Retrieve last 10 interactions
curl "http://localhost:8000/orchestrator/memory?limit=10"
```

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t genai-api .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data genai-api
```

### Environment Variables

Create `.env` file:
```
DATABASE_URL=sqlite:///./data/app.db
DEBUG=False
AGENT_LOG_LEVEL=INFO
```

### Production Server (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "api.main:app" --worker-class uvicorn.workers.UvicornWorker
```

---

## Performance Metrics

- Query execution: ~200-500ms (including multi-step workflows)
- Task creation: ~50ms
- Event scheduling (with conflict check): ~100ms
- Note search: ~30ms
- Database operations: ~10-50ms

---

## Support & Documentation

- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Project Documentation**: See [README.md](../README.md)

---

## Version

API Version: 2.0.0  
Last Updated: January 15, 2024
