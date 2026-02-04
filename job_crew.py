"""
Multi-Agent Job Search System using CrewAI
This module defines the agents, tasks, and crew for job searching and resume analysis.
Includes deep scraping capabilities for extracting full job posting content.
"""

import os
import logging
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafeScrapeWebsiteTool(ScrapeWebsiteTool):
    """
    A wrapper around ScrapeWebsiteTool with built-in error handling.
    Gracefully handles blocked websites and returns fallback data.
    """

    def _run(self, website_url: str) -> str:
        """
        Scrape website with error handling for blocked/failed requests.

        Args:
            website_url: The URL to scrape

        Returns:
            Scraped content or fallback message
        """
        try:
            logger.info(f"Attempting to scrape: {website_url}")
            result = super()._run(website_url)

            if result and len(result) > 100:
                logger.info(f"Successfully scraped {len(result)} characters from {website_url}")
                return result
            else:
                logger.warning(f"Minimal content returned from {website_url}")
                return self._fallback_message(website_url, "minimal content")

        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Scraping failed for {website_url}: {e}")

            # Handle specific error types
            if "403" in error_msg or "forbidden" in error_msg:
                return self._fallback_message(website_url, "access forbidden (403)")
            elif "404" in error_msg or "not found" in error_msg:
                return self._fallback_message(website_url, "page not found (404)")
            elif "timeout" in error_msg:
                return self._fallback_message(website_url, "connection timeout")
            elif "ssl" in error_msg or "certificate" in error_msg:
                return self._fallback_message(website_url, "SSL certificate error")
            else:
                return self._fallback_message(website_url, f"error: {str(e)[:100]}")

    def _fallback_message(self, url: str, reason: str) -> str:
        """Generate a fallback message when scraping fails."""
        return f"""
[SCRAPING NOTICE]
URL: {url}
Status: Could not fully scrape this page ({reason})
Action: Using search snippet data instead. Continue analysis with available information.

Note: Some job boards block automated access. The search results still contain
valuable information about this position. Proceed with the analysis using the
job title, company name, and requirements from the search snippets.
"""


