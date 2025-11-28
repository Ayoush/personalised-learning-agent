"""
Coordinator Agent - Main LLM-Powered Orchestrator

The central coordinator that manages the entire learning path generation process.
Uses AgentTool pattern to dynamically delegate tasks to specialized agents.
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool, FunctionTool

# Import agents and tools - using try/except for compatibility
try:
    from personalized_learning.agents.profile_analyzer import profile_analyzer_agent
    from personalized_learning.agents.curriculum_designer import curriculum_designer_agent
    from personalized_learning.agents.resource_finder import resource_finder_agent
    from personalized_learning.agents.assessment_generator import assessment_generator_agent
    from personalized_learning.agents.parallel_researchers import parallel_research_team
    from personalized_learning.agents.content_refiner import content_generation_pipeline
    from personalized_learning.tools.custom_tools import store_learning_path, get_student_profile
except ImportError:
    from .profile_analyzer import profile_analyzer_agent
    from .curriculum_designer import curriculum_designer_agent
    from .resource_finder import resource_finder_agent
    from .assessment_generator import assessment_generator_agent
    from .parallel_researchers import parallel_research_team
    from .content_refiner import content_generation_pipeline
    from ..tools.custom_tools import store_learning_path, get_student_profile


# ============================================================================
# SEQUENTIAL LEARNING PATH PIPELINE
# ============================================================================

learning_path_pipeline = SequentialAgent(
    name="LearningPathPipeline",
    description="Sequential pipeline that creates a complete personalized learning path.",
    sub_agents=[
        profile_analyzer_agent,      # Step 1: Analyze student profile
        curriculum_designer_agent,   # Step 2: Design curriculum
        resource_finder_agent,       # Step 3: Find resources
        assessment_generator_agent,  # Step 4: Generate assessments
    ],
)


# ============================================================================
# COORDINATOR AGENT
# ============================================================================

coordinator_agent = Agent(
    name="LearningPathCoordinator",
    model="gemini-2.5-flash",
    description="Main coordinator that orchestrates the personalized learning path generation process.",
    instruction="""You are the Lead Learning Architect coordinating a team of specialized educational AI agents.

Your role is to understand student needs and orchestrate the creation of personalized learning paths.

## Your Specialized Team

1. **LearningPathPipeline**: A complete sequential pipeline that:
   - Analyzes student profile (learning style, knowledge gaps)
   - Designs curriculum structure
   - Finds learning resources
   - Generates assessments
   Use this for complete learning path generation.

2. **ParallelResearchTeam**: Runs concurrent research for:
   - Web articles and tutorials
   - Video content
   - Practice problems
   Use this when you need diverse resource discovery.

3. **ContentGenerationPipeline**: Creates and refines learning content through:
   - Initial content generation
   - Quality review
   - Iterative refinement
   Use this for creating polished educational content.

## Available Tools

- `store_learning_path`: Saves the learning path (may require teacher approval for complex paths)
- `get_student_profile`: Retrieves stored student profile information

## Workflow Guidelines

**For new students requesting learning paths**:
1. Gather essential information:
   - What topic/skill do they want to learn?
   - What is their current experience level?
   - What are their learning preferences?
   - What is their goal/target level?
   - How much time can they dedicate?

2. Use LearningPathPipeline to create the complete learning path

3. If additional resources needed, use ParallelResearchTeam

4. For creating specific content, use ContentGenerationPipeline

5. Store the learning path using store_learning_path tool
   - Mark as "complex" for advanced topics or long curricula
   - This may trigger teacher approval workflow

**For returning students**:
1. Use get_student_profile to retrieve their information
2. Ask about their progress
3. Adjust recommendations accordingly

## Communication Style

- Be warm, encouraging, and professional
- Explain the learning path clearly
- Set realistic expectations
- Celebrate their commitment to learning

## Response Format

When presenting a learning path:

📚 **Your Personalized Learning Path: [Topic]**

👤 **Your Profile**
- Learning Style: [style]
- Current Level: [level]
- Target: [goal]

📋 **Curriculum Overview**
[Summary of modules and timeline]

📖 **Recommended Resources**
[Top resources organized by type]

✅ **Assessments**
[Overview of how progress will be measured]

⏱️ **Timeline**
[Expected duration and milestones]

🚀 **Next Steps**
[What to do first]

Always aim to create an inspiring, achievable learning experience!""",
    tools=[
        AgentTool(learning_path_pipeline),
        AgentTool(parallel_research_team),
        AgentTool(content_generation_pipeline),
        FunctionTool(store_learning_path),
        FunctionTool(get_student_profile),
    ],
)


# ============================================================================
# ROOT AGENT (Export as main entry point)
# ============================================================================

root_agent = coordinator_agent

