"""
Multi-Agent Job Search System using CrewAI
This module defines the agents, tasks, and crew for job searching and resume analysis.
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI


def create_crew(topic: str, resume_text: str, gemini_key: str, serper_key: str) -> str:
    """
    Create and run a CrewAI crew for job searching and resume optimization.

    Args:
        topic: Job title or search topic (e.g., "Senior Python Developer")
        resume_text: The user's resume content
        gemini_key: Google Gemini API key
        serper_key: Serper API key for web search

    Returns:
        The final output from the crew execution
    """
    # Set environment variables for the tools
    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ["SERPER_API_KEY"] = serper_key

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=gemini_key,
        temperature=0.7,
    )

    # Initialize tools
    search_tool = SerperDevTool()

    # ========== DEFINE AGENTS ==========

    # Agent 1: Job Researcher
    researcher = Agent(
        role="Senior Job Researcher",
        goal=f"Find the best job opportunities for {topic} positions",
        backstory="""You are an expert job market researcher with years of experience
        in identifying the best job opportunities. You have a keen eye for matching
        job requirements with candidate profiles and stay updated on the latest
        industry trends and hiring patterns. You excel at finding both well-known
        and hidden job opportunities across various platforms.""",
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 2: Resume Profiler
    profiler = Agent(
        role="Professional Resume Analyst",
        goal="Analyze the candidate's resume and match it against job requirements",
        backstory="""You are a seasoned HR professional and career coach with
        extensive experience in resume analysis and job matching. You understand
        what employers look for and can identify both strengths and gaps in a
        candidate's profile. You provide actionable insights to improve job
        application success rates.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 3: Content Writer
    writer = Agent(
        role="Professional Career Content Writer",
        goal="Create compelling cover letters and optimized resume bullet points",
        backstory="""You are an expert career content writer who has helped
        thousands of professionals land their dream jobs. You know how to craft
        compelling narratives that highlight achievements and align with job
        requirements. Your writing is clear, impactful, and ATS-friendly.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # ========== DEFINE TASKS ==========

    # Task 1: Search for Jobs
    search_task = Task(
        description=f"""Search for the latest job opportunities related to: {topic}

        Your task:
        1. Search for current job openings for {topic} positions
        2. Find at least 5-7 relevant job postings
        3. For each job, extract:
           - Job title
           - Company name
           - Key requirements and qualifications
           - Required skills (technical and soft skills)
           - Experience level required
           - Location (remote/hybrid/onsite)
           - Any salary information if available
        4. Identify common patterns in job requirements
        5. Note any emerging skills or technologies being requested

        Focus on jobs from reputable companies and platforms.""",
        expected_output="""A comprehensive report containing:
        - List of 5-7 relevant job opportunities with details
        - Common requirements across these positions
        - Key skills in demand for this role
        - Industry trends observed""",
        agent=researcher,
    )

    # Task 2: Analyze Resume
    analyze_task = Task(
        description=f"""Analyze the candidate's resume against the job opportunities found.

        Candidate's Resume:
        {resume_text}

        Your task:
        1. Review the candidate's current skills, experience, and qualifications
        2. Compare against the job requirements from the research
        3. Identify:
           - Strong matches (skills/experience that align well)
           - Gaps (missing skills or experience)
           - Transferable skills that could be highlighted
           - Unique selling points of this candidate
        4. Provide a match percentage estimate for the top positions
        5. Suggest specific improvements to increase job match

        Be specific and actionable in your analysis.""",
        expected_output="""A detailed analysis containing:
        - Skills match assessment
        - Gap analysis with specific recommendations
        - Top 3 jobs the candidate is best suited for
        - Priority areas for improvement
        - Unique strengths to emphasize""",
        agent=profiler,
        context=[search_task],
    )

    # Task 3: Write Content
    write_task = Task(
        description=f"""Based on the job research and resume analysis, create professional
        application materials for the candidate.

        Your task:
        1. Write a compelling, customizable cover letter template that:
           - Has placeholders for company name and specific role
           - Highlights the candidate's relevant achievements
           - Addresses potential gaps positively
           - Shows enthusiasm and cultural fit
           - Is concise (under 400 words)

        2. Create 5-7 powerful resume bullet points that:
           - Use strong action verbs
           - Include quantifiable achievements where possible
           - Align with the common job requirements found
           - Are ATS-friendly

        3. Provide 3-5 key talking points for interviews

        4. Suggest LinkedIn headline and summary improvements

        Make the content professional, impactful, and tailored to {topic} roles.""",
        expected_output="""Complete application package containing:
        - Professional cover letter template
        - Optimized resume bullet points
        - Interview talking points
        - LinkedIn optimization suggestions
        - Tips for customizing materials for specific applications""",
        agent=writer,
        context=[search_task, analyze_task],
    )

    # ========== CREATE AND RUN CREW ==========

    crew = Crew(
        agents=[researcher, profiler, writer],
        tasks=[search_task, analyze_task, write_task],
        process=Process.sequential,
        verbose=True,
    )

    # Execute the crew
    result = crew.kickoff()

    return str(result)
