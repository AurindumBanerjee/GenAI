# 🤖 Multi-Agent System Using Google ADK

A modular, extensible multi-agent architecture built with Python. This system coordinates multiple specialized agents (Task Manager, Calendar Manager, Notes Manager) through a central Orchestrator agent, following Google ADK patterns for scalability and maintainability.

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────┐
│           User Request                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Orchestrator Agent   │
        │ - Intent Detection   │
        │ - Route to Agents    │
        │ - Workflow Manager   │
        └──────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌──────────┐ ┌─────────┐
   │ Task    │ │ Calendar │ │ Notes   │
   │ Agent   │ │ Agent    │ │ Agent   │
   └─────────┘ └──────────┘ └─────────┘
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  SQLite Database     │
        │  - Tasks Table       │
        │  - Events Table      │
        │  - Notes Table       │
        └──────────────────────┘
```

## 📁 Project Structure

```
GenAI/
├── agents/                     # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base class
│   ├── orchestrator.py        # Main orchestrator
│   ├── task_agent.py          # Task management
│   ├── calendar_agent.py      # Calendar/events
│   └── notes_agent.py         # Notes management
├── db/                        # Database layer
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy ORM models
│   └── database.py            # Connection management
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── config.py              # Configuration
│   └── schemas.py             # Pydantic schemas
├── main.py                    # Entry point & demos
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
# 1. Navigate to project directory
cd GenAI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run initialization and demo
python main.py --demo info
```

## 🚀 Quick Start

### Basic Usage

```python
from agents import OrchestratorAgent, TaskAgent, CalendarAgent, NotesAgent
from db import init_database
from utils import Config

# Initialize database
init_database(Config.get_database_url())

# Create agents
orchestrator = OrchestratorAgent()
task_agent = TaskAgent()
calendar_agent = CalendarAgent()
notes_agent = NotesAgent()

# Register specialized agents
orchestrator.register_agent(task_agent)
orchestrator.register_agent(calendar_agent)
orchestrator.register_agent(notes_agent)

# Process user request
request = "Create a task to finish the report by Friday"
response = orchestrator.handle_request(request)

# Execute the generated plan
if response.get("execution_plan"):
    result = orchestrator.execute_plan(response["execution_plan"])
```

### Running Demos

```bash
# 1. Demo: Request Routing & Orchestration
python main.py --demo requests

# 2. Demo: Individual Agent Methods
python main.py --demo methods

# 3. Demo: System Information
python main.py --demo info
```

## 📋 Core Components

### 1. BaseAgent (`agents/base_agent.py`)

Abstract base class providing:
- Common interface for all agents
- Status tracking (IDLE, PROCESSING, COMPLETED, FAILED)
- Tool management
- Execution history logging

```python
class BaseAgent(ABC):
    def __init__(self, name, role, description, tools=None)
    @abstractmethod
    def handle_request(self, user_input, context=None)
    def add_tool(self, tool)
    def log_execution(self, request, response, success=True)
```

### 2. OrchestratorAgent (`agents/orchestrator.py`)

Main orchestrator that:
- **Intent Detection**: Analyzes user input to determine intent
- **Agent Routing**: Routes requests to appropriate specialized agents
- **Workflow Management**: Builds and executes multi-step workflows
- **Agent Registration**: Manages all registered agents
- **Execution History**: Tracks all operations

```python
orchestrator = OrchestratorAgent()
orchestrator.register_agent(task_agent)

response = orchestrator.handle_request("Create a task...")
plan = response["execution_plan"]
result = orchestrator.execute_plan(plan)
```

### 3. Specialized Agents

#### TaskAgent
```python
task_agent.create_task(title, description, due_date, priority, status)
task_agent.get_tasks(task_id, status, priority, limit)
task_agent.update_task(task_id, updates)
task_agent.get_overdue_tasks()
```

#### CalendarAgent
```python
calendar_agent.schedule_event(title, start_time, end_time, participants)
calendar_agent.check_conflicts(start_time, end_time, participant)
calendar_agent.get_available_slots(date, duration_minutes)
calendar_agent.add_participant(event_id, email)
```

#### NotesAgent
```python
notes_agent.create_note(content, title, tags)
notes_agent.search_notes(query, search_type, tags)
notes_agent.get_notes_by_tag(tag)
notes_agent.add_tag(note_id, tag)
```

### 4. Database Models (`db/models.py`)

#### Task
Fields: id, title, description, due_date, priority, status, created_at, updated_at

#### Event
Fields: id, title, description, start_time, end_time, participants, location, created_at, updated_at

#### Note
Fields: id, title, content, tags, embedding, created_at, updated_at

### 5. Schemas (`utils/schemas.py`)

Pydantic models for validation:
- `TaskCreate` / `TaskResponse` / `TaskUpdate`
- `EventCreate` / `EventResponse` / `EventUpdate`
- `NoteCreate` / `NoteResponse` / `NoteUpdate`

## 🔄 Request Flow

1. **User Input** → Orchestrator
2. **Intent Detection** → Classify intent (task/calendar/note)
3. **Agent Routing** → Select target agent(s)
4. **Execution Plan** → Generate workflow steps
5. **Tool Execution** → (Future) Execute agent methods with actual DB/API calls
6. **Result Aggregation** → Combine results from agents
7. **Response** → Return to user

## 📊 Intent Detection

The orchestrator automatically detects user intent:

| Intent | Keywords | Agent |
|--------|----------|-------|
| task | task, todo, create, complete, deadline | TaskAgent |
| calendar | event, meeting, schedule, appointment | CalendarAgent |
| note | note, remember, save, document, search | NotesAgent |
| unknown | (unmatched) | None |

## 🗄️ Database

### SQLite (Default)
- File-based: `data/app.db`
- Automatically created on first run
- Perfect for development and testing

### Configuration
```python
# Via environment variable
DATABASE_URL=sqlite:///./data/app.db

