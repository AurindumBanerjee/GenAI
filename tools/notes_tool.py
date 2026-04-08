"""
Notes Tool - MCP-style tool for notes operations.
Handles note creation, retrieval, searching, and tagging.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from db import get_db_manager, Note
from sqlalchemy.orm import Session
from utils.schemas import NoteResponse


class NotesTool:
    """
    MCP-style tool for note management.
    All methods accept structured input and return JSON output.
    Supports keyword search (with embedding support for future).
    """

    @staticmethod
    def create_note(
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new note.

        Args:
            content: Note content (required)
            title: Note title (optional)
            tags: List of tags for organization

        Returns:
            Dictionary with created note or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                new_note = Note(
                    title=title or f"Note created at {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    content=content,
                    tags=tags or []
                )
                session.add(new_note)
                session.flush()

                response = NoteResponse(
                    id=new_note.id,
                    title=new_note.title,
                    content=new_note.content,
                    tags=new_note.tags,
                    embedding=new_note.embedding,
                    created_at=new_note.created_at,
                    updated_at=new_note.updated_at
                )

                return {
                    "status": "success",
                    "action": "create_note",
                    "data": response.model_dump(),
                    "message": f"Note created: {new_note.title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "create_note",
                "error": str(e),
                "message": f"Failed to create note: {str(e)}"
            }

    @staticmethod
    def search_notes(
        query: str,
        search_type: str = "keyword",
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search notes by keyword or tags.

        Args:
            query: Search query string
            search_type: "keyword" or "semantic" (semantic ready for future)
            tags: Optional tags to filter by
            limit: Maximum number of results

        Returns:
            Dictionary with search results or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                base_query = session.query(Note)

                # Filter by tags if provided
                if tags:
                    # Filter notes that have ALL specified tags
                    for tag in tags:
                        base_query = base_query.filter(Note.tags.contains([tag]))

                # Search by keyword
                if search_type == "keyword":
                    query_lower = f"%{query.lower()}%"
                    results = base_query.filter(
                        (Note.content.ilike(query_lower)) |
                        (Note.title.ilike(query_lower))
                    ).limit(limit).all()
                else:
                    # Semantic search placeholder (future with embeddings)
                    results = base_query.limit(limit).all()

                note_list = [
                    NoteResponse(
                        id=n.id,
                        title=n.title,
                        content=n.content,
                        tags=n.tags,
                        embedding=n.embedding,
                        created_at=n.created_at,
                        updated_at=n.updated_at
                    ).model_dump()
                    for n in results
                ]

                return {
                    "status": "success",
                    "action": "search_notes",
                    "data": note_list,
                    "count": len(note_list),
                    "search_type": search_type,
                    "query": query,
                    "message": f"Found {len(note_list)} notes"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "search_notes",
                "error": str(e),
                "message": f"Failed to search notes: {str(e)}"
            }

    @staticmethod
    def get_note(note_id: int) -> Dict[str, Any]:
        """
        Get a specific note by ID.

        Args:
            note_id: Note ID to retrieve

        Returns:
            Dictionary with note data or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    return {
                        "status": "error",
                        "action": "get_note",
                        "error": "Note not found",
                        "message": f"Note {note_id} not found"
                    }

                response = NoteResponse(
                    id=note.id,
                    title=note.title,
                    content=note.content,
                    tags=note.tags,
                    embedding=note.embedding,
                    created_at=note.created_at,
                    updated_at=note.updated_at
                )

                return {
                    "status": "success",
                    "action": "get_note",
                    "data": response.model_dump(),
                    "message": f"Retrieved note {note_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "get_note",
                "error": str(e),
                "message": f"Failed to get note: {str(e)}"
            }

    @staticmethod
    def list_notes(
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List notes with optional filtering.

        Args:
            tags: Filter by tags
            date_from: Filter from date
            date_to: Filter until date
            limit: Maximum number of notes to return

        Returns:
            Dictionary with list of notes or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                query = session.query(Note)

                # Filter by tags
                if tags:
                    for tag in tags:
                        query = query.filter(Note.tags.contains([tag]))

                # Filter by date range
                if date_from:
                    query = query.filter(Note.created_at >= date_from)
                if date_to:
                    query = query.filter(Note.created_at <= date_to)

                notes = query.order_by(Note.created_at.desc()).limit(limit).all()

                note_list = [
                    NoteResponse(
                        id=n.id,
                        title=n.title,
                        content=n.content,
                        tags=n.tags,
                        embedding=n.embedding,
                        created_at=n.created_at,
                        updated_at=n.updated_at
                    ).model_dump()
                    for n in notes
                ]

                return {
                    "status": "success",
                    "action": "list_notes",
                    "data": note_list,
                    "count": len(note_list),
                    "message": f"Retrieved {len(note_list)} notes"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "list_notes",
                "error": str(e),
                "message": f"Failed to list notes: {str(e)}"
            }

    @staticmethod
    def add_tag(note_id: int, tag: str) -> Dict[str, Any]:
        """
        Add a tag to a note.

        Args:
            note_id: Note ID
            tag: Tag to add

        Returns:
            Dictionary with updated note or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    return {
                        "status": "error",
                        "action": "add_tag",
                        "error": "Note not found",
                        "message": f"Note {note_id} not found"
                    }

                if tag not in note.tags:
                    note.tags.append(tag)
                    session.flush()

                response = NoteResponse(
                    id=note.id,
                    title=note.title,
                    content=note.content,
                    tags=note.tags,
                    embedding=note.embedding,
                    created_at=note.created_at,
                    updated_at=note.updated_at
                )

                return {
                    "status": "success",
                    "action": "add_tag",
                    "data": response.model_dump(),
                    "message": f"Tag '{tag}' added to note {note_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "add_tag",
                "error": str(e),
                "message": f"Failed to add tag: {str(e)}"
            }

    @staticmethod
    def remove_tag(note_id: int, tag: str) -> Dict[str, Any]:
        """
        Remove a tag from a note.

        Args:
            note_id: Note ID
            tag: Tag to remove

        Returns:
            Dictionary with updated note or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    return {
                        "status": "error",
                        "action": "remove_tag",
                        "error": "Note not found",
                        "message": f"Note {note_id} not found"
                    }

                if tag in note.tags:
                    note.tags.remove(tag)
                    session.flush()

                response = NoteResponse(
                    id=note.id,
                    title=note.title,
                    content=note.content,
                    tags=note.tags,
                    embedding=note.embedding,
                    created_at=note.created_at,
                    updated_at=note.updated_at
                )

                return {
                    "status": "success",
                    "action": "remove_tag",
                    "data": response.model_dump(),
                    "message": f"Tag '{tag}' removed from note {note_id}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "remove_tag",
                "error": str(e),
                "message": f"Failed to remove tag: {str(e)}"
            }

    @staticmethod
    def get_notes_by_tag(tag: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get all notes with a specific tag.

        Args:
            tag: Tag to filter by
            limit: Maximum number of notes

        Returns:
            Dictionary with filtered notes or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                notes = session.query(Note).filter(
                    Note.tags.contains([tag])
                ).order_by(Note.created_at.desc()).limit(limit).all()

                note_list = [
                    NoteResponse(
                        id=n.id,
                        title=n.title,
                        content=n.content,
                        tags=n.tags,
                        embedding=n.embedding,
                        created_at=n.created_at,
                        updated_at=n.updated_at
                    ).model_dump()
                    for n in notes
                ]

                return {
                    "status": "success",
                    "action": "get_notes_by_tag",
                    "data": note_list,
                    "count": len(note_list),
                    "tag": tag,
                    "message": f"Found {len(note_list)} notes with tag '{tag}'"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "get_notes_by_tag",
                "error": str(e),
                "message": f"Failed to get notes by tag: {str(e)}"
            }

    @staticmethod
    def delete_note(note_id: int) -> Dict[str, Any]:
        """
        Delete a note.

        Args:
            note_id: Note ID to delete

        Returns:
            Dictionary with deletion status or error
        """
        try:
            db = get_db_manager()
            with db.session_scope() as session:
                note = session.query(Note).filter(Note.id == note_id).first()

                if not note:
                    return {
                        "status": "error",
                        "action": "delete_note",
                        "error": "Note not found",
                        "message": f"Note {note_id} not found"
                    }

                title = note.title
                session.delete(note)

                return {
                    "status": "success",
                    "action": "delete_note",
                    "data": {"deleted_id": note_id},
                    "message": f"Note deleted: {title}"
                }

        except Exception as e:
            return {
                "status": "error",
                "action": "delete_note",
                "error": str(e),
                "message": f"Failed to delete note: {str(e)}"
            }
