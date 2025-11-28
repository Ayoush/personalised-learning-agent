"""
Personalized Learning Path Generator - Main Agent Module

This is the main entry point for the ADK agent system.
The root_agent is the coordinator that orchestrates all specialized agents.

Features demonstrated:
- Multi-Agent System (Sequential, Parallel, Loop agents)
- Custom Tools (learning style analysis, knowledge gap)
- Long-Running Operations (teacher approval with pause/resume)
- Session State Management

Usage:
    adk run personalized_learning
    adk web personalized_learning
"""

import uuid
from datetime import datetime
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import AgentTool, FunctionTool, google_search

# ============================================================================
# CUSTOM TOOLS (defined inline to avoid import issues)
# ============================================================================

def analyze_learning_style(
    tool_context,
    student_responses: str,
    preferred_content_types: str = "",
    study_habits: str = "",
) -> dict:
    """
    Analyzes student responses to determine their learning style.
    """
    visual_keywords = ["diagram", "chart", "video", "image", "picture", "watch", "see", "visual"]
    auditory_keywords = ["listen", "audio", "podcast", "lecture", "discuss", "talk", "hear"]
    reading_keywords = ["read", "book", "article", "notes", "write", "text", "documentation"]
    kinesthetic_keywords = ["practice", "hands-on", "project", "build", "code", "experiment", "try"]
    
    full_text = f"{student_responses} {preferred_content_types} {study_habits}".lower()
    
    scores = {
        "Visual": sum(1 for kw in visual_keywords if kw in full_text),
        "Auditory": sum(1 for kw in auditory_keywords if kw in full_text),
        "Reading/Writing": sum(1 for kw in reading_keywords if kw in full_text),
        "Kinesthetic": sum(1 for kw in kinesthetic_keywords if kw in full_text),
    }
    
    total_score = sum(scores.values()) or 1
    style_breakdown = {style: round((score / total_score) * 100, 1) for style, score in scores.items()}
    
    sorted_styles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_style = sorted_styles[0][0]
    secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 else primary_style
    
    recommendations = {
        "Visual": ["Video tutorials", "Infographics", "Diagrams", "Mind maps"],
        "Auditory": ["Podcasts", "Audio lectures", "Discussion groups"],
        "Reading/Writing": ["Textbooks", "Articles", "Documentation", "Written notes"],
        "Kinesthetic": ["Hands-on projects", "Coding exercises", "Interactive labs"],
    }
    
    tool_context.state["student:learning_style"] = primary_style
    tool_context.state["student:style_breakdown"] = style_breakdown
    
    return {
        "status": "success",
        "primary_style": primary_style,
        "secondary_style": secondary_style,
        "style_breakdown": style_breakdown,
        "recommendations": recommendations.get(primary_style, []),
    }


def calculate_knowledge_gap(
    tool_context,
    topic: str,
    current_knowledge: str,
    target_level: str = "intermediate",
    prior_experience: str = "",
) -> dict:
    """
    Calculates the knowledge gap between current and target knowledge levels.
    """
    levels = ["beginner", "intermediate", "advanced", "expert"]
    level_scores = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    
    current_text = f"{current_knowledge} {prior_experience}".lower()
    
    if any(word in current_text for word in ["expert", "professional", "advanced"]):
        current_level = "advanced"
    elif any(word in current_text for word in ["some experience", "familiar", "basic"]):
        current_level = "intermediate"
    else:
        current_level = "beginner"
    
    target_level = target_level.lower()
    if target_level not in levels:
        target_level = "intermediate"
    
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
    
    tool_context.state["student:topic"] = topic
    tool_context.state["student:current_level"] = current_level
    tool_context.state["student:target_level"] = target_level
    
    return {
        "status": "success",
        "topic": topic,
        "current_level": current_level,
        "target_level": target_level,
        "gap_level": gap_level,
        "estimated_hours": estimated_hours,
    }


