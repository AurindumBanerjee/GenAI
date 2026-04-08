"""
Main entry point for the Multi-Agent System.
Demonstrates initialization and basic usage.
"""

import sys
from pathlib import Path

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


def initialize_system():
    """
    Initialize the multi-agent system.
    Sets up database, creates agents, and registers them with orchestrator.
    """
    print("=" * 70)
    print("🚀 Initializing Multi-Agent System")
    print("=" * 70)

    # Initialize database
    print("\n📦 Database Setup")
    print("-" * 70)
    init_database(Config.get_database_url())

    # Create agents
    print("\n🤖 Creating Agents")
    print("-" * 70)
    orchestrator = OrchestratorAgent()
    task_agent = TaskAgent()
    calendar_agent = CalendarAgent()
    notes_agent = NotesAgent()

    print(f"✓ {orchestrator}")
    print(f"✓ {task_agent}")
    print(f"✓ {calendar_agent}")
    print(f"✓ {notes_agent}")

    # Register specialized agents with orchestrator
    print("\n📋 Agent Registration")
    print("-" * 70)
    orchestrator.register_agent(task_agent)
    orchestrator.register_agent(calendar_agent)
    orchestrator.register_agent(notes_agent)

    return orchestrator


def demo_request_handling():
    """
    Demonstrate request handling and routing.
    """
    print("\n" + "=" * 70)
    print("📨 Demo: Request Handling and Routing")
    print("=" * 70)

    orchestrator = initialize_system()

    # Example requests
    test_requests = [
        "Create a task to finish the project report by next Friday with high priority",
        "Schedule a meeting with Alice and Bob next Tuesday at 2 PM for 1 hour",
        "Save a note about the new AI architecture we discussed",
        "Show me all my pending tasks",
        "Check for conflicts on Thursday afternoon for a 1-hour meeting"
    ]

    for idx, request in enumerate(test_requests, 1):
        print(f"\n{'─' * 70}")
        print(f"📥 Request #{idx}:")
        print(f"   {request}")
        print(f"{'─' * 70}")

        # Get orchestrator's routing decision
        response = orchestrator.handle_request(request)

        print(f"✓ Status: {response['status']}")
        print(f"✓ Detected Intent: {response['intent']}")
        print(f"✓ Target Agent(s): {response['target_agents']}")

        if response.get("execution_plan"):
            plan = response["execution_plan"]
            print(f"✓ Workflow ID: {plan['workflow_id']}")
            print(f"✓ Execution Steps: {len(plan['steps'])}")

            for step in plan["steps"]:
                print(f"   Step {step['step_number']}: {step['agent']}")

        # Execute the plan
        if response.get("execution_plan"):
            print(f"\n→ Executing plan...")
            execution_result = orchestrator.execute_plan(response["execution_plan"])
            print(f"  Overall Status: {execution_result['overall_status']}")
            print(f"  Steps Completed: {len(execution_result['step_results'])}")


def demo_agent_methods():
    """
    Demonstrate individual agent methods (without actual DB operations).
    """
    print("\n" + "=" * 70)
    print("🔍 Demo: Agent Methods (Placeholder Responses)")
    print("=" * 70)

    # Create individual agents
    task_agent = TaskAgent()
    calendar_agent = CalendarAgent()
    notes_agent = NotesAgent()

    print("\n📋 Task Agent Methods:")
    print("-" * 70)
    result = task_agent.create_task(
        title="Complete project documentation",
        priority=2,
        description="Write comprehensive documentation for the system"
    )
    print(f"✓ create_task():")
    print(f"  Status: {result['status']}")
    print(f"  Message: {result['message']}")

    result = task_agent.get_overdue_tasks()
    print(f"✓ get_overdue_tasks():")
    print(f"  Status: {result['status']}")
    print(f"  Filter: {result['filter']}")

    print("\n📅 Calendar Agent Methods:")
    print("-" * 70)
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    result = calendar_agent.schedule_event(
        title="Team Standup",
        start_time=now + timedelta(days=1, hours=10),
        end_time=now + timedelta(days=1, hours=10, minutes=30),
        participants=["alice@example.com", "bob@example.com"],
        location="Conference Room A"
    )
    print(f"✓ schedule_event():")
    print(f"  Status: {result['status']}")
    print(f"  Check Conflicts: {result['check_conflicts']}")

    result = calendar_agent.get_available_slots(
        date=now + timedelta(days=2),
        duration_minutes=60
    )
    print(f"✓ get_available_slots():")
    print(f"  Status: {result['status']}")

    print("\n📝 Notes Agent Methods:")
    print("-" * 70)
    result = notes_agent.create_note(
        title="System Design Notes",
        content="Multi-agent architecture with orchestrator pattern for flexible task delegation",
        tags=["ai", "architecture", "design"]
    )
    print(f"✓ create_note():")
    print(f"  Status: {result['status']}")
    print(f"  Tags: {result['note_data']['tags']}")

    result = notes_agent.search_notes(
        query="architecture",
        search_type="keyword",
        limit=10
    )
    print(f"✓ search_notes():")
    print(f"  Status: {result['status']}")
    print(f"  Search Type: {result['search_params']['search_type']}")


def show_system_info():
    """
    Display system configuration and status information.
    """
    print("\n" + "=" * 70)
    print("ℹ️  System Information")
    print("=" * 70)

    orchestrator = initialize_system()

    status = orchestrator.get_orchestrator_status()

    print(f"\n🤖 Orchestrator: {status['agent_name']}")
    print(f"   Status: {status['status']}")
    print(f"   Registered Agents: {status['total_registered']}")

    print(f"\n📋 Registered Agents:")
    for agent_name in status['registered_agents']:
        agent_info = status['agent_details'][agent_name]
        print(f"   • {agent_name}")
        print(f"     Role: {agent_info['role']}")
        print(f"     Tools: {agent_info['tools_count']}")

    print(f"\n⚙️  Configuration:")
    config_dict = Config.to_dict()
    for key, value in config_dict.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent System Demo")
    parser.add_argument(
        "--demo",
        choices=["requests", "methods", "info"],
        default="requests",
        help="Which demo to run"
    )

    args = parser.parse_args()

    if args.demo == "requests":
        demo_request_handling()
    elif args.demo == "methods":
        demo_agent_methods()
    elif args.demo == "info":
        show_system_info()

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
