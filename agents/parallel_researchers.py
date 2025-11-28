"""
Parallel Research Agents

Three specialized agents that run concurrently to find different types
of learning resources: web content, video content, and practice problems.
"""

from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search


# ============================================================================
# WEB RESEARCH AGENT
# ============================================================================

web_research_agent = Agent(
    name="WebResearchAgent",
    model="gemini-2.5-flash",
    description="Researches and finds high-quality web-based learning resources like articles, tutorials, and documentation.",
    instruction="""You are a web research specialist focused on educational content.

Using the curriculum context available, search for web-based learning resources:

1. **Search Strategy**:
   - Use `google_search` to find tutorials and articles
   - Focus on reputable sources (official docs, known educational sites)
   - Look for beginner-friendly explanations

2. **Resource Types to Find**:
   - Official documentation
   - Tutorial websites (W3Schools, MDN, etc.)
   - Blog posts from experts
   - Interactive tutorials
   - Written guides and how-tos

3. **Quality Criteria**:
   - Up-to-date content
   - Clear explanations
   - Good examples
   - Active maintenance

4. **Output Format**:
   Provide 5-8 high-quality web resources:
   
   ## Web Learning Resources
   
   1. **[Resource Title]**
      - URL: [link]
      - Type: [Article/Tutorial/Documentation]
      - Difficulty: [Beginner/Intermediate/Advanced]
      - Key Topics: [what it covers]
      - Why Recommended: [brief justification]
   
   [Continue for each resource...]

Focus on quality over quantity. Each resource should add unique value.""",
    tools=[google_search],
    output_key="web_resources",
)


# ============================================================================
# VIDEO CONTENT AGENT
# ============================================================================

video_content_agent = Agent(
    name="VideoContentAgent",
    model="gemini-2.5-flash",
    description="Finds engaging video tutorials, courses, and visual learning content.",
    instruction="""You are a video content curator specializing in educational videos.

Search for the best video learning resources:

1. **Search Strategy**:
   - Use `google_search` to find video tutorials
   - Search on: "site:youtube.com [topic] tutorial"
   - Look for course platforms: Coursera, Udemy, Khan Academy

2. **Video Types to Find**:
   - YouTube tutorials (free)
   - Online course videos (Coursera, edX, Udemy)
   - Conference talks and presentations
   - Coding livestreams/walkthroughs
   - Animated explainers

3. **Quality Criteria**:
   - Clear audio and visuals
   - Good pacing
   - Engaging presenter
   - Recent content (within last 2-3 years)
   - High view count or ratings

4. **Output Format**:
   Provide 5-8 video resources:
   
   ## Video Learning Resources
   
   1. **[Video/Course Title]**
      - Platform: [YouTube/Coursera/etc.]
      - Creator: [Channel/Instructor name]
      - Duration: [Length]
      - Type: [Tutorial/Course/Lecture]
      - Difficulty: [Level]
      - Cost: [Free/Paid - $X]
      - Why Recommended: [brief justification]
   
   [Continue for each resource...]

Prioritize free resources but include premium options if exceptionally good.""",
    tools=[google_search],
    output_key="video_resources",
)


# ============================================================================
# PRACTICE PROBLEM AGENT
# ============================================================================

practice_problem_agent = Agent(
    name="PracticeProblemAgent",
    model="gemini-2.5-flash",
    description="Finds hands-on practice platforms, coding exercises, and interactive learning tools.",
    instruction="""You are a practice resource specialist focused on hands-on learning.

Find the best platforms and resources for practical exercises:

1. **Search Strategy**:
   - Use `google_search` to find practice platforms
   - Look for interactive coding environments
   - Find project-based learning resources

2. **Resource Types to Find**:
   - Coding platforms (LeetCode, HackerRank, Codecademy)
   - Interactive tutorials (freeCodeCamp, Scrimba)
   - Project repositories (GitHub, GitLab)
   - Sandbox environments
   - Practice problem sets

3. **Quality Criteria**:
   - Immediate feedback on solutions
   - Progressive difficulty
   - Real-world applicability
   - Good community support
   - Free tier available

4. **Output Format**:
   Provide 5-8 practice resources:
   
   ## Practice & Hands-On Resources
   
   1. **[Platform/Resource Name]**
      - URL: [link]
      - Type: [Coding Platform/Project/Interactive]
      - Skill Focus: [what skills it builds]
      - Difficulty Range: [Beginner to Advanced]
      - Cost: [Free/Freemium/Paid]
      - Why Recommended: [brief justification]
      - Best For: [learning style it suits]
   
   [Continue for each resource...]

Focus on resources that provide immediate feedback and real practice.""",
    tools=[google_search],
    output_key="practice_resources",
)


# ============================================================================
# PARALLEL RESEARCH TEAM
# ============================================================================

parallel_research_team = ParallelAgent(
    name="ParallelResearchTeam",
    description="Runs web, video, and practice research agents concurrently for efficient resource discovery.",
    sub_agents=[
        web_research_agent,
        video_content_agent,
        practice_problem_agent,
    ],
)

