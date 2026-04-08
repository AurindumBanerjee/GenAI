"""
Enhanced demo for Phase 2: Tool Integration.
Shows MCP-style tools, multi-step workflows, database operations, and execution tracing.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents import (
    OrchestratorAgent,
    TaskAgent,
    CalendarAgent,
    NotesAgent
)
from db import init_database
from utils import Config
from tools import TaskTool, CalendarTool, NotesTool


def demo_tool_integration():
    """
    Demonstrate MCP-style tools with real database operations.
    """
    print("=" * 80)
    print("🔧 Phase 2 Demo: Tool Integration & Database Operations")
    print("=" * 80)

    # Initialize database
    print("\n📦 Database Setup")
    print("-" * 80)
    init_database(Config.get_database_url())

    # Demo 1: Task Tool
    print("\n" + "=" * 80)
    print("📋 Task Tool - Database Operations")
    print("=" * 80)

    print("\n1️⃣ Creating tasks...")
    task1 = TaskTool.create_task(
        title="Complete project documentation",
        description="Write comprehensive docs",
        priority=2,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    print(f"   ✓ Task created: {task1['message']}")
    task1_id = task1.get("data", {}).get("id")

    task2 = TaskTool.create_task(
        title="Review code changes",
        description="PR review for main branch",
        priority=3,
        due_date=datetime.utcnow() + timedelta(days=1)
    )
    print(f"   ✓ Task created: {task2['message']}")

    print("\n2️⃣ Listing tasks...")
    tasks = TaskTool.list_tasks(limit=10)
    print(f"   ✓ {tasks['count']} tasks found")
    for task in tasks.get("data", [])[:2]:
        print(f"     - {task['title']} (Priority: {task['priority']})")

    if task1_id:
        print("\n3️⃣ Updating task...")
        updated = TaskTool.update_task(task1_id, {"status": "in_progress"})
        print(f"   ✓ {updated['message']}")

    # Demo 2: Calendar Tool
    print("\n" + "=" * 80)
    print("📅 Calendar Tool - Event Scheduling")
    print("=" * 80)

    now = datetime.utcnow()
    start = now + timedelta(days=1, hours=10)
    end = start + timedelta(hours=1)

    print("\n1️⃣ Checking availability...")
    availability = CalendarTool.check_availability(start, end)
    print(f"   ✓ {availability['message']}")
    print(f"   Available: {availability['available']}")

    print("\n2️⃣ Scheduling event...")
    event = CalendarTool.schedule_event(
        title="Team Standup",
        start_time=start,
        end_time=end,
        participants=["alice@example.com", "bob@example.com"],
        location="Conference Room A",
        check_conflicts=True
    )
    print(f"   ✓ {event['message']}")
    event_id = event.get("data", {}).get("id")

    print("\n3️⃣ Listing events...")
    events = CalendarTool.list_events(limit=5)
    print(f"   ✓ {events['count']} events found")

    if event_id:
        print("\n4️⃣ Adding participant...")
        participant = CalendarTool.add_participant(event_id, "charlie@example.com")
        print(f"   ✓ {participant['message']}")

    # Demo 3: Notes Tool
    print("\n" + "=" * 80)
    print("📝 Notes Tool - Note Management")
    print("=" * 80)

    print("\n1️⃣ Creating notes...")
    note1 = NotesTool.create_note(
        title="System Architecture",
        content="Multi-agent architecture with orchestrator pattern for task management",
        tags=["architecture", "ai", "design"]
    )
    print(f"   ✓ {note1['message']}")
    note1_id = note1.get("data", {}).get("id")

    note2 = NotesTool.create_note(
        title="Meeting Notes",
        content="Discussed project timeline and resource allocation",
        tags=["meeting", "project"]
    )
    print(f"   ✓ {note2['message']}")

    print("\n2️⃣ Searching notes...")
    search = NotesTool.search_notes("architecture", search_type="keyword")
    print(f"   ✓ Found {search['count']} notes")

    print("\n3️⃣ Listing notes by tag...")
    tagged = NotesTool.get_notes_by_tag("architecture")
    print(f"   ✓ Found {tagged['count']} notes with 'architecture' tag")

    if note1_id:
        print("\n4️⃣ Adding tag...")
        tagged_result = NotesTool.add_tag(note1_id, "important")
        print(f"   ✓ {tagged_result['message']}")


def demo_multi_step_workflows():
    """
    Demonstrate multi-step workflows with execution tracing.
    """
    print("\n" + "=" * 80)
    print("🔄 Multi-Step Workflows & Execution Tracing")
    print("=" * 80)

    # Initialize
    init_database(Config.get_database_url())
    orchestrator = OrchestratorAgent()

    print("\n🤖 Creating and registering agents...")
    task_agent = TaskAgent()
    calendar_agent = CalendarAgent()
    notes_agent = NotesAgent()

    orchestrator.register_agent(task_agent)
    orchestrator.register_agent(calendar_agent)
    orchestrator.register_agent(notes_agent)

    # Example 1: Single intent
    print("\n" + "-" * 80)
    print("📥 Request 1: Single Intent")
    print("-" * 80)
    
    request1 = "Create a task to finish the project report"
    print(f"User: {request1}")

    response1 = orchestrator.handle_request(request1)
    print(f"\n✓ Intent(s) detected: {response1['intents']}")
    print(f"✓ Target agent(s): {response1['target_agents']}")

    if response1.get("execution_plan"):
        result1 = orchestrator.execute_plan(response1["execution_plan"])
        print(f"\n📊 Results:")
        print(f"   Actions: {len(result1['actions'])}")
        print(f"   Results: {len(result1['results'])}")
        print(f"   Message: {result1['message']}")

    # Example 2: Multi-step workflow
    print("\n" + "-" * 80)
    print("📥 Request 2: Multi-Step Workflow")
    print("-" * 80)
    
    request2 = "Schedule a meeting with the team and create a follow-up task"
    print(f"User: {request2}")

    response2 = orchestrator.handle_request(request2)
    print(f"\n✓ Intent(s) detected: {response2['intents']}")
    print(f"✓ Target agent(s): {response2['target_agents']}")
    print(f"✓ Execution steps: {len(response2['execution_plan']['steps'])}")

    if response2.get("execution_plan"):
        result2 = orchestrator.execute_plan(response2["execution_plan"])
        print(f"\n📊 Results:")
        print(f"   Actions: {len(result2['actions'])}")
        print(f"   Results: {len(result2['results'])}")
        print(f"   Message: {result2['message']}")
        
        for action in result2['actions']:
            print(f"\n  Action {action['step']}: {action['agent']}")
            print(f"    Intent: {action['intent']}")
            print(f"    Time: {action['timestamp']}")

    # Example 3: Complex workflow
    print("\n" + "-" * 80)
    print("📥 Request 3: Complex Multi-Intent Workflow")
    print("-" * 80)
    
    request3 = "Create a task, schedule a meeting, and take notes about it"
    print(f"User: {request3}")

    response3 = orchestrator.handle_request(request3)
    print(f"\n✓ Intent(s) detected: {response3['intents']}")
    print(f"✓ Target agent(s): {response3['target_agents']}")
    print(f"✓ Execution plan complexity: {len(response3['execution_plan']['steps'])} steps")

    if response3.get("execution_plan"):
        result3 = orchestrator.execute_plan(response3["execution_plan"])
        print(f"\n📊 Multi-Step Results:")
        print(f"   Total Actions: {len(result3['actions'])}")
        print(f"   Total Results: {len(result3['results'])}")
        print(f"   Summary: {result3['message']}")


def demo_memory_and_tracing():
    """
    Demonstrate orchestrator memory and execution tracing.
    """
    print("\n" + "=" * 80)
    print("💾 Memory & Execution Tracing")
    print("=" * 80)

    # Initialize
    init_database(Config.get_database_url())
    orchestrator = OrchestratorAgent(max_memory=10)

    print("\n🤖 Setting up agents...")
    orchestrator.register_agent(TaskAgent())
    orchestrator.register_agent(CalendarAgent())
    orchestrator.register_agent(NotesAgent())

    # Process multiple requests
    requests = [
        "Create a task",
        "Schedule a meeting",
        "Take a note",
        "Create another task"
    ]

    print(f"\nProcessing {len(requests)} requests...")
    for i, req in enumerate(requests, 1):
        print(f"\n  {i}. {req}")
        response = orchestrator.handle_request(req)
        if response.get("execution_plan"):
            orchestrator.execute_plan(response["execution_plan"])

    # Show memory
    print("\n" + "-" * 80)
    print("📊 Orchestrator Memory")
    print("-" * 80)
    
    memory = orchestrator.get_memory()
    print(f"\nTotal interactions in memory: {len(memory)}")
    for idx, interaction in enumerate(memory[-3:], 1):
        print(f"\n{idx}. Workflow: {interaction['workflow_id']}")
        print(f"   Input: {interaction['user_input']}")
        print(f"   Intents: {interaction['intents']}")
        print(f"   Actions: {interaction['actions_count']}")

    # Show execution trace
    print("\n" + "-" * 80)
    print("📈 Execution Trace")
    print("-" * 80)
    
    trace = orchestrator.get_execution_trace()
    print(f"\nTotal workflows traced: {len(trace)}")
    
    if trace:
        latest = trace[-1]
        print(f"\nLatest workflow: {latest['workflow_id']}")
        print(f"Intents: {latest['intents']}")
        print(f"Actions executed: {len(latest['actions'])}")
        print(f"Results collected: {len(latest['results'])}")

    # Show orchestrator status
    print("\n" + "-" * 80)
    print("⚙️  Orchestrator Status")
    print("-" * 80)
    
    status = orchestrator.get_orchestrator_status()
    print(f"\nAgent: {status['agent_name']}")
    print(f"Status: {status['status']}")
    print(f"Registered Agents: {status['total_registered']}")
    print(f"Workflows Executed: {status['workflows_executed']}")
    print(f"Memory Size: {status['memory_size']}/{status['max_memory']}")


def demo_structured_responses():
    """
    Demonstrate structured response format.
    """
    print("\n" + "=" * 80)
    print("📋 Structured Response Format")
    print("=" * 80)

    # Initialize
    init_database(Config.get_database_url())
    orchestrator = OrchestratorAgent()
    orchestrator.register_agent(TaskAgent())
    orchestrator.register_agent(CalendarAgent())
    orchestrator.register_agent(NotesAgent())

    request = "Create a task and schedule a meeting"
    print(f"\nRequest: {request}")

    response = orchestrator.handle_request(request)
    plan = response.get("execution_plan")

    if plan:
        result = orchestrator.execute_plan(plan)

        print("\n" + "-" * 80)
        print("Structured Output:")
        print("-" * 80)
        
        import json
        print(json.dumps({
            "status": result["status"],
            "workflow_id": result["workflow_id"],
            "message": result["message"],
            "actions_count": len(result["actions"]),
            "results_count": len(result["results"]),
            "total_steps": result["total_steps"],
            "actions": [
                {
                    "step": a["step"],
                    "agent": a["agent"],
                    "intent": a["intent"]
                }
                for a in result["actions"]
            ]
        }, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 2: Tool Integration Demo")
    parser.add_argument(
        "--demo",
        choices=["tools", "workflows", "memory", "responses", "all"],
        default="all",
        help="Which demo to run"
    )

    args = parser.parse_args()

    if args.demo in ["tools", "all"]:
        demo_tool_integration()

    if args.demo in ["workflows", "all"]:
        demo_multi_step_workflows()

    if args.demo in ["memory", "all"]:
        demo_memory_and_tracing()

    if args.demo in ["responses", "all"]:
        demo_structured_responses()

    print("\n" + "=" * 80)
    print("✅ Phase 2 Demos Complete!")
    print("=" * 80)
