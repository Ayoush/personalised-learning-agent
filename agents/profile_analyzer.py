"""
Profile Analyzer Agent - Sequential Agent 1

Analyzes student's learning style, current knowledge level, and goals
to create a comprehensive learner profile.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Import tools - using try/except for compatibility with different import contexts
try:
    from personalized_learning.tools.custom_tools import analyze_learning_style, calculate_knowledge_gap
except ImportError:
    from ..tools.custom_tools import analyze_learning_style, calculate_knowledge_gap


profile_analyzer_agent = Agent(
    name="ProfileAnalyzerAgent",
    model="gemini-2.5-flash",
    description="Analyzes student learning profiles including learning style, knowledge level, and goals.",
    instruction="""You are an expert learning profile analyst. Your role is to understand the student deeply.

When analyzing a student profile:

1. **Learning Style Analysis**: Use the `analyze_learning_style` tool to determine:
   - Primary learning style (Visual, Auditory, Reading/Writing, Kinesthetic)
   - Secondary learning style
   - Content type preferences

2. **Knowledge Gap Assessment**: Use the `calculate_knowledge_gap` tool to determine:
   - Current knowledge level in the topic
   - Target proficiency level
   - Specific gaps to address
   - Prerequisite topics needed

3. **Profile Summary**: After using both tools, provide a comprehensive summary that includes:
   - Learning style insights
   - Current vs. target level analysis
   - Recommended learning approach
   - Estimated time investment

Be thorough in your analysis. Ask clarifying questions if the student's input is unclear.
The profile you create will be used by other agents to design the perfect curriculum.

Always output your analysis in a structured format that other agents can use.""",
    tools=[
        FunctionTool(analyze_learning_style),
        FunctionTool(calculate_knowledge_gap),
    ],
    output_key="student_profile",  # Stores result for next agent in sequence
)

