"""
ARCHITECTURE.md - Detailed Architecture Documentation

This document provides in-depth information about the system architecture,
design patterns, and component interactions.
"""

# Multi-Agent System Architecture

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Design](#component-design)
3. [Data Flow](#data-flow)
4. [Design Patterns](#design-patterns)
5. [Extensibility](#extensibility)
6. [Performance Considerations](#performance-considerations)

## System Architecture

### High-Level Overview

```
User Interface Layer
        │
        ▼
┌─────────────────────────────┐
│  Orchestrator Agent Layer   │
│  - Request Parsing          │
│  - Intent Detection         │
│  - Agent Routing            │
│  - Workflow Orchestration   │
└─────────────────────────────┘
        │
        ├─────────┬──────────┬─────────┐
        │         │          │         │
        ▼         ▼          ▼         ▼
    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
    │Task  │ │Event │ │Notes │ │ ...  │
    │Agent │ │Agent │ │Agent │ │Agent │
    └──────┘ └──────┘ └──────┘ └──────┘
        │         │          │
        └─────────┴──────────┴────────┐
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Database Layer  │
                            │  (SQLAlchemy)    │
                            └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  SQLite / SQL    │
                            └──────────────────┘
```

### Component Hierarchy

**Tier 1: Entry Point**
- `main.py` - Application entry point with demo runners

**Tier 2: Orchestration**
- `agents/orchestrator.py` - Central request coordinator

**Tier 3: Specialized Agents**
- `agents/task_agent.py` - Task operations
- `agents/calendar_agent.py` - Calendar/event operations
- `agents/notes_agent.py` - Note operations

**Tier 4: Supporting Infrastructure**
- `agents/base_agent.py` - Abstract base class
- `db/` - Database layer (models, connection management)
- `utils/` - Utilities (schemas, config)

## Component Design

### 1. BaseAgent (Abstract)

```python
class BaseAgent(ABC):
    """
    Abstract base providing:
    - Consistent interface across all agents
    - Status tracking and lifecycle management
    - Tool registration and management
    - Execution history and audit trail
    - Error handling framework
    """
    
    properties:
    - name: str                          # Unique agent identifier
    - role: AgentRole                    # Enum: orchestrator, task_manager, etc.
    - status: AgentStatus                # Current execution status
    - tools: List[BaseTool]              # Available tools
    - execution_history: List[Dict]      # Audit trail
    
    methods:
    - handle_request()                   # PRIMARY: Process requests
    - add_tool() / remove_tool()         # Manage tools
    - set_status()                       # Update status
    - log_execution()                    # Record operations
    - get_agent_info()                   # Metadata retrieval
```

### 2. OrchestratorAgent

```python
class OrchestratorAgent(BaseAgent):
    """
    Brain of the system:
    - Analyzes user input for intent
    - Routes to appropriate agents
    - Builds execution plans
    - Manages agent coordination
    - Tracks workflow state
    """
    
    key_methods:
    - handle_request(user_input)         # Parse and route
    - _detect_intent()                   # Classify intent
    - _route_request()                   # Select agents
    - _build_execution_plan()            # Create workflow
    - execute_plan()                     # Execute workflow
    - register_agent()                   # Add specialized agents
```

### 3. Specialized Agents

Each specialized agent inherits from `BaseAgent` and focuses on a specific domain:

#### TaskAgent
```python
create_task(title, description, due_date, priority, status)
get_tasks(task_id, status, priority, limit)
update_task(task_id, updates)
get_tasks_by_priority(priority)
get_overdue_tasks()
```

#### CalendarAgent
```python
schedule_event(title, start_time, end_time, participants, location)
check_conflicts(start_time, end_time, participant)
get_event(event_id)
get_events(start_date, end_date, participant)
get_available_slots(date, duration)
add_participant(event_id, participant)
```

#### NotesAgent
```python
create_note(content, title, tags)
search_notes(query, search_type, tags)
get_note(note_id)
get_notes(tags, date_range)
add_tag(note_id, tag)
remove_tag(note_id, tag)
get_notes_by_tag(tag)
```

## Data Flow

### Request Processing Flow

```
User Input
    │
    ▼
OrchestratorAgent.handle_request()
    │
    ├─→ _detect_intent()
    │   └─→ Classify (task/calendar/note/unknown)
    │
    ├─→ _route_request()
    │   └─→ Select agent(s) based on intent
    │
    ├─→ _build_execution_plan()
    │   ├─→ Create workflow ID
    │   ├─→ Generate execution steps
    │   └─→ Return plan with steps
    │
    └─→ execute_plan(plan)
        ├─→ For each step:
        │   ├─→ Get agent from registry
        │   ├─→ Execute agent method (placeholder)
        │   └─→ Collect result
        │
        └─→ Return aggregated results

Results returned to user
```

### Execution Plan Structure

```python
{
    "workflow_id": "WF-20240115103000-001",
    "intent": "task",
    "user_input": "Create a task...",
    "steps": [
        {
            "step_number": 1,
            "agent": "TaskAgent",
            "action": "Process task request",
            "depends_on": None,
            "status": "pending"
        }
    ]
}
```

## Design Patterns

### 1. Abstract Base Class Pattern
- Base `BaseAgent` defines common interface
- All agents inherit from `BaseAgent`
- Ensures consistent behavior across agents

### 2. Strategy Pattern
- Each agent implements different strategy for handling requests
- Strategies encapsulated in agent classes
- Easy to add new strategies (new agents)

### 3. Orchestrator Pattern
- Central `OrchestratorAgent` coordinates specialized agents
- Decouples request routing from implementation
- Enables complex workflows

### 4. Factory Pattern
- `DatabaseManager` creates and manages connections
- `get_db_manager()` provides singleton access
- `Config` class manages application settings

### 5. Singleton Pattern
- Global database manager instance
- Ensures single connection pool
- Context managers for session safety

### 6. Context Manager Pattern
- `with db.session_scope():` for automatic cleanup
- Ensures proper resource management
- Automatic rollback on errors

### 7. Registry Pattern
- `orchestrator.registered_agents` acts as registry
- Enables dynamic agent discovery
- Supports hot-swapping agents

## Extensibility

### Adding a New Agent Type

1. **Create Agent Class**
```python
# agents/weather_agent.py
from agents.base_agent import BaseAgent, AgentRole

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            role=AgentRole.OBSERVER,
            description="Provides weather information"
        )
    
    def handle_request(self, user_input, context=None):
        # Implementation here
        pass
```

2. **Update Orchestrator Routing**
```python
# In orchestrator.py _detect_intent()
if any(kw in user_lower for kw in ["weather", "temperature", "forecast"]):
    return "weather"

# In _route_request()
routing = {
    ...
    "weather": ["WeatherAgent"],
}
```

3. **Register with Orchestrator**
```python
orchestrator = OrchestratorAgent()
orchestrator.register_agent(WeatherAgent())
```

### Adding a New Data Entity

1. **Create Model**
```python
# db/models.py
class Document(Base):
    __tablename__ = "documents"
    # Define fields
```

2. **Create Schemas**
```python
# utils/schemas.py
class DocumentCreate(BaseModel):
    # Define fields

class DocumentResponse(BaseModel):
    # Define fields
```

3. **Create Agent**
```python
# agents/document_agent.py
class DocumentAgent(BaseAgent):
    # Implement methods
```

## Performance Considerations

### Database
- **Connection Pooling**: SQLAlchemy manages connection pool
- **Lazy Loading**: ORM relationships are lazy-loaded by default
- **Query Optimization**: Use indexed fields (title, status, start_time)

### Caching
- Execution history stored in memory
- Can be optimized with Redis for distributed systems
- Agent metadata cached for quick lookups

### Concurrency
- Current implementation: Sequential agent execution
- Future: Parallel agent execution with `asyncio`
- Thread-safe database sessions

### Scalability
- Stateless agents enable horizontal scaling
- Database becomes bottleneck at scale
- Consider:
  - Database clustering
  - Read replicas
  - Query caching layer
  - Message queue for async operations

## Error Handling

### At Agent Level
```python
try:
    self.set_status(AgentStatus.PROCESSING)
    # Process request
    self.set_status(AgentStatus.COMPLETED)
except Exception as e:
    self.set_status(AgentStatus.FAILED)
    # Log error in execution history
```

### At Orchestrator Level
- Catches agent registration errors
- Handles missing agents gracefully
- Returns error responses to user

### Database Operations (Future)
- Transaction rollback on errors
- Connection retry logic
- Graceful degradation

## Security Considerations

### Current Implementation
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- No authentication/authorization yet

### Future Enhancements
- Request authentication
- Agent-level permissions
- Audit trail for compliance
- Data encryption
- Rate limiting

## Monitoring and Observability

### Available Metrics
- Execution history per agent
- Request-to-completion tracking
- Error logging
- Workflow duration

### Logging Strategy
- Agent operations logged in execution_history
- Future: Centralized logging with structured logs
- Debug mode via Config.DEBUG

---

**Architecture Version**: 1.0
**Last Updated**: 2024-01-15
**Status**: Foundational (Phase 1 Complete)
