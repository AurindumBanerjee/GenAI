"""
Orchestrator Agent - Coordinates all other agents in the system.
Routes requests to appropriate specialized agents and manages workflow.
"""

from typing import Any, Dict, List, Optional, Tuple
from agents.base_agent import BaseAgent, AgentRole, AgentStatus, BaseTool
from datetime import datetime


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator agent that:
    - Parses user input to determine intent
    - Routes requests to appropriate specialized agents
    - Manages multi-step workflows
    - Coordinates results from multiple agents
    """

    def __init__(self):
        """Initialize the orchestrator agent."""
        super().__init__(
            name="Orchestrator",
            role=AgentRole.ORCHESTRATOR,
            description="Main orchestrator that routes requests to specialized agents and manages workflows"
        )
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.workflow_steps: List[Dict[str, Any]] = []
        self.current_workflow: Optional[str] = None

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register a specialized agent with the orchestrator.

        Args:
            agent: BaseAgent instance to register
        """
        self.registered_agents[agent.name] = agent
        print(f"✓ Registered agent: {agent.name} ({agent.role.value})")

    def list_registered_agents(self) -> List[str]:
        """
        Get list of registered agents.

        Returns:
            List of agent names
        """
        return list(self.registered_agents.keys())

    def handle_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main request handler for the orchestrator.
        Parses user input and routes to appropriate agents.

        Args:
            user_input: User's natural language input
            context: Optional context with additional information

        Returns:
            Dictionary with routing decision and execution plan
        """
        self.set_status(AgentStatus.PROCESSING)

        try:
            # Step 1: Intent Detection
            intent = self._detect_intent(user_input)

            # Step 2: Route to appropriate agent(s)
            target_agents = self._route_request(intent)

            # Step 3: Build execution plan
            execution_plan = self._build_execution_plan(intent, target_agents, user_input, context)

            response = {
                "status": "success",
                "intent": intent,
                "target_agents": target_agents,
                "execution_plan": execution_plan,
                "ready_for_execution": True
            }

            self.set_status(AgentStatus.COMPLETED)
            self.log_execution(user_input, response, success=True)

            return response

        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e),
                "intent": None,
                "target_agents": [],
                "ready_for_execution": False
            }
            self.set_status(AgentStatus.FAILED)
            self.log_execution(user_input, error_response, success=False)
            return error_response

    def _detect_intent(self, user_input: str) -> str:
        """
        Detect user intent from input text.
        Simple pattern-based detection (can be enhanced with ML).

        Args:
            user_input: User input string

        Returns:
            Intent category: 'task', 'calendar', 'note', or 'unknown'
        """
        user_lower = user_input.lower()

        # Task-related keywords
        task_keywords = ["task", "todo", "create", "add task", "complete", "status", "deadline", "priority"]
        if any(kw in user_lower for kw in task_keywords):
            return "task"

        # Calendar-related keywords
        calendar_keywords = ["event", "meeting", "schedule", "calendar", "time", "appointment", "conflict"]
        if any(kw in user_lower for kw in calendar_keywords):
            return "calendar"

        # Note-related keywords
        note_keywords = ["note", "notes", "remember", "save", "document", "write", "search", "find"]
        if any(kw in user_lower for kw in note_keywords):
            return "note"

        return "unknown"

    def _route_request(self, intent: str) -> List[str]:
        """
        Route requests to appropriate agents based on intent.

        Args:
            intent: Detected intent

        Returns:
            List of agent names to involve in execution
        """
        routing = {
            "task": ["TaskAgent"],
            "calendar": ["CalendarAgent"],
            "note": ["NotesAgent"],
            "unknown": []
        }

        agents = routing.get(intent, [])
        # Filter to only registered agents
        return [a for a in agents if a in self.registered_agents]

    def _build_execution_plan(
        self,
        intent: str,
        target_agents: List[str],
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build an execution plan for the request.

        Args:
            intent: Detected user intent
            target_agents: List of agents to execute
            user_input: Original user input
            context: Additional context

        Returns:
            Execution plan with steps
        """
        plan = {
            "workflow_id": self._generate_workflow_id(),
            "intent": intent,
            "user_input": user_input,
            "steps": []
        }

        # Create steps for each target agent
        for idx, agent_name in enumerate(target_agents, 1):
            step = {
                "step_number": idx,
                "agent": agent_name,
                "action": f"Process {intent} request",
                "depends_on": idx - 1 if idx > 1 else None,
                "status": "pending"
            }
            plan["steps"].append(step)

        self.workflow_steps = plan["steps"]
        self.current_workflow = plan["workflow_id"]

        return plan

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a prepared execution plan.

        Args:
            plan: Execution plan from build_execution_plan

        Returns:
            Results from all steps
        """
        print(f"\n📋 Executing workflow: {plan['workflow_id']}")
        print(f"📌 Intent: {plan['intent']}")

        results = {
            "workflow_id": plan["workflow_id"],
            "total_steps": len(plan["steps"]),
            "step_results": [],
            "overall_status": "pending"
        }

        for step in plan["steps"]:
            agent_name = step["agent"]
            print(f"\n  → Step {step['step_number']}: {agent_name}")

            if agent_name in self.registered_agents:
                agent = self.registered_agents[agent_name]
                # Agent execution would happen here (to be implemented in step 7 with tool wiring)
                step_result = {
                    "step_number": step["step_number"],
                    "agent": agent_name,
                    "status": "pending_tool_implementation",
                    "message": "Awaiting tool integration"
                }
            else:
                step_result = {
                    "step_number": step["step_number"],
                    "agent": agent_name,
                    "status": "failed",
                    "error": f"Agent {agent_name} not registered"
                }

            results["step_results"].append(step_result)

        results["overall_status"] = "completed"
        return results

    def _generate_workflow_id(self) -> str:
        """
        Generate a unique workflow ID.

        Returns:
            Workflow ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        workflow_num = len(self.workflow_steps) + 1
        return f"WF-{timestamp}-{workflow_num:03d}"

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """
        Get current orchestrator status and configuration.

        Returns:
            Status dictionary
        """
        return {
            "agent_name": self.name,
            "status": self.status.value,
            "registered_agents": self.list_registered_agents(),
            "total_registered": len(self.registered_agents),
            "current_workflow": self.current_workflow,
            "execution_history_count": len(self.execution_history),
            "agent_details": {
                name: agent.get_agent_info()
                for name, agent in self.registered_agents.items()
            }
        }
