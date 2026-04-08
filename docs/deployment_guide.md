#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GenAI Deployment & Runbook Guide

Quick start guide for running and deploying the GenAI multi-agent API system.
"""

---

# 🚀 GenAI API - Getting Started

## Prerequisites

- Python 3.9+
- pip or conda
- Optional: Docker & Docker Compose

---

## 1. Installation

### Clone Repository
```bash
git clone https://github.com/AurindumBanerjee/GenAI.git
cd GenAI
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "import fastapi; import sqlalchemy; print('✅ Dependencies installed')"
```

---

## 2. Database Setup

Database is automatically initialized on first run. To manually initialize:

```bash
python -c "from db import init_database; from utils import Config; init_database(Config.get_database_url()); print('✅ Database ready')"
```

Database location: `data/app.db` (SQLite)

---

## 3. Start the API Server

### Development Mode (with auto-reload)
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Recommended for Production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "api.main:app" --worker-class uvicorn.workers.UvicornWorker
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## 4. Access the API

### Interactive Documentation (Swagger UI)
```
http://localhost:8000/docs
```

### Alternative Documentation (ReDoc)
```
http://localhost:8000/redoc
```

### OpenAPI Specification
```
http://localhost:8000/openapi.json
```

---

## 5. Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Example: Query Endpoint
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Schedule a meeting tomorrow at 3 PM",
    "include_trace": false
  }'
```

### Example: List Tasks
```bash
curl http://localhost:8000/tasks
```

### Example: Create Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix bug in API",
    "description": "Resolve authentication issue",
    "priority": 1,
    "due_date": "2024-02-15T23:59:59"
  }'
```

---

## 6. Demo Workflows

Run predefined demo scenarios:

### Demo 1: Schedule Meeting & Create Task
```bash
curl -X POST http://localhost:8000/demo/workflows?case=1
```

### Demo 2: Query Tasks Tomorrow
```bash
curl -X POST http://localhost:8000/demo/workflows?case=2
```

### Demo 3: Store Note About Project
```bash
curl -X POST http://localhost:8000/demo/workflows?case=3
```

### Demo 4: Find Notes
```bash
curl -X POST http://localhost:8000/demo/workflows?case=4
```

---

## 7. Docker Deployment

### Build Docker Image
```bash
docker build -t genai-api:latest .
```

### Run Docker Container
```bash
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL="sqlite:///./data/app.db" \
  genai-api:latest
```

### Docker Compose (Optional)
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      DATABASE_URL: sqlite:///./data/app.db
      DEBUG: "false"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with: `docker-compose up`

---

## 8. Environment Variables (.env)

Create `.env` file in project root:

```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# Debug mode
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000

# Logging
AGENT_LOG_LEVEL=INFO
```

---

## 9. System Status & Monitoring

### Check API Status
```bash
curl http://localhost:8000/status
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

### View Orchestrator Memory
```bash
curl "http://localhost:8000/orchestrator/memory?limit=5"
```

### Get Workflow Trace
```bash
curl "http://localhost:8000/orchestrator/trace/WF-20240115143022-001"
```

---

## 10. Run Tests

### All Tests
```bash
pytest test_phase2.py -v
```

### API Tests
```bash
pytest api/tests/ -v
```

### Specific Test
```bash
pytest test_phase2.py::TestOrchestratorAgent::test_multi_step_execution -v
```

---

## 11. Development Workflow

### Start Development Server
```bash
uvicorn api.main:app --reload
```

The server will:
- Auto-reload on code changes
- Display detailed error messages
- Log all requests

### Common Development Tasks

**Add new endpoint:**
1. Create route in `api/main.py`
2. Define request/response models
3. Implement logic using tools/agents
4. Test in Swagger UI (`/docs`)

**Modify agent logic:**
1. Update agent in `agents/`
2. Server auto-reloads
3. Retry request in Swagger UI

**Database changes:**
1. Modify models in `db/models.py`
2. Delete `data/app.db`
3. Restart server (will reinitialize)

---

## 12. Production Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use production-grade database (PostgreSQL, MySQL)
- [ ] Set strong `DATABASE_URL`
- [ ] Configure CORS appropriately
- [ ] Use Gunicorn or similar production ASGI server
- [ ] Set up SSL/TLS certificates
- [ ] Configure log aggregation
- [ ] Set up monitoring/alerting
- [ ] Test all demo workflows
- [ ] Load test the system
- [ ] Document API endpoints
- [ ] Set up CI/CD pipeline

---

## 13. Azure Cloud Deployment

### Prerequisites
- Azure CLI installed
- Azure subscription active

### Deploy to Container Apps
```bash
# Login to Azure
az login

# Create resource group
az group create --name genai-rg --location eastus

# Create container registry
az acr create --resource-group genai-rg --name genairegistry --sku Basic

# Build and push image
az acr build --registry genairegistry --image genai-api:latest .

# Create Container App
az containerapp create \
  --name genai-api \
  --resource-group genai-rg \
  --image genairegistry.azurecr.io/genai-api:latest \
  --target-port 8000 \
  --ingress external
```

### View Deployment
```bash
az containerapp show --name genai-api --resource-group genai-rg
```

---

## 14. Troubleshooting

### Port Already in Use
```bash
# Change port
uvicorn api.main:app --port 8001

# Or kill process using port 8000
# On Windows: netstat -ano | findstr :8000
# On Linux: lsof -i :8000
```

### Database Lock Error
```bash
# Delete database and reinitialize
rm data/app.db
python api/main.py
```

### Import Errors
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### API Timeout
- Increase timeout in client
- Check database performance
- Monitor agent execution time

---

## 15. Performance Tuning

### Database Optimization
```python
# In db/database.py
# Add connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=40
)
```

### API Response Optimization
- Use `include_trace=False` for production
- Implement caching for frequently accessed data
- Use pagination for large result sets

### Server Optimization
```bash
# Increase workers
gunicorn -w 8 "api.main:app" --worker-class uvicorn.workers.UvicornWorker

# Monitor resources
ps aux | grep gunicorn
```

---

## 16. Example Workflows

### Workflow 1: Daily Standup Planning
```bash
# Schedule standup meeting
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Schedule daily standup tomorrow at 9 AM and create task for agenda",
    "include_trace": true
  }'
```

### Workflow 2: Project Management
```bash
# Create project tasks and schedule review
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Create task for project milestone and schedule review meeting"
  }'
```

### Workflow 3: Documentation
```bash
# Create and organize notes
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Store documentation notes and tag with project"
  }'
```

---

## 17. API Client Examples

### Python Client
```python
import requests

BASE_URL = "http://localhost:8000"

# Query
response = requests.post(
    f"{BASE_URL}/query",
    json={"user_input": "Schedule meeting tomorrow", "include_trace": True}
)
print(response.json())

# List tasks
tasks = requests.get(f"{BASE_URL}/tasks").json()
print(f"Tasks: {tasks['count']}")
```

### JavaScript/Node.js Client
```javascript
const BASE_URL = "http://localhost:8000";

// Query
async function query(userInput) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: userInput, include_trace: true })
  });
  return await response.json();
}

// Example
query("Schedule meeting tomorrow").then(result => {
  console.log(`Workflow: ${result.workflow_id}`);
  console.log(`Status: ${result.status}`);
});
```

### cURL Examples (See API Documentation)
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for comprehensive cURL examples

---

## 18. Support & Documentation

| Topic | Location |
|-------|----------|
| API Endpoints | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Phase 2 Details | [PHASE2_DOCUMENTATION.md](PHASE2_DOCUMENTATION.md) |
| Phase 2 Summary | [PHASE2_COMPLETION_SUMMARY.md](PHASE2_COMPLETION_SUMMARY.md) |
| Quick Reference | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Main README | [README.md](README.md) |

---

## 19. Next Steps

1. **Run demo workflows** - Test all 4 demo cases
2. **Explore Swagger UI** - Try endpoints interactively
3. **Build custom client** - Integrate with your app
4. **Deploy to cloud** - Use Docker/Azure deployment
5. **Monitor in production** - Set up health checks & alerts

---

## 20. Version Info

- **API Version**: 2.0.0
- **Python**: 3.9+
- **FastAPI**: 0.104.1
- **SQLAlchemy**: 2.0.23
- **Pydantic**: 2.5.0

---

**Last Updated**: January 15, 2024  
**Status**: Production Ready ✅  
**Ready for Deployment**: Yes ✅