# Via Config class
from utils import Config
Config.get_database_url()
```

## 🛠️ Configuration

### Environment Variables (`.env`)
```
DATABASE_URL=sqlite:///./data/app.db
DEBUG=True
AGENT_LOG_LEVEL=INFO
ENABLE_CALENDAR_SYNC=False
ENABLE_SEMANTIC_SEARCH=False
```

### Programmatic Access
```python
from utils import Config

Config.APP_NAME           # Application name
Config.DEBUG              # Debug mode
Config.DEFAULT_TIMEOUT    # Agent timeout
Config.DATABASE_URL       # Database URL
```

## 📈 Agent Status Lifecycle

```
IDLE ──┐
       │
       ▼
    PROCESSING
       │
       ├─→ COMPLETED ──┐
       │               │
       ├─→ FAILED      │
       │               │
       ▼               │
    WAITING ◄──────────┘
       │
       ▼
     IDLE
```

## 🔍 Execution History

All agents maintain execution history:

```python
# Access execution history
history = agent.get_execution_history(limit=10)

# Each entry contains:
{
    "timestamp": "2024-01-15T10:30:00",
    "request": "user input",
    "response": {response data},
    "success": True,
    "status": "completed"
}
```

## 📝 Key Design Patterns

1. **Abstract Base Class** - Common interface via `BaseAgent`
2. **Strategy Pattern** - Different agents implement different strategies
3. **Orchestrator Pattern** - Central coordination of specialized agents
4. **Factory Pattern** - Database initialization and agent creation
5. **Singleton Pattern** - Global database manager instance
6. **Context Manager Pattern** - Safe database session handling

## 🎓 Example: Complete Workflow

```python
from agents import OrchestratorAgent, TaskAgent, CalendarAgent, NotesAgent
from db import init_database
from utils import Config
from datetime import datetime, timedelta

# 1. Initialize system
init_database()
orchestrator = OrchestratorAgent()

# 2. Create and register agents
task_agent = TaskAgent()
calendar_agent = CalendarAgent()
notes_agent = NotesAgent()

orchestrator.register_agent(task_agent)
orchestrator.register_agent(calendar_agent)
orchestrator.register_agent(notes_agent)

# 3. Process various requests
requests = [
    "Create a task to review the budget",
    "Schedule a meeting with finance team next Tuesday at 2 PM",
    "Save notes about Q1 planning"
]

for req in requests:
    response = orchestrator.handle_request(req)
    plan = response["execution_plan"]
    result = orchestrator.execute_plan(plan)
    print(f"Request: {req}")
    print(f"Status: {result['overall_status']}\n")

# 4. View system status
status = orchestrator.get_orchestrator_status()
print(f"Total Agents: {status['total_registered']}")
print(f"Registered: {status['registered_agents']}")
```

## 🔮 Future Enhancements (Next Steps)

### Phase 2: Tool Integration
- [ ] Implement actual database operations
- [ ] Google Calendar API integration
- [ ] Gmail integration
- [ ] Real-time synchronization

### Phase 3: Intelligence
- [ ] Enhanced NLP for intent detection
- [ ] Entity extraction
- [ ] Semantic search with embeddings
- [ ] Learning from execution history

### Phase 4: API & UI
- [ ] FastAPI REST endpoints
- [ ] WebSocket support
- [ ] Web dashboard
- [ ] Authentication/Authorization

### Phase 5: Advanced Features
- [ ] Multi-agent collaboration
- [ ] Conflict resolution
- [ ] Workflow automation
- [ ] Self-learning capabilities

## 📚 Documentation

Comprehensive docstrings provided for:
- All classes and methods
- Function parameters and return types
- Usage examples
- Agent responsibilities and capabilities

## 🧪 Testing

```bash
# Run system demos (included)
python main.py --demo requests    # Test request routing
python main.py --demo methods     # Test agent methods
python main.py --demo info        # Display system info
```

## 🔧 Development

### Adding a New Agent

1. Create `new_agent.py` in `/agents`
2. Inherit from `BaseAgent`
3. Implement `handle_request()` method
4. Add to orchestrator routing logic
5. Register with orchestrator

### Adding a New Data Entity

1. Define `SQLAlchemy` model in `db/models.py`
2. Create `Pydantic` schemas in `utils/schemas.py`
3. Create corresponding agent in `agents/`
4. Update orchestrator intent detection

## 📄 License

MIT License

## 👤 Author

AI Systems Engineer

---

**Status**: ✅ Foundational Architecture Complete
**Next**: Tool Integration & Database Operations
