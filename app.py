"""
Main Application Entry Point for Personalized Learning Path Generator.

This module provides:
- App configuration with resumability for long-running operations
- Session management (in-memory for dev, database for production)
- Memory Bank integration for student data persistence
- Runner setup for agent execution
"""

import asyncio
import os
import uuid
from typing import Optional

from google.adk.apps.app import App, ResumabilityConfig, EventsCompactionConfig
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types

from .agents.coordinator_agent import coordinator_agent
from .memory.student_memory import StudentMemoryManager
from .observability.logging_config import setup_logging, get_logger, AgentLogger, SessionLogger
from .observability.metrics_collector import get_metrics


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

APP_NAME = "personalized_learning"
DEFAULT_USER_ID = "student"


class PersonalizedLearningApp:
    """
    Main application class for the Personalized Learning Path Generator.
    
    Manages:
    - App lifecycle
    - Session management
    - Memory services
    - Agent execution
    - Observability
    """
    
    def __init__(
        self,
        use_database: bool = True,
        database_url: str = "sqlite+aiosqlite:///learning_data.db",
        enable_resumability: bool = True,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        """
        Initialize the application.
        
        Args:
            use_database: If True, use database for session persistence
            database_url: Database URL for production use
            enable_resumability: Enable pause/resume for long-running operations
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        # Setup logging
        self.logger = setup_logging(level=log_level, log_file=log_file)
        self.agent_logger = AgentLogger("coordinator")
        self.session_logger = SessionLogger()
        self.metrics = get_metrics()
        
        # Session service
        if use_database:
            self.session_service = DatabaseSessionService(db_url=database_url)
            self.logger.info(f"Using database session service: {database_url}")
        else:
            self.session_service = InMemorySessionService()
            self.logger.info("Using in-memory session service")
            
        # Memory service
        self.memory_service = InMemoryMemoryService()
        self.memory_manager = StudentMemoryManager(self.memory_service)
        
        # Create the ADK App with resumability
        self.app = App(
            name=APP_NAME,
            root_agent=coordinator_agent,
            resumability_config=ResumabilityConfig(
                is_resumable=enable_resumability
            ) if enable_resumability else None,
            events_compaction_config=EventsCompactionConfig(
                compaction_interval=10,  # Compact every 10 invocations
                overlap_size=2,  # Keep 2 previous turns for context
            ),
        )
        
        # Create the runner
        self.runner = Runner(
            app=self.app,
            session_service=self.session_service,
            memory_service=self.memory_service,
        )
        
        self.logger.info("Personalized Learning App initialized successfully")
        
    async def create_session(
        self,
        user_id: str = DEFAULT_USER_ID,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Create a new session for a student.
        
        Args:
            user_id: Student's unique identifier
            session_id: Optional session ID (auto-generated if not provided)
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            
        await self.session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        
        self.session_logger.log_session_created(session_id, user_id)
        return session_id
        
    async def chat(
        self,
        message: str,
        user_id: str = DEFAULT_USER_ID,
        session_id: Optional[str] = None,
    ):
        """
        Send a message to the learning path generator.
        
        Args:
            message: User's message/query
            user_id: Student's unique identifier
            session_id: Session ID (creates new if not exists)
            
        Yields:
            Response events from the agent
        """
        # Create session if needed
        if session_id is None:
            session_id = await self.create_session(user_id)
        else:
            try:
                await self.session_service.get_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_id,
                )
            except:
                await self.create_session(user_id, session_id)
                
        # Log the invocation
        self.agent_logger.log_invocation(message, session_id)
        self.metrics.start_timer("request")
        
        # Format the message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
        
        # Run the agent
        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message,
            ):
                yield event
                
            # Record success metrics
            duration = self.metrics.stop_timer("request")
            self.metrics.record_agent_invocation("coordinator", success=True)
            
        except Exception as e:
            self.agent_logger.log_error(e, f"Session: {session_id}")
            self.metrics.record_agent_invocation("coordinator", success=False)
            raise
            
    async def resume_with_approval(
        self,
        session_id: str,
        user_id: str,
        approval_id: str,
        invocation_id: str,
        approved: bool,
    ):
        """
        Resume a paused operation with approval decision.
        
        Args:
            session_id: Session ID
            user_id: User ID
            approval_id: The approval request ID
            invocation_id: The invocation to resume
            approved: Whether the request is approved
            
        Yields:
            Response events from the resumed agent
        """
        self.agent_logger.log_resume(approval_id, approved)
        self.metrics.start_timer("approval_resume")
        
        # Create the confirmation response
        confirmation_response = types.FunctionResponse(
            id=approval_id,
            name="adk_request_confirmation",
            response={"confirmed": approved}
        )
        
        approval_message = types.Content(
            role="user",
            parts=[types.Part(function_response=confirmation_response)]
        )
        
        # Resume the agent
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=approval_message,
            invocation_id=invocation_id,
        ):
            yield event
            
        duration = self.metrics.stop_timer("approval_resume")
        self.metrics.record_approval_decision(approved, duration)
        
    async def save_session_to_memory(
        self,
        user_id: str,
        session_id: str,
    ):
        """
        Save a session to long-term memory.
        
        Args:
            user_id: User ID
            session_id: Session ID
        """
        session = await self.session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        await self.memory_manager.save_session_to_memory(session)
        self.logger.info(f"Session {session_id} saved to memory")
        
    def get_metrics_summary(self):
        """Get summary of collected metrics."""
        return self.metrics.get_summary()


# ============================================================================
# QUICK START RUNNER (For development/testing)
# ============================================================================

async def run_interactive_session():
    """Run an interactive session with the learning path generator."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           🎓 PERSONALIZED LEARNING PATH GENERATOR 🎓                         ║
║                                                                              ║
║   An AI-powered system that creates personalized learning paths             ║
║   tailored to your learning style, goals, and current knowledge.            ║
║                                                                              ║
║   Type 'quit' or 'exit' to end the session.                                 ║
║   Type 'metrics' to see performance metrics.                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize the app WITH DATABASE for session persistence
    app = PersonalizedLearningApp(
        use_database=True,  # Creates learning_data.db for session/state persistence
        log_level="INFO",
    )
    
    user_id = "interactive_student"
    session_id = await app.create_session(user_id)
    
    print(f"\n📋 Session started: {session_id}\n")
    print("💡 Try: 'I want to learn Python programming. I'm a complete beginner.'\n")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 Thank you for using the Personalized Learning Path Generator!")
                print("   Your learning journey awaits! 🚀\n")
                break
                
            if user_input.lower() == "metrics":
                print("\n📊 Metrics Summary:")
                print(app.get_metrics_summary())
                continue
                
            print("\n🤖 Assistant: ", end="", flush=True)
            
            async for event in app.chat(user_input, user_id, session_id):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
                            
            print()  # New line after response
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    asyncio.run(run_interactive_session())

