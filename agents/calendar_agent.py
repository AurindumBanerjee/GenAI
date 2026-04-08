"""
Calendar Agent - Manages event scheduling and conflict detection.
Handles calendar operations and event management.
Integrates with CalendarTool for database operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent, AgentRole, AgentStatus
from tools.calendar_tool import CalendarTool


class CalendarAgent(BaseAgent):
    """
    Specialized agent for managing calendar events.
    Responsibilities:
    - Schedule events
    - Check for scheduling conflicts
    - Retrieve event information
    - Manage participant lists
    """

    def __init__(self):
        """Initialize the calendar agent."""
        super().__init__(
            name="CalendarAgent",
            role=AgentRole.CALENDAR_MANAGER,
            description="Manages calendar events, scheduling, and conflict detection"
        )

    def handle_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle calendar-related requests.

        Args:
            user_input: User's natural language input about events
            context: Optional context with database session or event data

        Returns:
            Dictionary with calendar operation result
        """
        self.set_status(AgentStatus.PROCESSING)

        try:
            # Determine calendar operation type
            operation = self._determine_operation(user_input)

            response = {
                "status": "success",
                "operation": operation,
                "message": f"Calendar operation '{operation}' parsed successfully",
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
        Determine which calendar operation to perform.

        Args:
            user_input: User input string

        Returns:
            Operation type: 'schedule', 'check_conflicts', 'get', 'list', or 'unknown'
        """
        user_lower = user_input.lower()

        if any(kw in user_lower for kw in ["schedule", "create event", "book", "set meeting"]):
            return "schedule"
        elif any(kw in user_lower for kw in ["conflict", "check", "available", "free"]):
            return "check_conflicts"
        elif any(kw in user_lower for kw in ["get", "show", "find", "retrieve"]):
            return "get"
        elif any(kw in user_lower for kw in ["list", "all events", "show all"]):
            return "list"
        else:
            return "unknown"

    def schedule_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        participants: Optional[List[str]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        check_conflicts: bool = True
    ) -> Dict[str, Any]:
        """
        Schedule a new event using CalendarTool.

        Args:
            title: Event title
            start_time: Event start time
            end_time: Event end time
            participants: List of participant email addresses or names
            location: Event location
            description: Event description
            check_conflicts: Whether to check for scheduling conflicts

        Returns:
            Dictionary with event data and scheduling status
        """
        return CalendarTool.schedule_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            participants=participants,
            location=location,
            description=description,
            check_conflicts=check_conflicts
        )

    def check_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        participant_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for scheduling conflicts in the given time slot using CalendarTool.

        Args:
            start_time: Start time to check
            end_time: End time to check
            participant_email: Optional specific participant to check

        Returns:
            Dictionary with conflict information
        """
        return CalendarTool.check_availability(start_time, end_time, participant_email)

    def get_event(self, event_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific event by ID using CalendarTool.

        Args:
            event_id: Event ID to retrieve

        Returns:
            Dictionary with event details
        """
        return CalendarTool.get_event(event_id)

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        participant: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve events with optional filtering using CalendarTool.

        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            participant: Optional participant email to filter
            limit: Maximum number of events to return

        Returns:
            Dictionary with event results
        """
        return CalendarTool.list_events(start_date, end_date, limit)

    def get_available_slots(
        self,
        date: datetime,
        duration_minutes: int = 30,
        participant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find available time slots on a given date using CalendarTool.

        Args:
            date: Date to find available slots for
            duration_minutes: Required duration of the slot
            participant: Optional specific participant

        Returns:
            Dictionary with available time slots
        """
        # Get all events for the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        events_result = CalendarTool.list_events(start_of_day, end_of_day)
        events = events_result.get("data", [])
        
        # Find gaps
        busy_times = [(datetime.fromisoformat(e["start_time"]), 
                      datetime.fromisoformat(e["end_time"])) for e in events]
        
        available_slots = []
        current_time = start_of_day
        
        for busy_start, busy_end in sorted(busy_times):
            if (busy_start - current_time).total_seconds() >= duration_minutes * 60:
                available_slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": busy_start.isoformat(),
                    "duration_minutes": int((busy_start - current_time).total_seconds() / 60)
                })
            current_time = max(current_time, busy_end)
        
        # Add final slot if available
        if (end_of_day - current_time).total_seconds() >= duration_minutes * 60:
            available_slots.append({
                "start_time": current_time.isoformat(),
                "end_time": end_of_day.isoformat(),
                "duration_minutes": int((end_of_day - current_time).total_seconds() / 60)
            })
        
        return {
            "status": "success",
            "action": "get_available_slots",
            "data": available_slots,
            "count": len(available_slots),
            "date": date.isoformat(),
            "required_duration": duration_minutes,
            "message": f"Found {len(available_slots)} available slots"
        }

    def add_participant(self, event_id: int, participant_email: str) -> Dict[str, Any]:
        """
        Add a participant to an existing event using CalendarTool.

        Args:
            event_id: Event ID
            participant_email: Email of participant to add

        Returns:
            Dictionary with update status
        """
        return CalendarTool.add_participant(event_id, participant_email)