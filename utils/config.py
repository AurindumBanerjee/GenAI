"""
Configuration and environment variables for the multi-agent system.
"""

import os
from typing import Optional


class Config:
    """
    Central configuration class for the application.
    """

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/app.db"
    )

    # Application Settings
    APP_NAME: str = "Multi-Agent System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Agent Configuration
    DEFAULT_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3
    AGENT_LOG_LEVEL: str = os.getenv("AGENT_LOG_LEVEL", "INFO")

    # Tool Configuration (placeholder for future integrations)
    ENABLE_CALENDAR_SYNC: bool = os.getenv("ENABLE_CALENDAR_SYNC", "False").lower() == "true"
    ENABLE_EMAIL_INTEGRATION: bool = os.getenv("ENABLE_EMAIL_INTEGRATION", "False").lower() == "true"
    ENABLE_SEMANTIC_SEARCH: bool = os.getenv("ENABLE_SEMANTIC_SEARCH", "False").lower() == "true"

    # Orchestrator Configuration
    ORCHESTRATOR_MODEL: str = os.getenv("ORCHESTRATOR_MODEL", "default")
    MAX_PARALLEL_AGENTS: int = 5
    WORKFLOW_MAX_STEPS: int = 10

    @classmethod
    def get_database_url(cls) -> str:
        """Get the database URL from configuration."""
        return cls.DATABASE_URL

    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if application is in debug mode."""
        return cls.DEBUG

    @classmethod
    def to_dict(cls) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary of all configuration values
        """
        return {
            "APP_NAME": cls.APP_NAME,
            "APP_VERSION": cls.APP_VERSION,
            "DEBUG": cls.DEBUG,
            "DATABASE_URL": cls.DATABASE_URL,
            "AGENT_LOG_LEVEL": cls.AGENT_LOG_LEVEL,
            "DEFAULT_TIMEOUT": cls.DEFAULT_TIMEOUT,
            "MAX_RETRIES": cls.MAX_RETRIES,
        }


# Application Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
