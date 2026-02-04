"""
Multi-Agent Job Search System - Streamlit UI
A web interface for the CrewAI-powered job search and resume optimization system.
"""

import streamlit as st
from dotenv import load_dotenv
import os
from pypdf import PdfReader

from job_crew import create_crew


def get_pdf_text(uploaded_file) -> str:
    """
    Extract text content from an uploaded PDF file.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Extracted text from all pages of the PDF
    """
    text = ""
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Job Search System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F5E9;
        border: 1px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🔍 Multi-Agent Job Search System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Powered by CrewAI, LangChain & Google Gemini</p>', unsafe_allow_html=True)

# Sidebar for API Keys
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("---")

    st.subheader("🔑 API Keys")

    # Get API keys from environment or user input
    default_gemini_key = os.getenv("GOOGLE_API_KEY", "")
    default_serper_key = os.getenv("SERPER_API_KEY", "")

    gemini_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=default_gemini_key,
        help="Get your API key from Google AI Studio",
    )

    serper_api_key = st.text_input(
        "Serper API Key",
        type="password",
        value=default_serper_key,
        help="Get your API key from serper.dev",
    )

    st.markdown("---")

    st.subheader("📚 How to Get API Keys")
    st.markdown("""
    **Google Gemini:**
    1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Create a new API key

    **Serper (Google Search):**
    1. Go to [serper.dev](https://serper.dev)
    2. Sign up and get your API key
    """)

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.markdown("""
    This system uses 3 AI agents:
    - **Researcher**: Finds relevant jobs
    - **Profiler**: Analyzes your resume
    - **Writer**: Creates application materials
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 Job Search Details")

    job_topic = st.text_input(
        "Job Title / Topic",
        placeholder="e.g., Senior Python Developer, Data Scientist, Product Manager",
        help="Enter the job title or role you're looking for",
    )

    st.subheader("📄 Your Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"],
        help="Upload your resume in PDF format for analysis",
    )

    # Extract text from PDF and show confirmation
    resume_text = ""
    if uploaded_file is not None:
        resume_text = get_pdf_text(uploaded_file)
        st.success(f"✅ Resume Loaded: {uploaded_file.name}")
        with st.expander("Preview extracted text"):
            st.text(resume_text[:2000] + "..." if len(resume_text) > 2000 else resume_text)

with col2:
    st.subheader("🚀 Results")

    # Initialize session state for results
    if "crew_result" not in st.session_state:
        st.session_state.crew_result = None

    # Kickoff button
    if st.button("🔥 Kickoff Crew", type="primary"):
        # Validation
        if not gemini_api_key:
            st.error("❌ Please enter your Google Gemini API Key in the sidebar.")
        elif not serper_api_key:
            st.error("❌ Please enter your Serper API Key in the sidebar.")
        elif not job_topic:
            st.error("❌ Please enter a job title or topic.")
        elif not resume_text:
            st.error("❌ Please upload your resume PDF.")
        else:
            # Run the crew
            with st.spinner("🤖 Agents are working... This may take a few minutes."):
                try:
                    st.info("🔍 **Researcher** is searching for jobs...")

                    result = create_crew(
                        topic=job_topic,
                        resume_text=resume_text,
                        gemini_key=gemini_api_key,
                        serper_key=serper_api_key,
                    )

                    st.session_state.crew_result = result
                    st.success("✅ Crew completed successfully!")

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.exception(e)

    # Display results
    if st.session_state.crew_result:
        st.markdown("---")
        st.subheader("📋 Agent Output")

        # Display the result in a nice format
        with st.container():
            st.markdown(st.session_state.crew_result)

        st.markdown("---")

        # Download button
        st.download_button(
            label="📥 Download Results as Markdown",
            data=st.session_state.crew_result,
            file_name=f"job_search_results_{job_topic.replace(' ', '_')}.md",
            mime="text/markdown",
        )

        # Copy button alternative
        st.code(st.session_state.crew_result, language="markdown")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 1rem;'>
        Built with CrewAI, LangChain, Streamlit & Google Gemini<br>
        <small>Multi-Agent Job Search System v1.0</small>
    </div>
    """,
    unsafe_allow_html=True,
)
