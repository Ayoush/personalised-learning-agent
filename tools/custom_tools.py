"""
Custom Tools for Personalized Learning Path Generator.

These tools provide functionality for:
- Analyzing student learning styles
- Calculating knowledge gaps
- Storing and retrieving learning paths
- Managing student profiles
"""

from typing import Any, Dict, Optional
from google.adk.tools import ToolContext


# ============================================================================
# LEARNING STYLE ANALYSIS TOOL
# ============================================================================

def analyze_learning_style(
    tool_context: ToolContext,
    student_responses: str,
    preferred_content_types: str = "",
    study_habits: str = "",
) -> Dict[str, Any]:
    """
    Analyzes student responses to determine their learning style.
    
    This tool evaluates student preferences and behaviors to classify them
    into learning style categories: Visual, Auditory, Reading/Writing, or Kinesthetic.
    
    Args:
        tool_context: ADK tool context for state management
        student_responses: Student's answers about their learning preferences
        preferred_content_types: Types of content the student prefers (videos, articles, etc.)
        study_habits: Description of student's study habits and patterns
        
    Returns:
        Dictionary containing:
        - primary_style: Main learning style (Visual/Auditory/Reading/Kinesthetic)
        - secondary_style: Secondary learning style
        - style_breakdown: Percentage breakdown of all styles
        - recommendations: Content type recommendations
    """
    
    # Keywords for learning style detection
    visual_keywords = ["diagram", "chart", "video", "image", "picture", "watch", "see", "visual", "color", "infographic"]
    auditory_keywords = ["listen", "audio", "podcast", "lecture", "discuss", "talk", "hear", "music", "explain verbally"]
    reading_keywords = ["read", "book", "article", "notes", "write", "text", "documentation", "manual", "blog"]
    kinesthetic_keywords = ["practice", "hands-on", "project", "build", "code", "experiment", "try", "do", "interactive"]
    
    # Combine all input for analysis
    full_text = f"{student_responses} {preferred_content_types} {study_habits}".lower()
    
    # Calculate scores
    scores = {
        "Visual": sum(1 for kw in visual_keywords if kw in full_text),
        "Auditory": sum(1 for kw in auditory_keywords if kw in full_text),
        "Reading/Writing": sum(1 for kw in reading_keywords if kw in full_text),
        "Kinesthetic": sum(1 for kw in kinesthetic_keywords if kw in full_text),
    }
    
    # Normalize scores to percentages
    total_score = sum(scores.values()) or 1
    style_breakdown = {style: round((score / total_score) * 100, 1) for style, score in scores.items()}
    
    # Determine primary and secondary styles
    sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_style = sorted_styles[0][0]
    secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 else primary_style
    
    # Content recommendations based on primary style
    recommendations = {
        "Visual": ["Video tutorials", "Infographics", "Diagrams", "Mind maps", "Flowcharts"],
        "Auditory": ["Podcasts", "Audio lectures", "Discussion groups", "Verbal explanations"],
        "Reading/Writing": ["Textbooks", "Articles", "Documentation", "Written notes", "Blogs"],
        "Kinesthetic": ["Hands-on projects", "Coding exercises", "Interactive labs", "Practice problems"],
    }
    
    result = {
        "status": "success",
        "primary_style": primary_style,
        "secondary_style": secondary_style,
        "style_breakdown": style_breakdown,
        "recommendations": recommendations.get(primary_style, []),
        "analysis_summary": f"Student shows a {primary_style} learning preference with {secondary_style} as secondary.",
    }
    
    # Store in session state for other agents to access
    tool_context.state["student:learning_style"] = primary_style
    tool_context.state["student:style_breakdown"] = style_breakdown
    tool_context.state["student:content_recommendations"] = recommendations.get(primary_style, [])
    
    return result


# ============================================================================
# KNOWLEDGE GAP CALCULATION TOOL
# ============================================================================

