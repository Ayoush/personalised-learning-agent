"""
Student Memory Manager

Manages long-term memory for student learning data, preferences,
and progress tracking using ADK's Memory Bank.
"""

from typing import Any, Dict, List, Optional
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import Session


class StudentMemoryManager:
    """
    Manages student learning data across sessions.
    
    Provides functionality for:
    - Storing learning preferences and styles
    - Tracking learning progress
    - Retrieving historical data for personalization
    - Managing learning path history
    """
    
    def __init__(self, memory_service: Optional[InMemoryMemoryService] = None):
        """
        Initialize the StudentMemoryManager.
        
        Args:
            memory_service: ADK memory service instance. Creates new if not provided.
        """
        self.memory_service = memory_service or InMemoryMemoryService()
        
    async def save_session_to_memory(self, session: Session) -> None:
        """
        Save a completed session to long-term memory.
        
        This allows the agent to recall information from past conversations.
        
        Args:
            session: The session to save to memory
        """
        await self.memory_service.add_session_to_memory(session)
        
    async def search_student_history(
        self,
        app_name: str,
        user_id: str,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search student's learning history for relevant information.
        
        Args:
            app_name: Application name
            user_id: Student's unique identifier
            query: Search query (e.g., "What topics has the student learned?")
            
        Returns:
            List of relevant memory entries
        """
        search_response = await self.memory_service.search_memory(
            app_name=app_name,
            user_id=user_id,
            query=query,
        )
        
        memories = []
        for memory in search_response.memories:
            if memory.content and memory.content.parts:
                memories.append({
                    "author": memory.author,
                    "content": memory.content.parts[0].text if memory.content.parts else "",
                })
                
        return memories
    
    async def get_student_learning_style(
        self,
        app_name: str,
        user_id: str,
    ) -> Optional[str]:
        """
        Retrieve the student's known learning style from memory.
        
        Args:
            app_name: Application name
            user_id: Student's unique identifier
            
        Returns:
            Learning style string if found, None otherwise
        """
        results = await self.search_student_history(
            app_name=app_name,
            user_id=user_id,
            query="What is the student's learning style preference?",
        )
        
        # Extract learning style from results
        for result in results:
            content = result.get("content", "").lower()
            if "visual" in content:
                return "Visual"
            elif "auditory" in content:
                return "Auditory"
            elif "reading" in content or "writing" in content:
                return "Reading/Writing"
            elif "kinesthetic" in content:
                return "Kinesthetic"
                
        return None
    
    async def get_completed_topics(
        self,
        app_name: str,
        user_id: str,
    ) -> List[str]:
        """
        Get list of topics the student has previously learned.
        
        Args:
            app_name: Application name
            user_id: Student's unique identifier
            
        Returns:
            List of completed topic names
        """
        results = await self.search_student_history(
            app_name=app_name,
            user_id=user_id,
            query="What topics has the student completed or learned?",
        )
        
        # This would need more sophisticated parsing in production
        topics = []
        for result in results:
            content = result.get("content", "")
            # Simple extraction - in production, use NLP
            if "completed" in content.lower() or "learned" in content.lower():
                topics.append(content[:100])  # Truncate for summary
                
        return topics
    
    async def get_learning_preferences(
        self,
        app_name: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Compile comprehensive learning preferences from memory.
        
        Args:
            app_name: Application name
            user_id: Student's unique identifier
            
        Returns:
            Dictionary of learning preferences
        """
        preferences = {
            "learning_style": await self.get_student_learning_style(app_name, user_id),
            "completed_topics": await self.get_completed_topics(app_name, user_id),
            "preferred_resources": [],
            "study_schedule": None,
        }
        
        # Search for additional preferences
        resource_results = await self.search_student_history(
            app_name=app_name,
            user_id=user_id,
            query="What types of resources does the student prefer?",
        )
        
        for result in resource_results:
            content = result.get("content", "").lower()
            if "video" in content:
                preferences["preferred_resources"].append("videos")
            if "article" in content or "reading" in content:
                preferences["preferred_resources"].append("articles")
            if "practice" in content or "exercise" in content:
                preferences["preferred_resources"].append("practice")
                
        return preferences


# ============================================================================
# MEMORY TOOL FUNCTIONS (for use with agents)
# ============================================================================

async def remember_student_preference(
    memory_manager: StudentMemoryManager,
    session: Session,
    preference_type: str,
    preference_value: str,
) -> Dict[str, Any]:
    """
    Store a student preference in long-term memory.
    
    Args:
        memory_manager: StudentMemoryManager instance
        session: Current session
        preference_type: Type of preference (e.g., "learning_style", "pace")
        preference_value: The preference value
        
    Returns:
        Status dictionary
    """
    # In production, you'd store this more structured way
    await memory_manager.save_session_to_memory(session)
    
    return {
        "status": "success",
        "message": f"Remembered {preference_type}: {preference_value}",
    }


async def recall_student_info(
    memory_manager: StudentMemoryManager,
    app_name: str,
    user_id: str,
    query: str,
) -> Dict[str, Any]:
    """
    Recall student information from long-term memory.
    
    Args:
        memory_manager: StudentMemoryManager instance
        app_name: Application name
        user_id: Student ID
        query: What to recall
        
    Returns:
        Retrieved information
    """
    results = await memory_manager.search_student_history(
        app_name=app_name,
        user_id=user_id,
        query=query,
    )
    
    if results:
        return {
            "status": "success",
            "memories": results,
        }
    else:
        return {
            "status": "not_found",
            "message": "No relevant memories found.",
        }

