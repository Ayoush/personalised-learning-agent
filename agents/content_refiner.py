"""
Content Refiner - Loop Agent

Iteratively refines the learning content through a cycle of:
Content Generation → Quality Review → Refinement
until quality standards are met.
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool


# ============================================================================
# EXIT FUNCTION - Called when content quality is approved
# ============================================================================

def exit_refinement_loop():
    """
    Call this function ONLY when the content quality review returns 'APPROVED',
    indicating the learning content meets all quality standards.
    """
    return {
        "status": "approved",
        "message": "Content quality approved. Exiting refinement loop.",
    }


# ============================================================================
# CONTENT GENERATOR AGENT
# ============================================================================

content_generator_agent = Agent(
    name="ContentGeneratorAgent",
    model="gemini-2.5-flash",
    description="Generates or refines learning content based on curriculum and feedback.",
    instruction="""You are an expert educational content creator.

Your task is to generate high-quality learning content.

**If this is the first generation**:
Using the available curriculum, resources, and student profile, create:

1. **Module Introduction**:
   - Engaging overview of what will be learned
   - Learning objectives clearly stated
   - Real-world relevance explained

2. **Core Content**:
   - Clear explanations of key concepts
   - Examples and analogies suited to learning style
   - Step-by-step breakdowns where needed

3. **Practical Elements**:
   - Code examples (if applicable)
   - Practice exercises
   - Real-world applications

4. **Summary & Next Steps**:
   - Key takeaways
   - Connection to next module
   - Additional exploration suggestions

**If refining based on feedback**:
Previous Content: {current_content}
Feedback: {critique}

Address all feedback points while maintaining content quality.

Output the complete, polished learning content.""",
    output_key="current_content",
)


# ============================================================================
# QUALITY REVIEWER AGENT
# ============================================================================

quality_reviewer_agent = Agent(
    name="QualityReviewerAgent",
    model="gemini-2.5-flash",
    description="Reviews learning content quality and provides feedback or approval.",
    instruction="""You are a strict but fair educational content quality reviewer.

Review the learning content provided: {current_content}

Evaluate against these quality criteria:

1. **Clarity** (25%):
   - Are explanations clear and understandable?
   - Is the language appropriate for the target level?
   - Are concepts introduced logically?

2. **Accuracy** (25%):
   - Is the information technically correct?
   - Are examples valid and working?
   - Are there any misleading statements?

3. **Engagement** (20%):
   - Is the content interesting and motivating?
   - Are there varied learning elements?
   - Does it maintain attention?

4. **Completeness** (15%):
   - Are all key concepts covered?
   - Are there gaps in the explanation?
   - Is prerequisite knowledge addressed?

5. **Practicality** (15%):
   - Are there actionable exercises?
   - Can learners apply what they learned?
   - Are real-world connections made?

**Your Response**:

If ALL criteria are satisfactorily met (score >= 80% overall):
Respond with EXACTLY: "APPROVED"

If improvements are needed:
Provide specific, actionable feedback:

## Quality Review Feedback

**Overall Score**: [X/100]

**Issues to Address**:
1. [Specific issue and how to fix it]
2. [Specific issue and how to fix it]
...

**Strengths to Maintain**:
- [What works well]

Be constructive but maintain high standards. Don't approve mediocre content.""",
    output_key="critique",
)


# ============================================================================
# REFINER AGENT
# ============================================================================

refiner_agent = Agent(
    name="RefinerAgent",
    model="gemini-2.5-flash",
    description="Refines content based on review feedback or exits if approved.",
    instruction="""You are a content refinement specialist.

You have:
- Content: {current_content}
- Review: {critique}

**Decision Logic**:

IF the critique is EXACTLY "APPROVED":
- Call the `exit_refinement_loop` function immediately
- Do nothing else

IF the critique contains feedback:
- Carefully analyze each feedback point
- Revise the content to address ALL issues
- Maintain the strengths mentioned
- Improve overall quality
- Output the refined, complete content

When refining:
- Address each critique point specifically
- Don't remove good content unnecessarily
- Improve clarity and engagement
- Ensure accuracy of all information""",
    tools=[FunctionTool(exit_refinement_loop)],
    output_key="current_content",  # Overwrites with refined version
)


# ============================================================================
# CONTENT REFINEMENT LOOP
# ============================================================================

content_refinement_loop = LoopAgent(
    name="ContentRefinementLoop",
    description="Iteratively refines content through review cycles until quality standards are met.",
    sub_agents=[quality_reviewer_agent, refiner_agent],
    max_iterations=3,  # Maximum 3 refinement cycles
)


# ============================================================================
# FULL CONTENT PIPELINE (Generator → Refinement Loop)
# ============================================================================

content_generation_pipeline = SequentialAgent(
    name="ContentGenerationPipeline",
    description="Complete pipeline: generates content then refines until approved.",
    sub_agents=[content_generator_agent, content_refinement_loop],
)

