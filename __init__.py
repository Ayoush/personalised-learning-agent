"""
Personalized Learning Path Generator

An AI-powered multi-agent system that creates personalized learning paths
by analyzing student profiles, learning styles, and goals.

Main Features:
- Multi-agent architecture (Sequential, Parallel, Loop patterns)
- Custom tools for learning analysis
- Long-running operations with teacher approval
- Session management and Memory Bank
- Comprehensive observability

Usage:
    # Run with ADK CLI
    adk run personalized_learning
    
    # Run web interface
    adk web personalized_learning
    
    # Run interactive session
    python -m personalized_learning.app
"""

import os
from pathlib import Path
from google.adk.apps.app import App, ResumabilityConfig, EventsCompactionConfig
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import InMemoryMemoryService

from .agent import root_agent
from .app import PersonalizedLearningApp

# Create database path in the same directory as this file
_db_path = Path(__file__).parent / "learning_sessions.db"
db_url = f"sqlite+aiosqlite:///{_db_path}"  # Use async SQLite driver

# Create App with DatabaseSessionService for persistent storage
# This is what ADK web will use
app = App(
    name="personalized_learning",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(
        is_resumable=True  # Enable long-running operations (teacher approval)
    ),
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,  # Compact every 10 invocations
        overlap_size=2,  # Keep 2 previous turns for context
    ),
)

# Create session service with database persistence
session_service = DatabaseSessionService(db_url=db_url)

# Create memory service
memory_service = InMemoryMemoryService()

__version__ = "1.0.0"
__all__ = ["root_agent", "app", "session_service", "memory_service", "PersonalizedLearningApp"]
