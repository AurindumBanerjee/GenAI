"""
Database connection and session management using SQLAlchemy.
Provides a singleton database instance for the application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from db.models import Base
import os


class DatabaseManager:
    """
    Manages SQLAlchemy database connections, sessions, and initialization.
    """

    def __init__(self, database_url: str = None):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL. Defaults to SQLite in-memory or file-based.
        """
        if database_url is None:
            # Use SQLite with a persistent file
            db_file = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            database_url = f"sqlite:///{db_file}"

        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        print("✓ Database tables initialized")

    def drop_all(self):
        """Drop all tables from the database (for testing/reset)."""
        Base.metadata.drop_all(bind=self.engine)
        print("✓ All database tables dropped")

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy Session instance
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions. Ensures proper cleanup.

        Yields:
            SQLAlchemy Session instance
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close all connections in the pool."""
        self.engine.dispose()


# Global database instance
_db_manager = None


def get_db_manager(database_url: str = None) -> DatabaseManager:
    """
    Get or initialize the global database manager.

    Args:
        database_url: SQLAlchemy database URL (only used on first call)

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url)
    return _db_manager


def init_database(database_url: str = None):
    """
    Initialize the database and create tables.

    Args:
        database_url: Optional SQLAlchemy database URL
    """
    db = get_db_manager(database_url)
    db.init_db()
