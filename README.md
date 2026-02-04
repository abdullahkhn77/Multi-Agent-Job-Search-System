# Multi-Agent Job Search System

A powerful AI-powered job search and resume optimization system built with CrewAI, LangChain, Streamlit, and Google Gemini.

## Overview

This application uses a team of 3 AI agents that work together to:
1. **Research** current job opportunities matching your target role
2. **Analyze** your resume against job requirements
3. **Write** optimized application materials (cover letters, resume bullets, interview tips)

## Features

- **Intelligent Job Search**: Finds relevant job postings using web search
- **Resume Analysis**: Identifies skill matches and gaps
- **Content Generation**: Creates tailored cover letters and resume bullet points
- **Interview Prep**: Provides talking points for interviews
- **LinkedIn Optimization**: Suggests profile improvements
- **Export Results**: Download results as Markdown

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [CrewAI](https://github.com/joaomdmoura/crewAI) | Multi-agent orchestration |
| [LangChain](https://langchain.com/) | LLM integration |
| [Google Gemini](https://ai.google.dev/) | Large Language Model |
| [Streamlit](https://streamlit.io/) | Web UI |
| [Serper](https://serper.dev/) | Google Search API |

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

3. **Enter your API keys** in the sidebar (if not using `.env`)

4. **Fill in the form:**
   - Job Title/Topic (e.g., "Senior Python Developer")
   - Paste your resume content

5. **Click "Kickoff Crew"** and wait for the agents to complete

6. **Review and download** your personalized results

## Agent Details

### 1. Job Researcher
- Searches for current job openings
- Extracts key requirements and qualifications
- Identifies common skills in demand
- Finds 5-7 relevant job postings

### 2. Resume Profiler
- Analyzes your skills and experience
- Compares against job requirements
- Identifies strengths and gaps
- Provides match percentage estimates

### 3. Content Writer
- Creates customizable cover letter templates
- Writes ATS-friendly resume bullet points
- Prepares interview talking points
- Suggests LinkedIn optimizations

## Example Output

The system generates:
- List of relevant job opportunities
- Skills match assessment
- Gap analysis with recommendations
- Professional cover letter template
- Optimized resume bullet points
- Interview preparation tips
- LinkedIn profile suggestions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API Key errors | Verify keys are correct and have proper permissions |
| Rate limiting | Wait a few minutes and try again |
| Import errors | Ensure all dependencies are installed: `pip install -r requirements.txt` |
| Slow response | The crew may take 2-5 minutes to complete all tasks |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent framework
- [Google](https://ai.google.dev/) for the Gemini API
- [Streamlit](https://streamlit.io/) for the web framework