# ============================================================================
# STORE LEARNING PATH TOOL (with Long-Running Operation / Teacher Approval)
# ============================================================================

def store_learning_path(
    tool_context,
    student_id: str,
    learning_path_summary: str,
    total_modules: int = 4,
    total_hours: int = 20,
    complexity_level: str = "normal",
) -> dict:
    """
    Stores the generated learning path. For complex paths (advanced topics, 
    professional certification, 20+ hours), triggers TEACHER APPROVAL workflow.
    
    THIS IS A LONG-RUNNING OPERATION - it may PAUSE execution and wait for
    teacher approval before continuing.
    
    Args:
        tool_context: ADK tool context for state management and LRO
        student_id: Unique identifier for the student
        learning_path_summary: Summary of the generated learning path
        total_modules: Number of modules in the curriculum
        total_hours: Total estimated learning hours
        complexity_level: Complexity level (simple/normal/complex/advanced)
        
    Returns:
        Dictionary with status (approved/pending/rejected) and path details
    """
    path_id = f"LP-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().isoformat()
    
    # Determine if teacher approval is needed
    # Approval required for: complex paths, advanced level, or 20+ hours
    approval_needed = (
        complexity_level in ["complex", "advanced"] or 
        total_hours >= 20 or
        total_modules >= 6
    )
    
    print(f"\n🔍 [store_learning_path] Path ID: {path_id}")
    print(f"   Complexity: {complexity_level}, Hours: {total_hours}, Modules: {total_modules}")
    print(f"   Approval needed: {approval_needed}")
    
    # If approval needed and no confirmation yet, PAUSE for teacher approval
    if approval_needed and not tool_context.tool_confirmation:
        print(f"\n⏸️ [PAUSING] Requesting teacher approval for path {path_id}...")
        
        tool_context.request_confirmation(
            hint=f"""
⚠️ TEACHER APPROVAL REQUIRED

A complex learning path has been generated and requires your review:

📋 Path ID: {path_id}
👤 Student: {student_id}
📊 Complexity: {complexity_level}
⏱️ Total Hours: {total_hours}
📚 Modules: {total_modules}

📝 Summary Preview:
{learning_path_summary[:500]}{'...' if len(learning_path_summary) > 500 else ''}

Please APPROVE or REJECT this learning path.
""",
            payload={
                "path_id": path_id,
                "student_id": student_id,
                "complexity_level": complexity_level,
                "total_hours": total_hours,
                "total_modules": total_modules,
                "timestamp": timestamp,
            }
        )
        
        # Store pending state
        tool_context.state[f"pending_path:{path_id}"] = {
            "status": "pending_approval",
            "student_id": student_id,
            "summary": learning_path_summary,
            "requested_at": timestamp,
        }
        
        return {
            "status": "pending",
            "path_id": path_id,
            "message": f"⏸️ Learning path {path_id} requires TEACHER APPROVAL. Execution paused.",
            "awaiting": "teacher_confirmation",
        }
    
    # If we're resuming with a confirmation response
    if tool_context.tool_confirmation:
        print(f"\n▶️ [RESUMING] Processing teacher decision for path {path_id}...")
        
        if tool_context.tool_confirmation.confirmed:
            # APPROVED - Store and deliver
            tool_context.state[f"learning_path:{path_id}"] = {
                "student_id": student_id,
                "summary": learning_path_summary,
                "complexity": complexity_level,
                "total_hours": total_hours,
                "total_modules": total_modules,
                "status": "approved",
                "approved_at": datetime.now().isoformat(),
            }
            
            print(f"✅ [APPROVED] Path {path_id} approved by teacher!")
            
            return {
                "status": "approved",
                "path_id": path_id,
                "message": f"✅ Learning path {path_id} APPROVED by teacher and saved!",
                "approved_at": datetime.now().isoformat(),
            }
        else:
            # REJECTED
            print(f"❌ [REJECTED] Path {path_id} rejected by teacher.")
            
            return {
                "status": "rejected",
                "path_id": path_id,
                "message": f"❌ Learning path {path_id} was REJECTED by teacher. Please revise.",
            }
    
    # No approval needed - store directly
    tool_context.state[f"learning_path:{path_id}"] = {
        "student_id": student_id,
        "summary": learning_path_summary,
        "complexity": complexity_level,
        "total_hours": total_hours,
        "total_modules": total_modules,
        "status": "auto_approved",
        "created_at": timestamp,
    }
    
    print(f"✅ [AUTO-APPROVED] Path {path_id} saved (no teacher approval needed)")
    
    return {
        "status": "approved",
        "path_id": path_id,
        "message": f"✅ Learning path {path_id} saved successfully (auto-approved).",
    }


