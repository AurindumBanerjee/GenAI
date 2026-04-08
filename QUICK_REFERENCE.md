"""
QUICK_REFERENCE.md - Developer Quick Reference Guide

Fast lookup for common tasks and patterns in the multi-agent system.
"""

# Quick Reference Guide

## File Locations

| Component | File | Purpose |
|-----------|------|---------|
| Base Agent | `agents/base_agent.py` | Abstract agent framework |
| Orchestrator | `agents/orchestrator.py` | Main coordinator |
| Task Agent | `agents/task_agent.py` | Task operations |
| Calendar Agent | `agents/calendar_agent.py` | Event operations |
| Notes Agent | `agents/notes_agent.py` | Note operations |
| Database Setup | `db/database.py` | Connection management |
| Data Models | `db/models.py` | SQLAlchemy models |
| Validation | `utils/schemas.py` | Pydantic schemas |
| Settings | `utils/config.py` | Configuration |
| Entry Point | `main.py` | Application entry point |

## Common Tasks

### Initialize System

```python
from agents import OrchestratorAgent, TaskAgent, CalendarAgent, NotesAgent
from db import init_database
from utils import Config

init_database(Config.get_database_url())
orchestrator = OrchestratorAgent()
orchestrator.register_agent(TaskAgent())
orchestrator.register_agent(CalendarAgent())
orchestrator.register_agent(NotesAgent())
```

### Create New Agent

```python
from agents.base_agent import BaseAgent, AgentRole

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            role=AgentRole.OBSERVER,
            description="My agent description"
        )
    
    def handle_request(self, user_input, context=None):
        self.set_status(AgentStatus.PROCESSING)
        try:
            # Your implementation here
            response = {"status": "success"}
            self.set_status(AgentStatus.COMPLETED)
            self.log_execution(user_input, response)
            return response
        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            self.set_status(AgentStatus.FAILED)
            self.log_execution(user_input, error_response, success=False)
            return error_response
```

### Register New Agent

```python
new_agent = MyAgent()
orchestrator.register_agent(new_agent)
```

### Process User Request

```python
user_request = "Your request here"
response = orchestrator.handle_request(user_request)

if response.get("execution_plan"):
    result = orchestrator.execute_plan(response["execution_plan"])
```

### Get Agent Status

```python
agent = task_agent
info = agent.get_agent_info()
print(f"Status: {info['status']}")
print(f"Tools: {info['tools_count']}")
print(f"Executions: {info['execution_count']}")
```

### Access Execution History

```python
history = agent.get_execution_history(limit=5)
for entry in history:
    print(f"{entry['timestamp']}: {entry['request']}")
```

## Intent Detection Keywords

| Intent | Keywords | Agent |
|--------|----------|-------|
| task | task, todo, create, complete, deadline, priority | TaskAgent |
| calendar | event, meeting, schedule, appointment, conflict | CalendarAgent |
| note | note, remember, save, document, write, search | NotesAgent |

## Agent Status Flow

```
IDLE → PROCESSING → COMPLETED → IDLE
              └→ WAITING
              └→ FAILED → IDLE
```

## Key Enums

### AgentRole
- `ORCHESTRATOR` - Main coordinator
- `TASK_MANAGER` - Task operations
- `CALENDAR_MANAGER` - Event operations
- `NOTE_MANAGER` - Note operations
- `OBSERVER` - Custom observers

### AgentStatus
- `IDLE` - Not processing
- `PROCESSING` - Currently executing
- `WAITING` - Waiting for external resource
- `COMPLETED` - Successfully completed
- `FAILED` - Execution failed

## Database Models - Field Reference

### Task
```python
Task.id: int (PK)
Task.title: str (required)
Task.description: str (optional)
Task.due_date: datetime (optional)
Task.priority: int (0-3)  # 0=low, 1=medium, 2=high, 3=urgent
Task.status: str  # pending, in_progress, completed, cancelled
Task.created_at: datetime
Task.updated_at: datetime
```

