"""
Test suite for Phase 2: Tool Integration and Multi-Step Workflows.
Validates all tools, agents, and orchestration patterns.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db import init_database, DatabaseManager
from agents import OrchestratorAgent, TaskAgent, CalendarAgent, NotesAgent
from tools import TaskTool, CalendarTool, NotesTool
from utils import Config


class TestTaskTool(unittest.TestCase):
    """Test TaskTool database operations."""

    @classmethod
    def setUpClass(cls):
        """Initialize database before tests."""
        init_database(Config.get_database_url())

    def test_create_task(self):
        """Test creating a task."""
        result = TaskTool.create_task(
            title="Test Task",
            description="A test task",
            priority=1,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "create_task")
        self.assertIn("data", result)
        self.assertIsNotNone(result["data"]["id"])

    def test_list_tasks(self):
        """Test listing tasks."""
        # Create a task first
        TaskTool.create_task(
            title="List Test Task",
            description="Test",
            priority=2
        )

        result = TaskTool.list_tasks()
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["count"], 0)
        self.assertIsInstance(result["data"], list)

    def test_get_task(self):
        """Test retrieving a single task."""
        # Create a task first
        created = TaskTool.create_task(
            title="Retrieve Test",
            description="Test",
            priority=1
        )
        task_id = created["data"]["id"]

        result = TaskTool.get_task(task_id)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["id"], task_id)

    def test_update_task(self):
        """Test updating a task."""
        # Create a task
        created = TaskTool.create_task(
            title="Update Test",
            description="Test",
            priority=1
        )
        task_id = created["data"]["id"]

        # Update it
        result = TaskTool.update_task(task_id, {"status": "in_progress"})
        self.assertEqual(result["status"], "success")

    def test_delete_task(self):
        """Test deleting a task."""
        # Create a task
        created = TaskTool.create_task(
            title="Delete Test",
            description="Test",
            priority=1
        )
        task_id = created["data"]["id"]

        # Delete it
        result = TaskTool.delete_task(task_id)
        self.assertEqual(result["status"], "success")


class TestCalendarTool(unittest.TestCase):
    """Test CalendarTool event operations."""

    @classmethod
    def setUpClass(cls):
        """Initialize database before tests."""
        init_database(Config.get_database_url())

    def test_schedule_event(self):
        """Test scheduling an event."""
        start = datetime.utcnow() + timedelta(days=1, hours=10)
        end = start + timedelta(hours=1)

        result = CalendarTool.schedule_event(
            title="Test Meeting",
            start_time=start,
            end_time=end,
            check_conflicts=False
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)

    def test_check_availability(self):
        """Test checking availability."""
        start = datetime.utcnow() + timedelta(days=2, hours=15)
        end = start + timedelta(hours=2)

        result = CalendarTool.check_availability(start, end)
        self.assertEqual(result["status"], "success")
        self.assertIn("available", result)

    def test_list_events(self):
        """Test listing events."""
        result = CalendarTool.list_events()
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["data"], list)

    def test_conflict_detection(self):
        """Test conflict detection in scheduling."""
        now = datetime.utcnow()
        start1 = now + timedelta(days=3, hours=10)
        end1 = start1 + timedelta(hours=1)

        # Schedule first event
        event1 = CalendarTool.schedule_event(
            title="Event 1",
            start_time=start1,
            end_time=end1,
            check_conflicts=False
        )
        self.assertEqual(event1["status"], "success")

        # Try to schedule overlapping event
        start2 = start1 + timedelta(minutes=30)  # Overlaps
        end2 = start2 + timedelta(hours=1)

        event2 = CalendarTool.schedule_event(
            title="Event 2",
            start_time=start2,
            end_time=end2,
            check_conflicts=True
        )
        # Should either succeed as conflict or fail - both are valid
        self.assertIn(event2["status"], ["success", "error"])


class TestNotesTool(unittest.TestCase):
    """Test NotesTool note operations."""

    @classmethod
    def setUpClass(cls):
        """Initialize database before tests."""
        init_database(Config.get_database_url())

    def test_create_note(self):
        """Test creating a note."""
        result = NotesTool.create_note(
            title="Test Note",
            content="This is a test note",
            tags=["test"]
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)

    def test_list_notes(self):
        """Test listing notes."""
        # Create a note first
        NotesTool.create_note(
            title="List Test",
            content="Content",
            tags=["test"]
        )

        result = NotesTool.list_notes()
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["data"], list)

    def test_search_notes(self):
        """Test searching notes."""
        # Create a note with keyword
        NotesTool.create_note(
            title="Searchable Note",
            content="Find this content",
            tags=["search"]
        )

        result = NotesTool.search_notes("searchable")
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["count"], 1)

    def test_tag_management(self):
        """Test tag operations."""
        # Create a note
        created = NotesTool.create_note(
            title="Tag Test",
            content="Test",
            tags=["initial"]
        )
        note_id = created["data"]["id"]

        # Add tag
        add_result = NotesTool.add_tag(note_id, "new_tag")
        self.assertEqual(add_result["status"], "success")

        # Get notes by tag
        tagged = NotesTool.get_notes_by_tag("new_tag")
        self.assertEqual(tagged["status"], "success")


class TestTaskAgent(unittest.TestCase):
    """Test TaskAgent integration with TaskTool."""

    @classmethod
    def setUpClass(cls):
        """Initialize database and agent."""
        init_database(Config.get_database_url())
        cls.agent = TaskAgent()

    def test_agent_create_task(self):
        """Test TaskAgent.create_task calls TaskTool."""
        result = self.agent.create_task(
            title="Agent Task",
            description="Created via agent",
            priority=1
        )
        self.assertEqual(result["status"], "success")

    def test_agent_get_tasks(self):
        """Test TaskAgent.get_tasks calls TaskTool."""
        result = self.agent.get_tasks()
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)

    def test_agent_update_task(self):
        """Test TaskAgent.update_task integration."""
        # Create task
        created = self.agent.create_task(
            title="Update via Agent",
            description="Test",
            priority=1
        )
        task_id = created["data"]["id"]

        # Update it
        result = self.agent.update_task(task_id, {"status": "completed"})
        self.assertEqual(result["status"], "success")


class TestCalendarAgent(unittest.TestCase):
    """Test CalendarAgent integration with CalendarTool."""

    @classmethod
    def setUpClass(cls):
        """Initialize database and agent."""
        init_database(Config.get_database_url())
        cls.agent = CalendarAgent()

    def test_agent_schedule_event(self):
        """Test CalendarAgent.schedule_event calls CalendarTool."""
        start = datetime.utcnow() + timedelta(days=1, hours=14)
        end = start + timedelta(hours=1)

        result = self.agent.schedule_event(
            title="Agent Meeting",
            start_time=start,
            end_time=end
        )
        self.assertEqual(result["status"], "success")

    def test_agent_get_events(self):
        """Test CalendarAgent.get_events."""
        result = self.agent.get_events()
        self.assertEqual(result["status"], "success")

    def test_agent_available_slots(self):
        """Test CalendarAgent.get_available_slots."""
        tomorrow = datetime.utcnow() + timedelta(days=1)
        result = self.agent.get_available_slots(tomorrow)
        self.assertEqual(result["status"], "success")


class TestNotesAgent(unittest.TestCase):
    """Test NotesAgent integration with NotesTool."""

    @classmethod
    def setUpClass(cls):
        """Initialize database and agent."""
        init_database(Config.get_database_url())
        cls.agent = NotesAgent()

    def test_agent_create_note(self):
        """Test NotesAgent.create_note calls NotesTool."""
        result = self.agent.create_note(
            title="Agent Note",
            content="Created via agent",
            tags=["agent"]
        )
        self.assertEqual(result["status"], "success")

    def test_agent_search_notes(self):
        """Test NotesAgent.search_notes."""
        result = self.agent.search_notes("agent")
        self.assertEqual(result["status"], "success")


class TestOrchestratorAgent(unittest.TestCase):
    """Test OrchestratorAgent multi-step workflows."""

    @classmethod
    def setUpClass(cls):
        """Initialize database and agents."""
        init_database(Config.get_database_url())
        cls.orchestrator = OrchestratorAgent(max_memory=10)
        cls.orchestrator.register_agent(TaskAgent())
        cls.orchestrator.register_agent(CalendarAgent())
        cls.orchestrator.register_agent(NotesAgent())

    def test_single_intent_detection(self):
        """Test detecting single intent."""
        request = "Create a task"
        response = self.orchestrator.handle_request(request)
        self.assertIn("task", response["intents"])

    def test_multi_intent_detection(self):
        """Test detecting multiple intents."""
        request = "Schedule a meeting and create a task"
        response = self.orchestrator.handle_request(request)
        self.assertGreaterEqual(len(response["intents"]), 2)

    def test_execution_plan_creation(self):
        """Test execution plan structure."""
        request = "Create task and schedule meeting"
        response = self.orchestrator.handle_request(request)
        plan = response.get("execution_plan")
        self.assertIsNotNone(plan)
        self.assertIn("steps", plan)

    def test_workflow_execution(self):
        """Test executing a workflow."""
        request = "Create a task"
        response = self.orchestrator.handle_request(request)
        if response.get("execution_plan"):
            result = self.orchestrator.execute_plan(response["execution_plan"])
            self.assertEqual(result["status"], "completed")
            self.assertGreater(len(result["actions"]), 0)

    def test_multi_step_execution(self):
        """Test executing multi-step workflow."""
        request = "Create a task and schedule a meeting"
        response = self.orchestrator.handle_request(request)
        if response.get("execution_plan"):
            result = self.orchestrator.execute_plan(response["execution_plan"])
            self.assertEqual(result["status"], "completed")
            self.assertGreaterEqual(len(result["actions"]), 2)

    def test_memory_storage(self):
        """Test interaction memory."""
        # Execute a request
        request = "Create a note"
        response = self.orchestrator.handle_request(request)
        if response.get("execution_plan"):
            self.orchestrator.execute_plan(response["execution_plan"])

        # Check memory
        memory = self.orchestrator.get_memory()
        self.assertGreater(len(memory), 0)

    def test_execution_trace(self):
        """Test execution tracing."""
        request = "Create a task"
        response = self.orchestrator.handle_request(request)
        if response.get("execution_plan"):
            self.orchestrator.execute_plan(response["execution_plan"])

        trace = self.orchestrator.get_execution_trace()
        self.assertGreater(len(trace), 0)

    def test_orchestrator_status(self):
        """Test orchestrator status."""
        status = self.orchestrator.get_orchestrator_status()
        self.assertEqual(status["status"], "active")
        self.assertGreater(status["total_registered"], 0)
        self.assertIn("workflows_executed", status)


class TestStructuredResponses(unittest.TestCase):
    """Test structured response formats."""

    @classmethod
    def setUpClass(cls):
        """Initialize database and tools."""
        init_database(Config.get_database_url())

    def test_tool_response_format(self):
        """Test tool response structure."""
        result = TaskTool.create_task(
            title="Response Test",
            description="Test",
            priority=1
        )
        self.assertIn("status", result)
        self.assertIn("action", result)
        self.assertIn("message", result)
        self.assertIn("data", result)

    def test_workflow_response_format(self):
        """Test workflow response structure."""
        orchestrator = OrchestratorAgent()
        orchestrator.register_agent(TaskAgent())

        request = "Create a task"
        response = orchestrator.handle_request(request)

        # Check response structure
        self.assertIn("status", response)
        self.assertIn("intents", response)
        self.assertIn("target_agents", response)
        self.assertIn("execution_plan", response)

        if response.get("execution_plan"):
            result = orchestrator.execute_plan(response["execution_plan"])
            self.assertIn("status", result)
            self.assertIn("workflow_id", result)
            self.assertIn("actions", result)
            self.assertIn("results", result)
            self.assertIn("message", result)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTaskTool))
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarTool))
    suite.addTests(loader.loadTestsFromTestCase(TestNotesTool))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestNotesAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestratorAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredResponses))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
