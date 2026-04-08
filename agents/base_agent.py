"""
Base agent class following Google ADK patterns.
Provides the foundational structure for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import json


class AgentRole(Enum):
    """Enumeration of agent roles in the system."""
    ORCHESTRATOR = "orchestrator"
    TASK_MANAGER = "task_manager"
    CALENDAR_MANAGER = "calendar_manager"
    NOTE_MANAGER = "note_manager"
    OBSERVER = "observer"


class AgentStatus(Enum):
    """Enumeration of agent execution statuses."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseTool:
    """
    Represents a tool that an agent can use (placeholder for future integration).
    """

    def __init__(self, name: str, description: str, parameters: Optional[List[str]] = None):
        """
        Initialize a tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: List of parameter names the tool accepts
        """
        self.name = name
        self.description = description
        self.parameters = parameters or []

    def __repr__(self):
        return f"<Tool(name='{self.name}')>"


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Follows Google ADK patterns for extensibility and modularity.
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str = "",
        tools: Optional[List[BaseTool]] = None
    ):
        """
        Initialize a base agent.

        Args:
            name: Unique agent name
            role: AgentRole enum value
            description: Human-readable description of agent purpose
            tools: List of available tools (initially empty, populated later)
        """
        self.name = name
        self.role = role
        self.description = description
        self.tools = tools or []
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    def handle_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle a user request. Must be implemented by subclasses.

        Args:
            user_input: The user's input/request
            context: Optional context dictionary with additional information

        Returns:
            Dictionary with response and metadata
        """
        pass

    def add_tool(self, tool: BaseTool) -> None:
        """
        Register a tool with this agent.

        Args:
            tool: BaseTool instance to add
        """
        if tool not in self.tools:
            self.tools.append(tool)

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from this agent.

        Args:
            tool_name: Name of the tool to remove
        """
        self.tools = [t for t in self.tools if t.name != tool_name]

    def get_tools(self) -> List[BaseTool]:
        """
        Get all available tools.

        Returns:
            List of BaseTool instances
        """
        return self.tools

    def set_status(self, status: AgentStatus) -> None:
        """
        Update agent status.

        Args:
            status: New AgentStatus value
        """
        self.status = status
        self.last_activity = datetime.utcnow()

    def log_execution(self, request: str, response: Dict[str, Any], success: bool = True) -> None:
        """
        Log agent execution for audit trail.

        Args:
            request: The input request
            response: The response data
            success: Whether execution was successful
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request": request,
            "response": response,
            "success": success,
            "status": self.status.value
        }
        self.execution_history.append(log_entry)

    def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve execution history.

        Args:
            limit: Optional limit on number of records to return (most recent)

        Returns:
            List of execution log entries
        """
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent metadata and configuration.

        Returns:
            Dictionary with agent information
        """
        return {
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "status": self.status.value,
            "tools_count": len(self.tools),
            "tools": [{"name": t.name, "description": t.description} for t in self.tools],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "execution_count": len(self.execution_history)
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role.value}')>"
