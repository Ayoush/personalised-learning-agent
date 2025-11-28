"""
Logging Configuration for Personalized Learning Path Generator.

Provides structured logging with different levels for debugging,
monitoring, and production use.
"""

import logging
import sys
from datetime import datetime
from typing import Optional


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    include_timestamp: bool = True,
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs
        include_timestamp: Whether to include timestamps in log messages
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("personalized_learning")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if include_timestamp:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            "%(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "personalized_learning") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (will be prefixed with 'personalized_learning.')
        
    Returns:
        Logger instance
    """
    if not name.startswith("personalized_learning"):
        name = f"personalized_learning.{name}"
    return logging.getLogger(name)


# ============================================================================
# AGENT LOGGING UTILITIES
# ============================================================================

class AgentLogger:
    """
    Specialized logger for agent operations.
    
    Provides structured logging for:
    - Agent invocations
    - Tool calls
    - Decision points
    - Errors and exceptions
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize agent logger.
        
        Args:
            agent_name: Name of the agent being logged
        """
        self.logger = get_logger(f"agent.{agent_name}")
        self.agent_name = agent_name
        
    def log_invocation(self, user_input: str, session_id: str):
        """Log the start of an agent invocation."""
        self.logger.info(
            f"🚀 Agent invoked | Session: {session_id} | Input: {user_input[:100]}..."
        )
        
    def log_tool_call(self, tool_name: str, params: dict):
        """Log a tool call made by the agent."""
        self.logger.debug(
            f"🔧 Tool called: {tool_name} | Params: {params}"
        )
        
    def log_tool_result(self, tool_name: str, result: dict):
        """Log the result of a tool call."""
        status = result.get("status", "unknown")
        self.logger.debug(
            f"✅ Tool result: {tool_name} | Status: {status}"
        )
        
    def log_decision(self, decision: str, reasoning: str = ""):
        """Log a decision point in agent reasoning."""
        self.logger.info(
            f"🤔 Decision: {decision}" + (f" | Reasoning: {reasoning}" if reasoning else "")
        )
        
    def log_delegation(self, target_agent: str, task: str):
        """Log delegation to another agent."""
        self.logger.info(
            f"📤 Delegating to {target_agent} | Task: {task}"
        )
        
    def log_response(self, response_preview: str):
        """Log the agent's final response."""
        self.logger.info(
            f"📝 Response generated | Preview: {response_preview[:100]}..."
        )
        
    def log_error(self, error: Exception, context: str = ""):
        """Log an error with context."""
        self.logger.error(
            f"❌ Error: {str(error)} | Context: {context}",
            exc_info=True
        )
        
    def log_warning(self, message: str):
        """Log a warning."""
        self.logger.warning(f"⚠️ {message}")
        
    def log_pause(self, reason: str, confirmation_id: str):
        """Log when agent pauses for approval."""
        self.logger.info(
            f"⏸️ Execution paused | Reason: {reason} | Confirmation ID: {confirmation_id}"
        )
        
    def log_resume(self, confirmation_id: str, approved: bool):
        """Log when agent resumes from pause."""
        status = "approved" if approved else "rejected"
        self.logger.info(
            f"▶️ Execution resumed | Confirmation ID: {confirmation_id} | Status: {status}"
        )


# ============================================================================
# SESSION LOGGING
# ============================================================================

class SessionLogger:
    """Logger for session-level events."""
    
    def __init__(self):
        self.logger = get_logger("session")
        
    def log_session_created(self, session_id: str, user_id: str):
        """Log session creation."""
        self.logger.info(
            f"📋 Session created | ID: {session_id} | User: {user_id}"
        )
        
    def log_session_resumed(self, session_id: str):
        """Log session resumption."""
        self.logger.info(f"🔄 Session resumed | ID: {session_id}")
        
    def log_session_ended(self, session_id: str, duration_seconds: float):
        """Log session end."""
        self.logger.info(
            f"🏁 Session ended | ID: {session_id} | Duration: {duration_seconds:.2f}s"
        )
        
    def log_state_update(self, session_id: str, key: str, value_preview: str):
        """Log state updates."""
        self.logger.debug(
            f"💾 State updated | Session: {session_id} | Key: {key} | Value: {value_preview[:50]}..."
        )

