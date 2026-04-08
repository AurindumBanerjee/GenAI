"""
Orchestrator Agent - Coordinates all other agents in the system.
Routes requests to appropriate specialized agents and manages workflow.
Includes multi-step workflow support, execution tracing, and memory.
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
    - Maintains execution trace
    - Stores interaction memory
    """

    def __init__(self, max_memory: int = 20):
        """Initialize the orchestrator agent."""
        super().__init__(
            name="Orchestrator",
            role=AgentRole.ORCHESTRATOR,
            description="Main orchestrator that routes requests to specialized agents and manages workflows"
        )
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.workflow_steps: List[Dict[str, Any]] = []
        self.current_workflow: Optional[str] = None
        
        # New: Execution trace and memory
        self.execution_trace: List[Dict[str, Any]] = []
        self.interactions_memory: List[Dict[str, Any]] = []
        self.max_memory = max_memory

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
            intents = self._detect_intents(user_input)

            # Step 2: Route to appropriate agent(s)
            target_agents = self._route_request(intents)

            # Step 3: Build execution plan
            execution_plan = self._build_execution_plan(intents, target_agents, user_input, context)

            response = {
                "status": "success",
                "intents": intents,
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
                "intents": [],
                "target_agents": [],
                "ready_for_execution": False
            }
            self.set_status(AgentStatus.FAILED)
            self.log_execution(user_input, error_response, success=False)
            return error_response

    def _detect_intents(self, user_input: str) -> List[str]:
        """
        Detect ALL intents from input (supports multi-step workflows).
        
        Args:
            user_input: User input string

        Returns:
            List of intent categories detected
        """
        user_lower = user_input.lower()
        detected = []

        # Task-related keywords
        task_keywords = ["task", "todo", "create", "add task", "complete", "status", "deadline", "priority"]
        if any(kw in user_lower for kw in task_keywords):
            detected.append("task")

        # Calendar-related keywords
        calendar_keywords = ["event", "meeting", "schedule", "appointment", "conflict", "time", "attend"]
        if any(kw in user_lower for kw in calendar_keywords):
            detected.append("calendar")

        # Note-related keywords
        note_keywords = ["note", "notes", "remember", "save", "document", "write", "search", "find"]
        if any(kw in user_lower for kw in note_keywords):
            detected.append("note")

        return detected if detected else ["unknown"]

    def _route_request(self, intents: List[str]) -> List[str]:
        """
        Route requests to appropriate agents based on intents.
        Supports multi-agent workflows.

        Args:
            intents: List of detected intents

        Returns:
            List of agent names to invoke (in order)
        """
        routing = {
            "task": "TaskAgent",
            "calendar": "CalendarAgent",
            "note": "NotesAgent",
            "unknown": None
        }

        agents = []
        for intent in intents:
            agent_name = routing.get(intent)
            if agent_name and agent_name in self.registered_agents:
                agents.append(agent_name)

        return agents

    def _build_execution_plan(
        self,
        intents: List[str],
        target_agents: List[str],
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build an execution plan for the request, supporting multi-step workflows.

        Args:
            intents: List of detected intents
            target_agents: List of agents to execute
            user_input: Original user input
            context: Additional context

        Returns:
            Execution plan with steps
        """
        plan = {
            "workflow_id": self._generate_workflow_id(),
            "intents": intents,
            "user_input": user_input,
            "steps": [],
            "created_at": datetime.utcnow().isoformat()
        }

        # Create steps for each target agent (sequential)
        for idx, agent_name in enumerate(target_agents, 1):
            step = {
                "step_number": idx,
                "agent": agent_name,
                "intent": intents[min(idx-1, len(intents)-1)],
                "action": f"Process {intents[min(idx-1, len(intents)-1)]} request",
                "depends_on": idx - 1 if idx > 1 else None,
                "status": "pending"
            }
            plan["steps"].append(step)

        self.workflow_steps = plan["steps"]
        self.current_workflow = plan["workflow_id"]

        return plan

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a prepared execution plan with full tracing and structured output.

        Args:
            plan: Execution plan from build_execution_plan

        Returns:
            Structured results with actions, results, and execution trace
        """
        workflow_id = plan["workflow_id"]
        print(f"\n📋 Executing workflow: {workflow_id}")
        print(f"📌 Intents: {', '.join(plan['intents'])}")

        # Initialize trace
        trace_entry = {
            "workflow_id": workflow_id,
            "user_input": plan["user_input"],
            "intents": plan["intents"],
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [],
            "results": []
        }

        actions = []
        results = []
        step_results = []

        # Execute each step
        for step in plan["steps"]:
            agent_name = step["agent"]
            intent = step["intent"]
            
            print(f"\n  → Step {step['step_number']}/{len(plan['steps'])}: {agent_name}")
            print(f"    Intent: {intent}")

            if agent_name in self.registered_agents:
                agent = self.registered_agents[agent_name]
                
                # Record action
                action = {
                    "step": step["step_number"],
                    "agent": agent_name,
                    "intent": intent,
                    "timestamp": datetime.utcnow().isoformat()
                }
                actions.append(action)
                trace_entry["actions"].append(action)

                # Handle agent request execution
                agent_response = agent.handle_request(plan["user_input"])

                # Process response
                if agent_response.get("status") == "success":
                    step_status = "completed"
                    print(f"    ✓ Status: Completed")
                else:
                    step_status = "pending_tool_execution"
                    print(f"    ⏳ Status: Awaiting tools")

                # Record result
                result = {
                    "step": step["step_number"],
                    "agent": agent_name,
                    "status": step_status,
                    "data": agent_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                results.append(result)
                trace_entry["results"].append(result)

                step_result = {
                    "step_number": step["step_number"],
                    "agent": agent_name,
                    "status": step_status,
                    "message": agent_response.get("message", "")
                }
            else:
                step_result = {
                    "step_number": step["step_number"],
                    "agent": agent_name,
                    "status": "failed",
                    "error": f"Agent {agent_name} not registered"
                }

            step_results.append(step_result)

        # Structured response format
        structured_response = {
            "status": "success",
            "workflow_id": workflow_id,
            "actions": actions,
            "results": results,
            "step_results": step_results,
            "total_steps": len(plan["steps"]),
            "message": f"Workflow completed: {len(actions)} actions, {len(results)} results"
        }

        # Store in execution trace
        trace_entry["summary"] = structured_response["message"]
        self.execution_trace.append(trace_entry)

        # Store in memory
        self._add_to_memory({
            "workflow_id": workflow_id,
            "user_input": plan["user_input"],
            "intents": plan["intents"],
            "actions_count": len(actions),
            "timestamp": datetime.utcnow().isoformat()
        })

        return structured_response

    def _generate_workflow_id(self) -> str:
        """
        Generate a unique workflow ID.

        Returns:
            Workflow ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        workflow_num = len(self.execution_trace) + 1
        return f"WF-{timestamp}-{workflow_num:03d}"

    def _add_to_memory(self, interaction: Dict[str, Any]) -> None:
        """
        Add interaction to memory, maintaining max size.

        Args:
            interaction: Interaction data to store
        """
        self.interactions_memory.append(interaction)
        
        # Keep only recent interactions
        if len(self.interactions_memory) > self.max_memory:
            self.interactions_memory = self.interactions_memory[-self.max_memory:]

    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve interaction memory.

        Args:
            limit: Optional limit on records to return

        Returns:
            List of recent interactions
        """
        if limit:
            return self.interactions_memory[-limit:]
        return self.interactions_memory

    def get_execution_trace(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution trace for a specific workflow or all.

        Args:
            workflow_id: Optional specific workflow to trace

        Returns:
            Execution trace entries
        """
        if workflow_id:
            return [t for t in self.execution_trace if t["workflow_id"] == workflow_id]
        return self.execution_trace

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
            "workflows_executed": len(self.execution_trace),
            "memory_size": len(self.interactions_memory),
            "max_memory": self.max_memory,
            "execution_history_count": len(self.execution_history),
            "agent_details": {
                name: agent.get_agent_info()
                for name, agent in self.registered_agents.items()
            }
        }
