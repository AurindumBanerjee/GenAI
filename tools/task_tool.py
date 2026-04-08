"""
Task Tool - MCP-style tool for task operations.
Handles all CRUD operations for tasks with database integration.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from db import get_db_manager, Task
from sqlalchemy.orm import Session
from utils.schemas import TaskCreate, TaskResponse


class TaskTool:
    """
    MCP-style tool for task management.
    All methods accept structured input and return JSON output.
    """

    @staticmethod
    def create_task(
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: int = 0,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """
        Create a new task in the database.

        Args:
            title: Task title (required)
            description: Task description
            due_date: Due date for the task
            priority: Priority level (0-3)
            status: Initial status (default: pending)

        Returns:
            Dictionary with created task data or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                # Create new task
                new_task = Task(
                    title=title,
                    description=description,
                    due_date=due_date,
                    priority=priority,
                    status=status
                )
                session.add(new_task)
                session.flush()  # Get the ID

                response = TaskResponse(
                    id=new_task.id,
                    title=new_task.title,
                    description=new_task.description,
                    due_date=new_task.due_date,
                    priority=new_task.priority,
                    status=new_task.status,
                    created_at=new_task.created_at,
                    updated_at=new_task.updated_at
                )

                return {
                    "status": "success",
                    "action": "create_task",
                    "data": response.model_dump(),
                    "message": f"Task created: {title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "create_task",
                "error": str(e),
                "message": f"Failed to create task: {str(e)}"
            }

    @staticmethod
    def update_task(task_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            updates: Dictionary of fields to update

        Returns:
            Dictionary with updated task or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                task = session.query(Task).filter(Task.id == task_id).first()

                if not task:
                    return {
                        "status": "error",
                        "action": "update_task",
                        "error": "Task not found",
                        "message": f"Task {task_id} not found"
                    }

                # Update allowed fields
                allowed_fields = ["title", "description", "due_date", "priority", "status"]
                for field, value in updates.items():
                    if field in allowed_fields and value is not None:
                        setattr(task, field, value)

                session.flush()

                response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    due_date=task.due_date,
                    priority=task.priority,
                    status=task.status,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                return {
                    "status": "success",
                    "action": "update_task",
                    "data": response.model_dump(),
                    "message": f"Task {task_id} updated"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "update_task",
                "error": str(e),
                "message": f"Failed to update task: {str(e)}"
            }

    @staticmethod
    def list_tasks(
        status: Optional[str] = None,
        priority: Optional[int] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List tasks with optional filtering.

        Args:
            status: Filter by status (pending, in_progress, completed, cancelled)
            priority: Filter by priority level
            limit: Maximum number of tasks to return

        Returns:
            Dictionary with list of tasks or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                query = session.query(Task)

                # Apply filters
                if status:
                    query = query.filter(Task.status == status)
                if priority is not None:
                    query = query.filter(Task.priority == priority)

                # Order by priority (desc) then due_date (asc)
                tasks = query.order_by(
                    Task.priority.desc(),
                    Task.due_date.asc()
                ).limit(limit).all()

                task_list = [
                    TaskResponse(
                        id=t.id,
                        title=t.title,
                        description=t.description,
                        due_date=t.due_date,
                        priority=t.priority,
                        status=t.status,
                        created_at=t.created_at,
                        updated_at=t.updated_at
                    ).model_dump()
                    for t in tasks
                ]

                return {
                    "status": "success",
                    "action": "list_tasks",
                    "data": task_list,
                    "count": len(task_list),
                    "message": f"Retrieved {len(task_list)} tasks"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "list_tasks",
                "error": str(e),
                "message": f"Failed to list tasks: {str(e)}"
            }

    @staticmethod
    def get_task(task_id: int) -> Dict[str, Any]:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Dictionary with task data or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                task = session.query(Task).filter(Task.id == task_id).first()

                if not task:
                    return {
                        "status": "error",
                        "action": "get_task",
                        "error": "Task not found",
                        "message": f"Task {task_id} not found"
                    }

                response = TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    due_date=task.due_date,
                    priority=task.priority,
                    status=task.status,
                    created_at=task.created_at,
                    updated_at=task.updated_at
                )

                return {
                    "status": "success",
                    "action": "get_task",
                    "data": response.model_dump(),
                    "message": f"Retrieved task {task_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "get_task",
                "error": str(e),
                "message": f"Failed to get task: {str(e)}"
            }

    @staticmethod
    def delete_task(task_id: int) -> Dict[str, Any]:
        """
        Delete a task by ID.

        Args:
            task_id: Task ID to delete

        Returns:
            Dictionary with deletion status or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                task = session.query(Task).filter(Task.id == task_id).first()

                if not task:
                    return {
                        "status": "error",
                        "action": "delete_task",
                        "error": "Task not found",
                        "message": f"Task {task_id} not found"
                    }

                title = task.title
                session.delete(task)

                return {
                    "status": "success",
                    "action": "delete_task",
                    "data": {"deleted_id": task_id},
                    "message": f"Task deleted: {title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "delete_task",
                "error": str(e),
                "message": f"Failed to delete task: {str(e)}"
            }

    @staticmethod
    def get_overdue_tasks() -> Dict[str, Any]:
        """
        Get all overdue tasks.

        Returns:
            Dictionary with list of overdue tasks
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                now = datetime.utcnow()
                tasks = session.query(Task).filter(
                    Task.due_date < now,
                    Task.status != "completed"
                ).order_by(Task.due_date.asc()).all()

                task_list = [
                    TaskResponse(
                        id=t.id,
                        title=t.title,
                        description=t.description,
                        due_date=t.due_date,
                        priority=t.priority,
                        status=t.status,
                        created_at=t.created_at,
                        updated_at=t.updated_at
                    ).model_dump()
                    for t in tasks
                ]

                return {
                    "status": "success",
                    "action": "get_overdue_tasks",
                    "data": task_list,
                    "count": len(task_list),
                    "message": f"Found {len(task_list)} overdue tasks"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "get_overdue_tasks",
                "error": str(e),
                "message": f"Failed to get overdue tasks: {str(e)}"
            }
