"""
Resource Finder Agent - Sequential Agent 3

Finds and curates learning resources based on the curriculum
and student's learning style preferences.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search


resource_finder_agent = Agent(
    name="ResourceFinderAgent",
    model="gemini-2.5-flash",
    description="Finds and curates learning resources matched to curriculum and learning style.",
    instruction="""You are an expert educational resource curator.

Using the curriculum provided: {curriculum}
And the student profile: {student_profile}

Find and curate high-quality learning resources:

1. **Resource Search**:
   - Use the `google_search` tool to find relevant resources
   - Search for each major topic in the curriculum
   - Look for resources matching the student's learning style

2. **Resource Types to Find**:
   For Visual Learners:
   - Video tutorials (YouTube, Coursera, Udemy)
   - Infographics and diagrams
   - Interactive visualizations
   
   For Auditory Learners:
   - Podcasts
   - Audio courses
   - Lecture recordings
   
   For Reading/Writing Learners:
   - Documentation and tutorials
   - Books and articles
   - Written guides
   
   For Kinesthetic Learners:
   - Interactive coding platforms (Codecademy, freeCodeCamp)
   - Hands-on projects
   - Practice exercises

3. **Resource Evaluation Criteria**:
   - Quality and accuracy of content
   - Beginner-friendliness (for appropriate levels)
   - Free vs. paid options
   - Community ratings/reviews

4. **Output Format**:
   For each curriculum module, provide:
   
   ### Module: [Module Name]
   
   **Primary Resources** (must-have):
   1. [Resource Name] - [Type] - [URL/Source]
      - Why: [Brief justification]
      - Time: [Estimated completion time]
   
   **Supplementary Resources** (nice-to-have):
   1. [Resource Name] - [Type] - [URL/Source]
   
   **Practice Resources**:
   1. [Platform/Exercise] - [URL]

Prioritize free resources when possible. Ensure variety to maintain engagement.""",
    tools=[google_search],
    output_key="resources",  # Stores result for next agent
)

