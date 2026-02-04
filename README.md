# Multi-Agent Job Search System

A powerful AI-powered job search and resume optimization system built with CrewAI, LangChain, Streamlit, and Google Gemini. Features deep web scraping, ATS keyword analysis, and professional PDF exports.

## Overview

This application uses a team of 3 specialized AI agents that work together to:
1. **Research** current job opportunities matching your target role (with optional deep web scraping)
2. **Analyze** your resume against job requirements using ATS keyword matching
3. **Write** optimized application materials (cover letters, resume bullets, interview tips)

## Features

### Core Features
- **Intelligent Job Search**: Finds 5-7 relevant job postings using web search
- **PDF Resume Upload**: Upload your resume as PDF for automatic text extraction
- **ATS Keyword Analysis**: Technical recruiter-style gap analysis with match scores (0-100%)
- **Content Generation**: Creates tailored cover letters and ATS-optimized resume bullet points
- **Interview Prep**: Generates likely questions with suggested answers
- **LinkedIn Optimization**: Suggests headline, summary, and skills improvements

### Advanced Features
- **Deep Search Mode**: Scrapes full job posting pages for hidden requirements, tech stacks, and company culture
- **Search History**: Save and revisit previous searches within your session
- **Professional PDF Export**: Download results as beautifully formatted PDF reports
- **Job Preferences**: Filter by work arrangement, experience level, and salary range
- **Tabbed Results**: Organized output in Job List, Match Analysis, Documents, and Full Report tabs
- **Error Resilience**: Graceful fallback when websites block scraping

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [CrewAI](https://github.com/joaomdmoura/crewAI) | Multi-agent orchestration |
| [LangChain](https://langchain.com/) | LLM integration |
| [Google Gemini](https://ai.google.dev/) | Large Language Model (gemini-1.5-pro) |
| [Streamlit](https://streamlit.io/) | Web UI |
| [Serper](https://serper.dev/) | Google Search API |
| [FPDF2](https://pyfpdf.github.io/fpdf2/) | Professional PDF generation |
| [PyPDF](https://pypdf.readthedocs.io/) | Resume PDF text extraction |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | Web scraping support |

## Project Structure

```
job_search_crew/
├── .env                 # API keys (not committed)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── job_crew.py          # CrewAI agents, tasks & crew logic
├── app.py               # Streamlit web interface
└── README.md            # This file
```

## Prerequisites

- Python 3.9+
- Google Gemini API Key
- Serper API Key

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd job_search_crew
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   .\venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure API Keys:**

   Option A - Edit `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

   Option B - Enter keys in the app sidebar (no `.env` needed)

## Getting API Keys

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Serper API Key
1. Go to [serper.dev](https://serper.dev)
2. Sign up for a free account (2,500 free searches)
3. Copy your API key from the dashboard

## Usage

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Configure the sidebar:**
   - Enter your API keys
   - Set job preferences (work type, experience, salary)
   - Choose search depth (Simple or Deep)

4. **Upload your resume:**
   - Click "Upload your resume (PDF)"
   - Select your resume file

5. **Enter job details:**
   - Type your target job title (e.g., "Senior Python Developer")

6. **Click "Kickoff Crew"** and wait for the agents to complete

7. **Review results** in the tabbed interface:
   - Job List: Found opportunities
   - Match Analysis: Keyword gaps and scores
   - Final Documents: Cover letter and resume bullets
   - Full Report: Complete analysis

8. **Download PDFs** using the download buttons in each tab

## Search Modes

| Mode | Description | Speed | Detail Level |
|------|-------------|-------|--------------|
| **Simple** | Uses search result snippets | Fast (2-3 min) | Good |
| **Deep** | Scrapes full job posting pages | Slower (5-8 min) | Comprehensive |

### When to Use Deep Search
- When you need exact tech stack requirements
- To understand company culture and values
- For more accurate ATS keyword matching
- When search snippets lack detail

## Agent Details

### 1. Job Researcher (+ Web Intelligence Specialist in Deep Mode)
- Searches for current job openings using Serper API
- In Deep mode: Scrapes full job posting URLs
- Extracts requirements, skills, salary, and location
- Identifies top 3 recommended positions
- Aggregates skills in demand across all postings
- **Tools**: SerperDevTool, ScrapeWebsiteTool (Deep mode)

### 2. Senior Technical Recruiter & ATS Expert
- Analyzes resume keywords vs job requirements
- Calculates match scores (0-100%) for top jobs
- Identifies critical missing keywords
- Recommends certifications and skills to acquire
- Highlights unique candidate strengths
- **Expertise**: 50,000+ resumes reviewed, ATS algorithm knowledge

### 3. Executive Career Content Strategist
- Creates customizable cover letter templates
- Writes ATS-optimized resume bullet points
- Prepares interview questions with suggested answers
- Optimizes LinkedIn headline and summary
- **Output**: Professional markdown-formatted report

## Output Sections

### Job Application Report
1. **Executive Summary**
   - Best match job with score
   - Overall assessment
   - Key action items

2. **Tailored Cover Letter**
   - Customizable template with placeholders
   - Highlights matching skills
   - Addresses gaps positively

3. **Optimized Resume Bullets**
   - 7-10 ATS-friendly bullet points
   - Action verbs + metrics
   - Missing keywords incorporated

4. **Interview Preparation**
   - 5 likely questions based on job requirements
   - Suggested answers using your experience
   - Key talking points

5. **LinkedIn Optimization**
   - Suggested headline (120 chars)
   - Professional summary
   - Skills to add

## Search History

- Previous searches are saved in your session
- Click any past search in the sidebar to reload results
- Use "Clear History" to reset
- History includes: topic, timestamp, preferences, and full results

## PDF Export Options

| Button | Contents |
|--------|----------|
| Download Job List (PDF) | Job opportunities found |
| Download Analysis (PDF) | Match scores and keyword gaps |
| Download Documents (PDF) | Cover letter and resume bullets |
| Download Report (PDF) | Full report section |
| Download All-in-One PDF | Complete package with cover page and TOC |

## Error Handling

The system includes robust error handling:
- **Blocked websites**: Gracefully falls back to search snippets
- **403 Forbidden**: Continues with available data
- **Timeouts**: Uses cached snippet data
- **SSL errors**: Reports issue and proceeds

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API Key errors | Verify keys are correct and have proper permissions |
| Rate limiting | Wait a few minutes and try again |
| Import errors | Run `pip install -r requirements.txt` |
| Slow response | Normal for Deep mode (5-8 min); Simple mode is faster |
| PDF upload fails | Ensure file is a valid PDF with extractable text |
| Scraping blocked | System auto-falls back to search snippets |
| Empty results | Check API keys and internet connection |

## Dependencies

```
crewai
crewai-tools
langchain-google-genai
streamlit
python-dotenv
pypdf
fpdf2
beautifulsoup4
requests
lxml
```

## Version History

| Version | Features |
|---------|----------|
| v1.0 | Basic job search with 3 agents |
| v2.0 | Job preferences, tabbed UI, structured output |
| v3.0 | Search history, professional PDF export |
| v4.0 | Deep search with web scraping, enhanced error handling |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Ideas for Contribution
- Add more job board integrations
- Implement resume scoring visualization
- Add email notification for saved searches
- Create Docker deployment option

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent framework
- [Google](https://ai.google.dev/) for the Gemini API
- [Streamlit](https://streamlit.io/) for the web framework
- [Serper](https://serper.dev/) for the search API
