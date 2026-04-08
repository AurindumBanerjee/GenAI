"""
Notes Agent - Manages note creation, retrieval, and semantic search.
Handles all note-related operations for the system.
Integrates with NotesTool for database operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentRole, AgentStatus
from tools.notes_tool import NotesTool


class NotesAgent(BaseAgent):
    """
    Specialized agent for managing notes.
    Responsibilities:
    - Create and store notes
    - Retrieve notes with filtering
    - Search notes by content or tags
    - Manage note metadata and tags
    - Support for semantic search (future embedding integration)
    """

    def __init__(self):
        """Initialize the notes agent."""
        super().__init__(
            name="NotesAgent",
            role=AgentRole.NOTE_MANAGER,
            description="Manages note creation, retrieval, searching, and tagging"
        )

    def handle_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle note-related requests.

        Args:
            user_input: User's natural language input about notes
            context: Optional context with database session or note data

        Returns:
            Dictionary with note operation result
        """
        self.set_status(AgentStatus.PROCESSING)

        try:
            # Determine note operation type
            operation = self._determine_operation(user_input)

            response = {
                "status": "success",
                "operation": operation,
                "message": f"Note operation '{operation}' parsed successfully",
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
        Determine which note operation to perform.

        Args:
            user_input: User input string

        Returns:
            Operation type: 'create', 'search', 'get', 'list', 'tag', or 'unknown'
        """
        user_lower = user_input.lower()

        if any(kw in user_lower for kw in ["create", "add", "write", "save", "new note"]):
            return "create"
        elif any(kw in user_lower for kw in ["search", "find", "look for", "query"]):
            return "search"
        elif any(kw in user_lower for kw in ["get", "show", "retrieve"]):
            return "get"
        elif any(kw in user_lower for kw in ["list", "all notes", "show all"]):
            return "list"
        elif any(kw in user_lower for kw in ["tag", "label", "mark", "organize"]):
            return "tag"
        else:
            return "unknown"

    def create_note(
        self,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new note using NotesTool.

        Args:
            content: Note content/body
            title: Optional note title
            tags: Optional list of tags for organization

        Returns:
            Dictionary with note data and metadata
        """
        return NotesTool.create_note(content=content, title=title, tags=tags)

    def search_notes(
        self,
        query: str,
        search_type: str = "keyword",
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search notes by keyword or semantic similarity using NotesTool.

        Args:
            query: Search query string
            search_type: Type of search: 'keyword' or 'semantic' (embedding-based)
            tags: Optional tags to filter by
            limit: Maximum number of results

        Returns:
            Dictionary with search results
        """
        return NotesTool.search_notes(query=query, search_type=search_type, tags=tags, limit=limit)

    def get_note(self, note_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific note by ID using NotesTool.

        Args:
            note_id: Note ID to retrieve

        Returns:
            Dictionary with note details
        """
        return NotesTool.get_note(note_id)

    def get_notes(
        self,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve notes with optional filtering by tags and date range using NotesTool.

        Args:
            tags: Optional list of tags to filter by
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            limit: Maximum number of notes to return

        Returns:
            Dictionary with note results
        """
        return NotesTool.list_notes(tags=tags, date_from=date_from, date_to=date_to, limit=limit)

    def add_tag(self, note_id: int, tag: str) -> Dict[str, Any]:
        """
        Add a tag to an existing note using NotesTool.

        Args:
            note_id: Note ID
            tag: Tag to add

        Returns:
            Dictionary with update status
        """
        return NotesTool.add_tag(note_id, tag)

    def remove_tag(self, note_id: int, tag: str) -> Dict[str, Any]:
        """
        Remove a tag from a note using NotesTool.

        Args:
            note_id: Note ID
            tag: Tag to remove

        Returns:
            Dictionary with update status
        """
        return NotesTool.remove_tag(note_id, tag)

    def get_notes_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get all notes with a specific tag using NotesTool.

        Args:
            tag: Tag to filter by

        Returns:
            Dictionary with filtered notes
        """
        return NotesTool.get_notes_by_tag(tag)