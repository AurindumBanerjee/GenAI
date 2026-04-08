"""
Calendar Tool - MCP-style tool for calendar/event operations.
Handles event scheduling, conflict checking, and availability management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from db import get_db_manager, Event
from sqlalchemy.orm import Session
from utils.schemas import EventResponse


class CalendarTool:
    """
    MCP-style tool for calendar event management.
    All methods accept structured input and return JSON output.
    """

    @staticmethod
    def schedule_event(
        title: str,
        start_time: datetime,
        end_time: datetime,
        participants: Optional[List[str]] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        check_conflicts: bool = True
    ) -> Dict[str, Any]:
        """
        Schedule a new event.

        Args:
            title: Event title (required)
            start_time: Event start time (required)
            end_time: Event end time (required)
            participants: List of participant emails/names
            location: Event location
            description: Event description
            check_conflicts: Whether to check for conflicts

        Returns:
            Dictionary with created event or error/conflict info
        """
        try:
            # Check for conflicts if requested
            if check_conflicts:
                conflicts = CalendarTool.check_availability(
                    start_time, end_time
                )
                if conflicts["data"]:  # Found conflicts
                    return {
                        "status": "conflict",
                        "action": "schedule_event",
                        "message": f"Scheduling conflict detected",
                        "conflicts": conflicts["data"]
                    }

            db = get_db_manager()
            with db.session_scope() as session:
                new_event = Event(
                    title=title,
                    start_time=start_time,
                    end_time=end_time,
                    description=description,
                    participants=participants or [],
                    location=location
                )
                session.add(new_event)
                session.flush()

                response = EventResponse(
                    id=new_event.id,
                    title=new_event.title,
                    description=new_event.description,
                    start_time=new_event.start_time,
                    end_time=new_event.end_time,
                    participants=new_event.participants,
                    location=new_event.location,
                    created_at=new_event.created_at,
                    updated_at=new_event.updated_at
                )

                return {
                    "status": "success",
                    "action": "schedule_event",
                    "data": response.model_dump(),
                    "message": f"Event scheduled: {title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "schedule_event",
                "error": str(e),
                "message": f"Failed to schedule event: {str(e)}"
            }

    @staticmethod
    def check_availability(
        start_time: datetime,
        end_time: datetime,
        participant: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check for scheduling conflicts.

        Args:
            start_time: Start time to check
            end_time: End time to check
            participant: Optional specific participant to check

        Returns:
            Dictionary with conflicts or availability info
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                # Find overlapping events
                query = session.query(Event).filter(
                    Event.start_time < end_time,
                    Event.end_time > start_time
                )

                conflicts = query.all()

                conflict_list = [
                    {
                        "id": c.id,
                        "title": c.title,
                        "start_time": c.start_time.isoformat(),
                        "end_time": c.end_time.isoformat(),
                        "location": c.location
                    }
                    for c in conflicts
                ]

                return {
                    "status": "success",
                    "action": "check_availability",
                    "data": conflict_list,
                    "available": len(conflict_list) == 0,
                    "conflict_count": len(conflict_list),
                    "message": f"Found {len(conflict_list)} conflicts"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "check_availability",
                "error": str(e),
                "message": f"Failed to check availability: {str(e)}"
            }

    @staticmethod
    def get_event(event_id: int) -> Dict[str, Any]:
        """
        Get a specific event by ID.

        Args:
            event_id: Event ID to retrieve

        Returns:
            Dictionary with event data or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                event = session.query(Event).filter(Event.id == event_id).first()

                if not event:
                    return {
                        "status": "error",
                        "action": "get_event",
                        "error": "Event not found",
                        "message": f"Event {event_id} not found"
                    }

                response = EventResponse(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    participants=event.participants,
                    location=event.location,
                    created_at=event.created_at,
                    updated_at=event.updated_at
                )

                return {
                    "status": "success",
                    "action": "get_event",
                    "data": response.model_dump(),
                    "message": f"Retrieved event {event_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "get_event",
                "error": str(e),
                "message": f"Failed to get event: {str(e)}"
            }

    @staticmethod
    def list_events(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List events with optional date filtering.

        Args:
            start_date: Filter events from this date
            end_date: Filter events until this date
            limit: Maximum number of events to return

        Returns:
            Dictionary with list of events or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                query = session.query(Event)

                if start_date:
                    query = query.filter(Event.start_time >= start_date)
                if end_date:
                    query = query.filter(Event.end_time <= end_date)

                events = query.order_by(Event.start_time.asc()).limit(limit).all()

                event_list = [
                    EventResponse(
                        id=e.id,
                        title=e.title,
                        description=e.description,
                        start_time=e.start_time,
                        end_time=e.end_time,
                        participants=e.participants,
                        location=e.location,
                        created_at=e.created_at,
                        updated_at=e.updated_at
                    ).model_dump()
                    for e in events
                ]

                return {
                    "status": "success",
                    "action": "list_events",
                    "data": event_list,
                    "count": len(event_list),
                    "message": f"Retrieved {len(event_list)} events"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "list_events",
                "error": str(e),
                "message": f"Failed to list events: {str(e)}"
            }

    @staticmethod
    def add_participant(event_id: int, participant: str) -> Dict[str, Any]:
        """
        Add a participant to an event.

        Args:
            event_id: Event ID
            participant: Participant email/name

        Returns:
            Dictionary with updated event or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                event = session.query(Event).filter(Event.id == event_id).first()

                if not event:
                    return {
                        "status": "error",
                        "action": "add_participant",
                        "error": "Event not found",
                        "message": f"Event {event_id} not found"
                    }

                if participant not in event.participants:
                    event.participants.append(participant)
                    session.flush()

                response = EventResponse(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    participants=event.participants,
                    location=event.location,
                    created_at=event.created_at,
                    updated_at=event.updated_at
                )

                return {
                    "status": "success",
                    "action": "add_participant",
                    "data": response.model_dump(),
                    "message": f"Participant added to event {event_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "add_participant",
                "error": str(e),
                "message": f"Failed to add participant: {str(e)}"
            }

    @staticmethod
    def delete_event(event_id: int) -> Dict[str, Any]:
        """
        Delete an event.

        Args:
            event_id: Event ID to delete

        Returns:
            Dictionary with deletion status or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                event = session.query(Event).filter(Event.id == event_id).first()

                if not event:
                    return {
                        "status": "error",
                        "action": "delete_event",
                        "error": "Event not found",
                        "message": f"Event {event_id} not found"
                    }

                title = event.title
                session.delete(event)

                return {
                    "status": "success",
                    "action": "delete_event",
                    "data": {"deleted_id": event_id},
                    "message": f"Event deleted: {title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "delete_event",
                "error": str(e),
                "message": f"Failed to delete event: {str(e)}"
            }