### Event
```python
Event.id: int (PK)
Event.title: str (required)
Event.description: str (optional)
Event.start_time: datetime (required)
Event.end_time: datetime (required)
Event.participants: list[str] (JSON)
Event.location: str (optional)
Event.created_at: datetime
Event.updated_at: datetime
```

### Note
```python
Note.id: int (PK)
Note.title: str (optional)
Note.content: str (required)
Note.tags: list[str] (JSON)
Note.embedding: any (JSON, optional)
Note.created_at: datetime
Note.updated_at: datetime
```

## Configuration Variables

```python
from utils import Config

Config.APP_NAME              # "Multi-Agent System"
Config.APP_VERSION           # "0.1.0"
Config.DEBUG                 # True/False
Config.DATABASE_URL          # SQLite path
Config.DEFAULT_TIMEOUT       # 30 seconds
Config.MAX_RETRIES           # 3
Config.MAX_PARALLEL_AGENTS   # 5
Config.WORKFLOW_MAX_STEPS    # 10
```

## Common Patterns

### Using Context Manager for DB

```python
from db import get_db_manager

db = get_db_manager()
with db.session_scope() as session:
    # Use session here
    # Auto-commits on success
    # Auto-rollbacks on error
    pass
```

### Creating Pydantic Response

```python
from utils.schemas import TaskResponse

task_data = {
    "id": 1,
    "title": "My Task",
    "description": "Description",
    "due_date": datetime.utcnow(),
    "priority": 2,
    "status": "pending",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

response = TaskResponse(**task_data)
print(response.model_dump())  # Serialize to dict
print(response.model_dump_json())  # JSON string
```

### Adding Tool to Agent

```python
from agents.base_agent import BaseTool

tool = BaseTool(
    name="my_tool",
    description="Does something useful",
    parameters=["param1", "param2"]
)

agent.add_tool(tool)

# List all tools
tools = agent.get_tools()
for t in tools:
    print(f"{t.name}: {t.description}")
```

## Debugging Tips

### Enable Debug Logging

```python
import os
os.environ['DEBUG'] = 'True'
from utils import Config
print(Config.DEBUG)  # True
```

### Print Agent Info

```python
agent = task_agent
print(agent)  # Shows __repr__
print(agent.get_agent_info())  # Full metadata
```

### Trace Execution

```python
# All executions are logged
history = agent.get_execution_history()
for entry in history:
    print(f"Success: {entry['success']}")
    print(f"Request: {entry['request']}")
    print(f"Response: {entry['response']}")
```

### Check Orchestrator Routing

```python
intent = orchestrator._detect_intent("Create a task")
print(intent)  # "task"

agents = orchestrator._route_request(intent)
print(agents)  # ["TaskAgent"]
```

## Performance Tips

1. **Reuse Orchestrator Instance** - Don't recreate
2. **Register Agents Once** - At startup
3. **Batch Similar Requests** - Reduces orchestration overhead
4. **Use Context Managers** - For automatic resource cleanup
5. **Monitor Execution History** - Keep it trimmed

## Testing Checklist

- [ ] Can initialize database
- [ ] Can create and register agents
- [ ] Can process user requests
- [ ] Can detect intents correctly
- [ ] Can route to correct agents
- [ ] Can execute plans
- [ ] Can access agent history
- [ ] Can get agent info
- [ ] Can handle errors gracefully
- [ ] Can add/remove tools

## Useful Commands

```bash
# Show help
python main.py --help

# Run demos
python main.py --demo requests
python main.py --demo methods
python main.py --demo info

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

## Module Imports

```python
# Agents
from agents import (
    BaseAgent,
    AgentRole,
    AgentStatus,
    OrchestratorAgent,
    TaskAgent,
    CalendarAgent,
    NotesAgent
)

# Database
from db import (
    Task,
    Event,
    Note,
    DatabaseManager,
    get_db_manager,
    init_database
)

# Utils
from utils import (
    Config,
    TaskCreate,
    TaskResponse,
    EventCreate,
    EventResponse,
    NoteCreate,
    NoteResponse
)
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2024-01-15