def calculate_knowledge_gap(
    tool_context: ToolContext,
    topic: str,
    current_knowledge: str,
    target_level: str = "intermediate",
    prior_experience: str = "",
) -> Dict[str, Any]:
    """
    Calculates the knowledge gap between current and target knowledge levels.
    
    This tool analyzes what a student currently knows and what they need to learn
    to reach their target proficiency level.
    
    Args:
        tool_context: ADK tool context for state management
        topic: The subject/topic being learned
        current_knowledge: Description of student's current knowledge
        target_level: Desired proficiency level (beginner/intermediate/advanced/expert)
        prior_experience: Any related experience the student has
        
    Returns:
        Dictionary containing:
        - gap_level: Overall gap severity (small/medium/large)
        - current_level: Estimated current proficiency
        - target_level: Target proficiency level
        - knowledge_gaps: List of specific gaps to address
        - prerequisite_topics: Topics that should be learned first
        - estimated_hours: Estimated learning hours
    """
    
    # Level hierarchy
    levels = ["beginner", "intermediate", "advanced", "expert"]
    level_scores = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    
    # Analyze current knowledge indicators
    current_text = f"{current_knowledge} {prior_experience}".lower()
    
    # Estimate current level based on keywords
    if any(word in current_text for word in ["expert", "professional", "years of experience", "advanced"]):
        current_level = "advanced"
    elif any(word in current_text for word in ["some experience", "familiar", "used before", "basic understanding"]):
        current_level = "intermediate"
    elif any(word in current_text for word in ["beginner", "new to", "no experience", "starting", "never"]):
        current_level = "beginner"
    else:
        current_level = "beginner"  # Default assumption
    
    target_level = target_level.lower()
    if target_level not in levels:
        target_level = "intermediate"
    
    # Calculate gap
    current_score = level_scores.get(current_level, 1)
    target_score = level_scores.get(target_level, 2)
    gap_size = target_score - current_score
    
    if gap_size <= 0:
        gap_level = "none"
        estimated_hours = 5
    elif gap_size == 1:
        gap_level = "small"
        estimated_hours = 20
    elif gap_size == 2:
        gap_level = "medium"
        estimated_hours = 50
    else:
        gap_level = "large"
        estimated_hours = 100
    
    # Generate knowledge gap areas based on topic
    knowledge_gaps = _generate_knowledge_gaps(topic, current_level, target_level)
    prerequisite_topics = _generate_prerequisites(topic, current_level)
    
    result = {
        "status": "success",
        "topic": topic,
        "current_level": current_level,
        "target_level": target_level,
        "gap_level": gap_level,
        "knowledge_gaps": knowledge_gaps,
        "prerequisite_topics": prerequisite_topics,
        "estimated_hours": estimated_hours,
        "gap_summary": f"To go from {current_level} to {target_level} in {topic}, approximately {estimated_hours} hours of learning is recommended.",
    }
    
    # Store in session state
    tool_context.state["student:topic"] = topic
    tool_context.state["student:current_level"] = current_level
    tool_context.state["student:target_level"] = target_level
    tool_context.state["student:knowledge_gaps"] = knowledge_gaps
    tool_context.state["student:estimated_hours"] = estimated_hours
    
    return result


def _generate_knowledge_gaps(topic: str, current_level: str, target_level: str) -> list:
    """Generate specific knowledge gaps based on topic and levels."""
    
    # Generic gap templates that can be customized per topic
    level_gaps = {
        "beginner": [
            f"Core concepts and terminology of {topic}",
            f"Basic syntax and structure",
            f"Fundamental principles",
            f"Simple practical applications",
        ],
        "intermediate": [
            f"Advanced {topic} patterns and best practices",
            f"Error handling and debugging",
            f"Performance optimization basics",
            f"Real-world project experience",
        ],
        "advanced": [
            f"Complex {topic} architectures",
            f"Advanced optimization techniques",
            f"System design with {topic}",
            f"Edge cases and advanced troubleshooting",
        ],
        "expert": [
            f"Cutting-edge {topic} developments",
            f"Contributing to {topic} ecosystem",
            f"Teaching and mentoring others",
            f"Innovation and research in {topic}",
        ],
    }
    
    levels = ["beginner", "intermediate", "advanced", "expert"]
    current_idx = levels.index(current_level) if current_level in levels else 0
    target_idx = levels.index(target_level) if target_level in levels else 1
    
    gaps = []
    for level in levels[current_idx + 1:target_idx + 1]:
        gaps.extend(level_gaps.get(level, []))
    
    return gaps[:6]  # Return top 6 gaps


def _generate_prerequisites(topic: str, current_level: str) -> list:
    """Generate prerequisite topics based on current level."""
    
    if current_level == "beginner":
        return [
            "Basic computer literacy",
            "Problem-solving fundamentals",
            "Logical thinking",
        ]
    elif current_level == "intermediate":
        return [
            f"Solid foundation in {topic} basics",
            "Version control basics (Git)",
            "Development environment setup",
        ]
    else:
        return []