def create_crew(
    topic: str,
    resume_text: str,
    gemini_key: str,
    serper_key: str,
    work_type: str = "Any",
    salary_range: str = "Not specified",
    experience_level: str = "Any",
    deep_search: bool = False,
) -> dict:
    """
    Create and run a CrewAI crew for job searching and resume optimization.

    Args:
        topic: Job title or search topic (e.g., "Senior Python Developer")
        resume_text: The user's resume content
        gemini_key: Google Gemini API key
        serper_key: Serper API key for web search
        work_type: Preferred work arrangement (Remote/Hybrid/On-site/Any)
        salary_range: Expected salary range
        experience_level: Experience level (Entry/Mid/Senior/Any)
        deep_search: Enable deep scraping of job posting URLs for detailed analysis

    Returns:
        Dictionary containing structured results from each task
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

    # Configure tools based on search depth
    researcher_tools = [search_tool]

    if deep_search:
        # Add scraping tool for deep search mode
        scrape_tool = SafeScrapeWebsiteTool()
        researcher_tools.append(scrape_tool)
        logger.info("Deep search enabled: Scraping tool activated")

    # Build preferences string for search context
    preferences = f"""
    Candidate Preferences:
    - Work Type: {work_type}
    - Salary Range: {salary_range}
    - Experience Level: {experience_level}
    """

    # Deep search instructions
    deep_search_instructions = ""
    if deep_search:
        deep_search_instructions = """

    DEEP SEARCH MODE ENABLED:
    You have access to the ScrapeWebsiteTool. For each promising job posting:
    1. Use the scrape tool to visit the actual job posting URL
    2. Extract the FULL job description including:
       - Complete list of required skills and technologies
       - Company culture and values
       - Benefits and perks mentioned
       - Team structure and reporting lines
       - Specific project or product details
       - Hidden requirements not in the snippet
    3. If a website blocks scraping (403 error or similar), gracefully continue
       using the search snippet data - DO NOT let this stop your research
    4. Pass ALL scraped content to subsequent agents for deeper analysis

    FALLBACK BEHAVIOR:
    - If scraping fails, use the search result snippets
    - Never report an error to the user for blocked sites
    - Continue with available data and note which sources were limited
    """

    # ========== DEFINE AGENTS ==========

    # Agent 1: Job Researcher (Enhanced with scraping capabilities)
    researcher_backstory = """You are an expert job market researcher with 15+ years of experience
        in talent acquisition and job market analysis. You have deep connections across
        LinkedIn, Indeed, Glassdoor, and niche job boards. You specialize in identifying
        both well-known opportunities at top companies and hidden gems at growing startups.
        You understand salary benchmarks, market trends, and what makes a job posting
        legitimate and worthwhile. You always verify job details and prioritize positions
        that match the candidate's stated preferences for work arrangement and compensation."""

    if deep_search:
        researcher_backstory += """

        ADVANCED CAPABILITY: You are equipped with web scraping tools that allow you to
        read the FULL content of job posting pages. This gives you access to:
        - Complete job descriptions beyond search snippets
        - Hidden requirements and "nice-to-haves"
        - Company culture information
        - Detailed tech stack specifications
        - Benefits and compensation details

        When you find a relevant job URL, use your scraping tool to extract the complete
        posting. If a site blocks access, gracefully fall back to using search data."""

    researcher = Agent(
        role="Senior Job Market Researcher" + (" & Web Intelligence Specialist" if deep_search else ""),
        goal=f"Find the best {work_type.lower()} job opportunities for {topic} positions matching candidate preferences"
             + (" and extract full job details using web scraping" if deep_search else ""),
        backstory=researcher_backstory,
        tools=researcher_tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 2: Resume Profiler (Enhanced as Technical Recruiter)
    profiler = Agent(
        role="Senior Technical Recruiter & ATS Expert",
        goal="Perform deep keyword analysis between resume and job requirements to maximize ATS compatibility",
        backstory="""You are a Senior Technical Recruiter with 12+ years of experience at
        Fortune 500 companies and top tech firms (Google, Amazon, Microsoft). You have
        personally reviewed over 50,000 resumes and understand exactly how Applicant
        Tracking Systems (ATS) work. Your expertise lies in:

        1. KEYWORD OPTIMIZATION: You identify exact keyword matches and gaps between
           resumes and job descriptions. You know which keywords are "must-haves" vs
           "nice-to-haves" and how ATS algorithms rank candidates.

        2. SKILLS GAP ANALYSIS: You pinpoint specific technical skills, certifications,
           and tools that are missing from the resume but required in job postings.

        3. MATCH SCORING: You calculate precise match percentages based on required
           qualifications, preferred qualifications, and years of experience.

        4. COMPETITIVE POSITIONING: You understand what makes a candidate stand out
           and what red flags recruiters look for.

        You are brutally honest in your assessments because you want candidates to succeed.

        IMPORTANT: When analyzing job requirements, use ALL available information including
        any scraped full job descriptions provided by the Researcher. The more detailed
        the job posting data, the more precise your keyword analysis will be.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 3: Content Writer (Enhanced for structured output)
    writer = Agent(
        role="Executive Career Content Strategist",
        goal="Create a comprehensive, professionally formatted Job Application Report",
        backstory="""You are an Executive Career Content Strategist who has helped
        C-level executives, senior engineers, and professionals at all levels land
        positions at top companies. You've written content that has secured offers
        at FAANG companies, Fortune 500 corporations, and high-growth startups.

        Your expertise includes:
        - ATS-optimized resume writing with powerful action verbs and metrics
        - Compelling cover letters that tell a story and show cultural fit
        - Interview preparation and talking points
        - LinkedIn profile optimization for recruiter visibility

        You always deliver your work in a clean, professional, well-structured format
        using proper Markdown formatting for easy reading and implementation.

        IMPORTANT: Leverage ALL job details provided, including scraped content with
        company culture, values, and specific requirements. Tailor cover letters to
        mention specific details that show you've researched the company thoroughly.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    # ========== DEFINE TASKS ==========

    # Task 1: Search for Jobs (Enhanced with deep search capabilities)
    search_task_description = f"""Search for the latest job opportunities related to: {topic}

        {preferences}
        {deep_search_instructions}

        Your task:
        1. Search for current job openings for {topic} positions
        2. Filter for {work_type} positions when possible
        3. Find at least 5-7 relevant job postings
        4. For each job, extract:
           - Job title (exact title from posting)
           - Company name
           - Location and work arrangement (Remote/Hybrid/On-site)
           - Key requirements and qualifications (list ALL mentioned skills)
           - Required years of experience
           - Salary range (if available)
           - Application URL or platform"""

    if deep_search:
        search_task_description += """
           - FULL JOB DESCRIPTION (from scraped content)
           - Company culture and values (if available)
           - Tech stack details (specific versions, frameworks)
           - Team information and growth opportunities
           - Benefits and perks mentioned"""

    search_task_description += f"""
        5. Identify the TOP 3 most promising opportunities based on candidate preferences
        6. List ALL unique technical skills and tools mentioned across all postings

        Focus on jobs from reputable companies. Prioritize positions matching the
        candidate's work type preference: {work_type}."""

    expected_output_jobs = """A structured job search report in this EXACT format:

## Job Opportunities Found

### Job 1: [Title] at [Company]
- **Location**: [City/Remote/Hybrid]
- **Requirements**: [Bullet list of key requirements]
- **Skills Needed**: [Comma-separated list]
- **Experience**: [X years]
- **Salary**: [Range if available]
- **URL**: [Job posting URL]"""

    if deep_search:
        expected_output_jobs += """
- **Full Description**: [Scraped content summary - key details]
- **Company Culture**: [Values, work environment details]
- **Tech Stack**: [Detailed technologies with versions if available]
- **Scrape Status**: [Success/Fallback to snippet]"""

    expected_output_jobs += """

[Repeat for all 5-7 jobs]

## Top 3 Recommended Positions
1. [Job Title at Company] - [Why it's a good fit]
2. [Job Title at Company] - [Why it's a good fit]
3. [Job Title at Company] - [Why it's a good fit]

## Skills in Demand (Aggregated)
- Technical Skills: [List]
- Soft Skills: [List]
- Tools/Platforms: [List]
- Certifications: [List if any]"""

    if deep_search:
        expected_output_jobs += """

## Deep Search Insights
- **Hidden Requirements Found**: [Skills only visible in full descriptions]
- **Common Company Values**: [Culture themes across postings]
- **Scraping Summary**: [X/Y sites successfully scraped]"""

    search_task = Task(
        description=search_task_description,
        expected_output=expected_output_jobs,
        agent=researcher,
    )

    # Task 2: Analyze Resume with Keyword Gap Analysis
    analyze_task = Task(
        description=f"""Perform a comprehensive keyword and skills gap analysis.

        Candidate's Resume:
        {resume_text}

        Your task:
        1. Extract ALL keywords from the resume:
           - Technical skills
           - Tools and technologies
           - Soft skills
           - Certifications
           - Industry terms

        2. Compare against job requirements from the research and identify:
           - MATCHING KEYWORDS: Skills in resume that match job requirements
           - MISSING KEYWORDS: Critical skills in jobs NOT in resume
           - PARTIAL MATCHES: Similar skills that need rewording

        3. Calculate a MATCH SCORE (0-100%) for each of the top 3 jobs based on:
           - Required skills match (40% weight)
           - Experience alignment (30% weight)
           - Preferred qualifications (20% weight)
           - Soft skills match (10% weight)

        4. Provide SPECIFIC keyword recommendations:
           - Exact phrases to add to resume
           - Skills to learn/acquire
           - Certifications that would boost candidacy

        {"5. Use the FULL scraped job descriptions for more accurate keyword matching" if deep_search else ""}

        Be specific and data-driven in your analysis.""",
        expected_output="""A detailed analysis report in this EXACT format:

## Resume Keyword Analysis

### Keywords Found in Resume
- **Technical Skills**: [List]
- **Tools/Technologies**: [List]
- **Soft Skills**: [List]
- **Certifications**: [List]

## Match Analysis

### Job 1: [Title] at [Company]
- **Match Score**: [X]%
- **Matching Keywords**: [List of matching skills]
- **Missing Keywords**: [List of gaps - CRITICAL]
- **Recommendation**: [Specific advice]

[Repeat for top 3 jobs]

## Keyword Gap Summary

### Critical Missing Skills (Add to Resume)
1. [Skill] - Required by X/Y jobs
2. [Skill] - Required by X/Y jobs
[Continue list]

### Skills to Learn/Acquire
1. [Skill] - [Why important]
2. [Skill] - [Why important]

### Recommended Certifications
1. [Certification] - [Impact on candidacy]

## Candidate Strengths
- [Unique selling point 1]
- [Unique selling point 2]
- [Unique selling point 3]""",
        agent=profiler,
        context=[search_task],
    )

    # Task 3: Write Content with Structured Report Format
    write_task = Task(
        description=f"""Create a comprehensive Job Application Report based on the job
        research and resume analysis.

        Your task is to produce a PROFESSIONALLY FORMATTED report with these sections:

        1. EXECUTIVE SUMMARY
           - Overall match assessment
           - Top recommended job with match score
           - Key action items

        2. TAILORED COVER LETTER
           - Professional, customizable template
           - Placeholders for [Company Name] and [Position]
           - Highlights matching skills from analysis
           - Addresses gaps positively
           - Under 350 words, compelling narrative
           {"- Reference specific company values/culture from scraped data" if deep_search else ""}

        3. OPTIMIZED RESUME BULLETS
           - 7-10 powerful bullet points
           - Incorporate missing keywords naturally
           - Use metrics and quantifiable achievements
           - ATS-friendly formatting

        4. INTERVIEW PREPARATION
           - 5 likely interview questions based on job requirements
           - Suggested answers incorporating candidate's experience
           - Key talking points
           {"- Company-specific questions based on scraped culture info" if deep_search else ""}

        5. LINKEDIN OPTIMIZATION
           - Suggested headline (120 chars max)
           - Summary paragraph (2000 chars max)
           - Skills to add to profile

        Target role: {topic}
        Work preference: {work_type}

        Format everything in clean, professional Markdown.""",
        expected_output="""
# Job Application Report

## Executive Summary
- **Best Match**: [Job Title] at [Company] - [X]% Match
- **Overall Assessment**: [2-3 sentence summary]
- **Key Action Items**:
  1. [Action 1]
  2. [Action 2]
  3. [Action 3]

---

## Tailored Cover Letter

[Professional cover letter with [Company Name] and [Position] placeholders]

---

## Optimized Resume Bullets

### Experience Highlights
1. [Strong action verb] + [Task] + [Quantifiable result]
2. [Continue with ATS-optimized bullets...]

### Skills Section Additions
- Add: [Skill 1], [Skill 2], [Skill 3]
- Reword: "[Current phrasing]" → "[Optimized phrasing]"

---

## Interview Preparation

### Likely Questions
1. **[Question 1]**
   - *Suggested Answer*: [Answer incorporating experience]

[Continue for 5 questions]

### Key Talking Points
- [Point 1]
- [Point 2]
- [Point 3]

---

## LinkedIn Optimization

### Suggested Headline
[Optimized headline under 120 characters]

### Suggested Summary
[Professional summary paragraph]

### Skills to Add
[List of skills to add to LinkedIn profile]

---

## Next Steps
1. [Immediate action]
2. [Short-term action]
3. [Long-term action]
""",
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
    logger.info(f"Starting crew execution (deep_search={deep_search})")
    result = crew.kickoff()
    logger.info("Crew execution completed")

    # Return structured results
    return {
        "jobs": str(search_task.output) if search_task.output else "",
        "analysis": str(analyze_task.output) if analyze_task.output else "",
        "documents": str(write_task.output) if write_task.output else "",
        "full_report": str(result),
        "deep_search_enabled": deep_search,
    }