# ============================================================================
# SEQUENTIAL AGENTS
# ============================================================================

profile_analyzer_agent = Agent(
    name="ProfileAnalyzerAgent",
    model="gemini-2.5-flash",
    description="Analyzes student learning profiles including learning style and knowledge gaps.",
    instruction="""You are an expert learning profile analyst.

When analyzing a student profile:
1. Use `analyze_learning_style` to determine their learning style preferences
2. Use `calculate_knowledge_gap` to assess their current vs target level
3. Provide a comprehensive summary of findings

Output a structured profile that includes learning style, knowledge gaps, and recommendations.""",
    tools=[
        FunctionTool(analyze_learning_style),
        FunctionTool(calculate_knowledge_gap),
    ],
    output_key="student_profile",
)

curriculum_designer_agent = Agent(
    name="CurriculumDesignerAgent",
    model="gemini-2.5-flash",
    description="Designs personalized learning curricula based on student profiles.",
    instruction="""You are an expert curriculum designer.

Using the student profile: {student_profile}

Design a learning curriculum with:
1. Clear learning objectives (3-5)
2. Module structure (4-8 modules in logical progression)
3. Timeline and milestones
4. Content types matched to learning style

Output a structured curriculum plan.""",
    output_key="curriculum",
)

resource_finder_agent = Agent(
    name="ResourceFinderAgent",
    model="gemini-2.5-flash",
    description="Finds learning resources matched to curriculum and learning style.",
    instruction="""You are an expert educational resource curator.

Using the curriculum: {curriculum}
And the student profile: {student_profile}

Find and curate resources using google_search:
- Videos for visual learners
- Articles and docs for readers
- Practice platforms for kinesthetic learners

Provide organized resource recommendations.""",
    tools=[google_search],
    output_key="resources",
)

assessment_generator_agent = Agent(
    name="AssessmentGeneratorAgent",
    model="gemini-2.5-flash",
    description="Creates personalized assessments for learning evaluation.",
    instruction="""You are an expert assessment designer.

Using the curriculum: {curriculum}
And resources: {resources}

Create:
1. Pre-assessment (5 questions)
2. Module assessments (3 questions each)
3. Practice exercises
4. Final assessment

Adapt to the student's learning style from: {student_profile}""",
    output_key="assessments",
)


# ============================================================================
# PARALLEL AGENTS
# ============================================================================

web_research_agent = Agent(
    name="WebResearchAgent",
    model="gemini-2.5-flash",
    description="Finds web-based learning resources.",
    instruction="""Search for web tutorials and articles using google_search.
Focus on official docs, tutorials, and beginner-friendly content.
Output 5 quality resources with URLs and descriptions.""",
    tools=[google_search],
    output_key="web_resources",
)

video_content_agent = Agent(
    name="VideoContentAgent",
    model="gemini-2.5-flash",
    description="Finds video learning content.",
    instruction="""Search for video tutorials using google_search.
Look for YouTube tutorials, online courses (Coursera, Udemy).
Output 5 quality video resources.""",
    tools=[google_search],
    output_key="video_resources",
)