# ============================================================================
# LEARNING PATH STORAGE TOOL (with Long-Running Operation support)
# ============================================================================

def store_learning_path(
    tool_context: ToolContext,
    student_id: str,
    learning_path: str,
    complexity_level: str = "normal",
    requires_approval: bool = False,
) -> Dict[str, Any]:
    """
    Stores the generated learning path with optional teacher approval workflow.
    
    For complex or high-stakes learning paths, this tool can pause execution
    to request teacher approval before delivering to the student.
    
    Args:
        tool_context: ADK tool context for state management and LRO
        student_id: Unique identifier for the student
        learning_path: The generated learning path content
        complexity_level: Complexity of the path (simple/normal/complex/advanced)
        requires_approval: Whether teacher approval is required
        
    Returns:
        Dictionary containing:
        - status: approved/pending/rejected
        - path_id: Unique identifier for the learning path
        - message: Status message
    """
    
    import uuid
    from datetime import datetime
    
    path_id = f"LP-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().isoformat()
    
    # Check if approval is needed for complex paths
    approval_needed = requires_approval or complexity_level in ["complex", "advanced"]
    
    # If approval needed and no confirmation yet, pause for approval
    if approval_needed and not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"⚠️ Complex learning path generated for student {student_id}. Complexity: {complexity_level}. Please review and approve.",
            payload={
                "student_id": student_id,
                "path_id": path_id,
                "complexity_level": complexity_level,
                "learning_path_preview": learning_path[:500] + "..." if len(learning_path) > 500 else learning_path,
                "timestamp": timestamp,
            }
        )
        
        return {
            "status": "pending",
            "path_id": path_id,
            "message": f"Learning path {path_id} requires teacher approval before delivery.",
        }
    
    # If we're resuming with a confirmation
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            # Approved - store and deliver
            tool_context.state[f"learning_path:{path_id}"] = {
                "student_id": student_id,
                "content": learning_path,
                "complexity": complexity_level,
                "status": "approved",
                "approved_at": timestamp,
            }
            
            return {
                "status": "approved",
                "path_id": path_id,
                "message": f"Learning path {path_id} approved by teacher and saved successfully.",
            }
        else:
            # Rejected
            return {
                "status": "rejected",
                "path_id": path_id,
                "message": f"Learning path {path_id} was rejected by teacher. Please revise.",
            }
    
    # No approval needed - store directly
    tool_context.state[f"learning_path:{path_id}"] = {
        "student_id": student_id,
        "content": learning_path,
        "complexity": complexity_level,
        "status": "approved",
        "created_at": timestamp,
    }
    
    return {
        "status": "approved",
        "path_id": path_id,
        "message": f"Learning path {path_id} saved successfully for student {student_id}.",
    }


# ============================================================================
# STUDENT PROFILE RETRIEVAL TOOL
# ============================================================================

def get_student_profile(
    tool_context: ToolContext,
    student_id: str,
) -> Dict[str, Any]:
    """
    Retrieves stored student profile information from session state.
    
    Args:
        tool_context: ADK tool context for state access
        student_id: Unique identifier for the student
        
    Returns:
        Dictionary containing student profile data or error if not found.
    """
    
    profile = {
        "student_id": student_id,
        "learning_style": tool_context.state.get("student:learning_style"),
        "style_breakdown": tool_context.state.get("student:style_breakdown"),
        "content_recommendations": tool_context.state.get("student:content_recommendations"),
        "topic": tool_context.state.get("student:topic"),
        "current_level": tool_context.state.get("student:current_level"),
        "target_level": tool_context.state.get("student:target_level"),
        "knowledge_gaps": tool_context.state.get("student:knowledge_gaps"),
        "estimated_hours": tool_context.state.get("student:estimated_hours"),
    }
    
    # Check if we have any data
    has_data = any(v is not None for k, v in profile.items() if k != "student_id")
    
    if has_data:
        return {
            "status": "success",
            "profile": profile,
            "message": f"Retrieved profile for student {student_id}",
        }
    else:
        return {
            "status": "not_found",
            "profile": None,
            "message": f"No profile data found for student {student_id}. Please run analysis first.",
        }

