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
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🔍 Multi-Agent Job Search System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Powered by CrewAI, LangChain & Google Gemini</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("---")

    # API Keys Section
    st.subheader("🔑 API Keys")

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

    # Job Search Preferences Section
    st.subheader("🎯 Job Search Preferences")

    work_type = st.selectbox(
        "Work Arrangement",
        options=["Any", "Remote", "Hybrid", "On-site"],
        index=0,
        help="Select your preferred work arrangement",
    )

    experience_level = st.selectbox(
        "Experience Level",
        options=["Any", "Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior (5-8 years)", "Lead/Principal (8+ years)"],
        index=0,
        help="Select your experience level",
    )

    salary_range = st.selectbox(
        "Expected Salary Range (USD)",
        options=[
            "Not specified",
            "$40,000 - $60,000",
            "$60,000 - $80,000",
            "$80,000 - $100,000",
            "$100,000 - $130,000",
            "$130,000 - $160,000",
            "$160,000 - $200,000",
            "$200,000+",
        ],
        index=0,
        help="Select your expected salary range",
    )

    st.markdown("---")

    # How to Get API Keys
    with st.expander("📚 How to Get API Keys"):
        st.markdown("""
        **Google Gemini:**
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Create a new API key

        **Serper (Google Search):**
        1. Go to [serper.dev](https://serper.dev)
        2. Sign up and get your API key (2,500 free searches)
        """)

    st.markdown("---")

    # About Section
    st.subheader("ℹ️ About")
    st.markdown("""
    This system uses 3 AI agents:
    - **Researcher**: Finds relevant jobs
    - **Profiler**: Technical recruiter analysis
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

    # Display current preferences summary
    st.markdown("---")
    st.subheader("📋 Search Summary")
    pref_col1, pref_col2 = st.columns(2)
    with pref_col1:
        st.markdown(f"**Role:** {job_topic or 'Not specified'}")
        st.markdown(f"**Work Type:** {work_type}")
    with pref_col2:
        st.markdown(f"**Experience:** {experience_level}")
        st.markdown(f"**Salary:** {salary_range}")

with col2:
    st.subheader("🚀 Results")

    # Initialize session state for results
    if "crew_result" not in st.session_state:
        st.session_state.crew_result = None
    if "job_topic_saved" not in st.session_state:
        st.session_state.job_topic_saved = ""

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
                    # Progress indicators
                    progress_placeholder = st.empty()
                    progress_placeholder.info("🔍 **Stage 1/3**: Researcher is searching for jobs...")

                    result = create_crew(
                        topic=job_topic,
                        resume_text=resume_text,
                        gemini_key=gemini_api_key,
                        serper_key=serper_api_key,
                        work_type=work_type,
                        salary_range=salary_range,
                        experience_level=experience_level,
                    )

                    st.session_state.crew_result = result
                    st.session_state.job_topic_saved = job_topic
                    progress_placeholder.empty()
                    st.success("✅ All agents completed successfully!")

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.exception(e)

    # Display results in tabs
    if st.session_state.crew_result:
        st.markdown("---")

        # Create tabs for organized output
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Job List",
            "🔍 Match Analysis",
            "📝 Final Documents",
            "📊 Full Report"
        ])

        result = st.session_state.crew_result

        with tab1:
            st.subheader("Job Opportunities Found")
            if result.get("jobs"):
                st.markdown(result["jobs"])
            else:
                st.info("Job search results will appear here.")

            st.markdown("---")
            st.download_button(
                label="📥 Download Job List",
                data=result.get("jobs", "No data"),
                file_name=f"job_list_{st.session_state.job_topic_saved.replace(' ', '_')}.md",
                mime="text/markdown",
                key="download_jobs"
            )

        with tab2:
            st.subheader("Resume Match Analysis")
            if result.get("analysis"):
                st.markdown(result["analysis"])
            else:
                st.info("Match analysis will appear here.")

            st.markdown("---")
            st.download_button(
                label="📥 Download Analysis",
                data=result.get("analysis", "No data"),
                file_name=f"match_analysis_{st.session_state.job_topic_saved.replace(' ', '_')}.md",
                mime="text/markdown",
                key="download_analysis"
            )

        with tab3:
            st.subheader("Application Documents")
            if result.get("documents"):
                st.markdown(result["documents"])
            else:
                st.info("Cover letter and resume bullets will appear here.")

            st.markdown("---")
            st.download_button(
                label="📥 Download Documents",
                data=result.get("documents", "No data"),
                file_name=f"application_docs_{st.session_state.job_topic_saved.replace(' ', '_')}.md",
                mime="text/markdown",
                key="download_docs"
            )

        with tab4:
            st.subheader("Complete Report")
            if result.get("full_report"):
                with st.expander("View Full Report", expanded=True):
                    st.markdown(result["full_report"])
            else:
                st.info("Full report will appear here.")

            st.markdown("---")
            st.download_button(
                label="📥 Download Full Report",
                data=result.get("full_report", "No data"),
                file_name=f"full_report_{st.session_state.job_topic_saved.replace(' ', '_')}.md",
                mime="text/markdown",
                key="download_full"
            )

        # Raw output option
        with st.expander("🔧 View Raw Output (Debug)"):
            st.code(str(result), language="python")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 1rem;'>
        Built with CrewAI, LangChain, Streamlit & Google Gemini<br>
        <small>Multi-Agent Job Search System v2.0</small>
    </div>
    """,
    unsafe_allow_html=True,
)
