"""
Task Agent - Manages task creation, retrieval, and status updates.
Handles all task-related operations for the system.
Integrates with TaskTool for database operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentRole, AgentStatus
from tools.task_tool import TaskTool


class TaskAgent(BaseAgent):
    """
    Specialized agent for managing tasks.
    Responsibilities:
    - Create tasks
    - Retrieve tasks (single, filtered, or all)
    - Update task status and metadata
    - Query tasks by priority, due date, etc.
    """

    def __init__(self):
        """Initialize the task agent."""
        super().__init__(
            name="TaskAgent",
            role=AgentRole.TASK_MANAGER,
            description="Manages task creation, retrieval, and status updates"
        )

    def handle_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle task-related requests.

        Args:
            user_input: User's natural language input about tasks
            context: Optional context with database session or task data

        Returns:
            Dictionary with task operation result
        """
        self.set_status(AgentStatus.PROCESSING)

        try:
            # Determine operation type based on input
            operation = self._determine_operation(user_input)

            response = {
                "status": "success",
                "operation": operation,
                "message": f"Task operation '{operation}' parsed successfully",
                "ready_for_tool_execution": True
            }

            self.set_status(AgentStatus.COMPLETED)
            self.log_execution(user_input, response, success=True)
            return response

        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e),
                "ready_for_tool_execution": False
            }
            self.set_status(AgentStatus.FAILED)
            self.log_execution(user_input, error_response, success=False)
            return error_response

    def _determine_operation(self, user_input: str) -> str:
        """
        Determine which task operation to perform.

        Args:
            user_input: User input string

        Returns:
            Operation type: 'create', 'get', 'update', 'list', or 'unknown'
        """
        user_lower = user_input.lower()

        if any(kw in user_lower for kw in ["create", "add", "new task"]):
            return "create"
        elif any(kw in user_lower for kw in ["get", "show", "find", "retrieve", "what is"]):
            return "get"
        elif any(kw in user_lower for kw in ["update", "change", "set"]):
            return "update"
        elif any(kw in user_lower for kw in ["list", "all tasks", "show all", "get all"]):
            return "list"
        else:
            return "unknown"

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: int = 0,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Create a new task using TaskTool.

        Args:
            title: Task title
            description: Task description
            due_date: Due date for the task
            priority: Priority level (0-3)
            status: Initial task status

        Returns:
            Dictionary with task data and metadata
        """
        return TaskTool.create_task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status
        )

    def get_tasks(
        self,
        task_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve tasks with optional filtering (placeholder).
status: Optional[str] = None,
        priority: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve tasks with optional filtering using TaskTool.

        Args:
            status: Optional status filter
            priority: Optional priority filter
            limit: Maximum number of tasks to return

        Returns:
            Dictionary with task results
        """
        return TaskTool.list_tasks(status=status, priority=priority, limit=limit)""
        Update an existing task (placeholder).

        Args:
            task_id: ID of task to update
            updates: Dictionary of fields to update

        Returns:
            Dictionary with update status
        """
        return {
            "status": "pending_db_execution",
            "message": "Task update pending database integration",
            "task_id": task_id,
            "updates": updatesusing TaskTool.

        Args:
            task_id: ID of task to update
            updates: Dictionary of fields to update

        Returns:
            Dictionary with update status
        """
        return TaskTool.update_task(task_id, updates)   "status": "pending_db_execution",
            "message": "Task query pending database integration",
            "filter": {"priority": priority}
        }

    def get_overdue_tasks(self) -> Dict[str, Any]:
        """
        Get all tasks that are past their due date.

        Returns: using TaskTool.

        Args:
            priority: Priority level to filter by

        Returns:
            Dictionary with filtered tasks
        """
        return TaskTool.list_tasks(priority=priority)

    def get_overdue_tasks(self) -> Dict[str, Any]:
        """
        Get all tasks that are past their due date using TaskTool.

        Returns:
            Dictionary with overdue tasks
        """
        return TaskTool.get_overdue_tasks()