practice_problem_agent = Agent(
    name="PracticeProblemAgent",
    model="gemini-2.5-flash",
    description="Finds hands-on practice resources.",
    instruction="""Search for practice platforms using google_search.
Find: LeetCode, HackerRank, Codecademy, freeCodeCamp.
Output 5 practice resources.""",
    tools=[google_search],
    output_key="practice_resources",
)

parallel_research_team = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[web_research_agent, video_content_agent, practice_problem_agent],
)


# ============================================================================
# LOOP AGENT (Content Refinement)
# ============================================================================

def exit_refinement_loop():
    """Call when content quality is APPROVED."""
    return {"status": "approved", "message": "Content approved."}


quality_reviewer_agent = Agent(
    name="QualityReviewerAgent",
    model="gemini-2.5-flash",
    instruction="""Review the content: {current_content}

Evaluate clarity, accuracy, engagement, completeness.
If ALL criteria met (>=80%), respond EXACTLY: "APPROVED"
Otherwise provide specific improvement feedback.""",
    output_key="critique",
)

refiner_agent = Agent(
    name="RefinerAgent",
    model="gemini-2.5-flash",
    instruction="""Content: {current_content}
Review: {critique}

IF critique is "APPROVED": call exit_refinement_loop
OTHERWISE: revise content based on feedback""",
    tools=[FunctionTool(exit_refinement_loop)],
    output_key="current_content",
)

content_refinement_loop = LoopAgent(
    name="ContentRefinementLoop",
    sub_agents=[quality_reviewer_agent, refiner_agent],
    max_iterations=3,
)


# ============================================================================
# SEQUENTIAL PIPELINE
# ============================================================================

learning_path_pipeline = SequentialAgent(
    name="LearningPathPipeline",
    sub_agents=[
        profile_analyzer_agent,
        curriculum_designer_agent,
        resource_finder_agent,
        assessment_generator_agent,
    ],
)


# ============================================================================
# ROOT COORDINATOR AGENT
# ============================================================================

root_agent = Agent(
    name="LearningPathCoordinator",
    model="gemini-2.5-flash",
    description="Main coordinator for personalized learning path generation.",
    instruction="""You are the Lead Learning Architect coordinating educational AI agents.

Your role is to understand student needs and create personalized learning paths.

## Your Specialized Team

1. **LearningPathPipeline**: Creates complete learning paths (profile → curriculum → resources → assessments)
2. **ParallelResearchTeam**: Finds diverse resources concurrently
3. **store_learning_path**: Saves the final learning path (may require teacher approval for complex paths)

## Workflow

**For new students**:
1. Gather info: topic, experience level, learning preferences, goals, available time
2. Use LearningPathPipeline to create the complete path
3. Present the learning path clearly
4. **ALWAYS call store_learning_path at the end** to save the path

## IMPORTANT: Teacher Approval Workflow

For COMPLEX learning paths (advanced topics, 20+ hours, professional certification):
- Call `store_learning_path` with complexity_level="advanced" or "complex"
- The system will PAUSE and wait for teacher approval
- Once approved, the path is saved and delivered to the student

## When to mark as COMPLEX:
- Professional certification programs
- Advanced/Expert level content
- 20+ hours of learning
- Multiple specialized topics
- Production-ready skills

**Communication Style**:
- Be warm, encouraging, professional
- Explain clearly
- Set realistic expectations

**Response Format**:
📚 **Your Personalized Learning Path: [Topic]**

👤 **Your Profile**
- Learning Style: [style]
- Current Level: [level]
- Target: [goal]

📋 **Curriculum Overview**
[Modules and timeline]

📖 **Recommended Resources**
[Top resources by type]

✅ **Assessments**
[Progress tracking overview]

⏱️ **Timeline**
[Duration and milestones]

🚀 **Next Steps**
[What to do first]

After presenting, ALWAYS call store_learning_path to save!""",
    tools=[
        AgentTool(learning_path_pipeline),
        AgentTool(parallel_research_team),
        FunctionTool(store_learning_path),
    ],
)
