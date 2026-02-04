"""
Multi-Agent Job Search System - Streamlit UI
A web interface for the CrewAI-powered job search and resume optimization system.
"""

import streamlit as st
from dotenv import load_dotenv
import os
import re
import io
from datetime import datetime
from pypdf import PdfReader
from fpdf import FPDF

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


class ProfessionalPDF(FPDF):
    """Custom PDF class with professional styling."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Add header to each page."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Job Application Report | Multi-Agent Job Search System", align="C")
        self.ln(5)
        self.set_draw_color(30, 136, 229)
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(10)

    def footer(self):
        """Add footer with page number."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")

    def chapter_title(self, title: str):
        """Add a chapter title with styling."""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 136, 229)
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(30, 136, 229)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(5)

    def section_title(self, title: str):
        """Add a section title."""
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, title, ln=True)
        self.ln(2)

    def body_text(self, text: str):
        """Add body text with proper encoding."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        # Handle encoding issues
        clean_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, clean_text)
        self.ln(3)

    def bullet_point(self, text: str):
        """Add a bullet point."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        clean_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.cell(5, 6, chr(149))  # Bullet character
        self.multi_cell(0, 6, clean_text)


def export_to_pdf(content: str, title: str = "Job Application Report") -> bytes:
    """
    Convert markdown content to a professional PDF.

    Args:
        content: Markdown content from the agents
        title: Title for the PDF document

    Returns:
        PDF file as bytes
    """
    pdf = ProfessionalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Add main title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 136, 229)
    pdf.cell(0, 15, title, ln=True, align="C")
    pdf.ln(10)

    # Process markdown content
    lines = content.split('\n')
    current_section = ""

    for line in lines:
        line = line.strip()

        if not line:
            pdf.ln(3)
            continue

        # Handle headers
        if line.startswith('# '):
            pdf.chapter_title(line[2:])
        elif line.startswith('## '):
            pdf.chapter_title(line[3:])
        elif line.startswith('### '):
            pdf.section_title(line[4:])
        elif line.startswith('#### '):
            pdf.section_title(line[5:])
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            pdf.bullet_point(line[2:])
        elif re.match(r'^\d+\.', line):
            # Numbered list
            pdf.bullet_point(line)
        # Handle bold text (simplified)
        elif line.startswith('**') and line.endswith('**'):
            pdf.section_title(line.strip('*'))
        # Handle horizontal rules
        elif line == '---' or line == '***':
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        else:
            # Regular text - remove markdown formatting
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Bold
            clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)  # Italic
            clean_line = re.sub(r'`(.*?)`', r'\1', clean_line)  # Code
            pdf.body_text(clean_line)

    # Return PDF as bytes
    return pdf.output()


def export_full_report_pdf(result: dict, job_topic: str) -> bytes:
    """
    Export all sections as a comprehensive PDF report.

    Args:
        result: Dictionary containing all crew results
        job_topic: The job title/topic searched

    Returns:
        PDF file as bytes
    """
    pdf = ProfessionalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Cover page
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(30, 136, 229)
    pdf.ln(40)
    pdf.cell(0, 20, "Job Application Report", ln=True, align="C")

    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Position: {job_topic}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True, align="C")

    pdf.ln(30)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 6, "This report was generated by the Multi-Agent Job Search System using AI-powered analysis of job postings and resume matching.", align="C")

    # Table of Contents
    pdf.add_page()
    pdf.chapter_title("Table of Contents")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    sections = [
        "1. Job Opportunities Found",
        "2. Resume Match Analysis",
        "3. Application Documents",
        "4. Complete Report"
    ]
    for section in sections:
        pdf.cell(0, 10, section, ln=True)

    # Section 1: Jobs
    pdf.add_page()
    pdf.chapter_title("1. Job Opportunities Found")
    if result.get("jobs"):
        process_markdown_to_pdf(pdf, result["jobs"])

    # Section 2: Analysis
    pdf.add_page()
    pdf.chapter_title("2. Resume Match Analysis")
    if result.get("analysis"):
        process_markdown_to_pdf(pdf, result["analysis"])

    # Section 3: Documents
    pdf.add_page()
    pdf.chapter_title("3. Application Documents")
    if result.get("documents"):
        process_markdown_to_pdf(pdf, result["documents"])

    # Section 4: Full Report
    pdf.add_page()
    pdf.chapter_title("4. Complete Report")
    if result.get("full_report"):
        process_markdown_to_pdf(pdf, result["full_report"])

    return pdf.output()


def process_markdown_to_pdf(pdf: ProfessionalPDF, content: str):
    """Process markdown content and add to PDF."""
    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            pdf.ln(2)
            continue

        if line.startswith('# '):
            pdf.section_title(line[2:])
        elif line.startswith('## '):
            pdf.section_title(line[3:])
        elif line.startswith('### '):
            pdf.section_title(line[4:])
        elif line.startswith('- ') or line.startswith('* '):
            pdf.bullet_point(line[2:])
        elif re.match(r'^\d+\.', line):
            pdf.bullet_point(line)
        elif line == '---' or line == '***':
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
        else:
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
            clean_line = re.sub(r'`(.*?)`', r'\1', clean_line)
            pdf.body_text(clean_line)


# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Job Search System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "crew_result" not in st.session_state:
    st.session_state.crew_result = None
if "job_topic_saved" not in st.session_state:
    st.session_state.job_topic_saved = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "selected_history_index" not in st.session_state:
    st.session_state.selected_history_index = None

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
    .history-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        background-color: #f0f2f6;
        cursor: pointer;
    }
    .history-item:hover {
        background-color: #e0e2e6;
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

    # Search History Section
    st.subheader("📜 Search History")

    if st.session_state.search_history:
        st.caption(f"{len(st.session_state.search_history)} previous search(es)")

        for idx, history_item in enumerate(reversed(st.session_state.search_history)):
            actual_idx = len(st.session_state.search_history) - 1 - idx
            timestamp = history_item.get("timestamp", "")
            topic = history_item.get("topic", "Unknown")

            # Create a button for each history item
            if st.button(
                f"🔹 {topic[:25]}{'...' if len(topic) > 25 else ''}",
                key=f"history_{actual_idx}",
                help=f"Searched on {timestamp}\nClick to view results",
                use_container_width=True,
            ):
                st.session_state.selected_history_index = actual_idx
                st.session_state.crew_result = history_item.get("result")
                st.session_state.job_topic_saved = topic
                st.toast(f"📂 Loaded: {topic}", icon="✅")
                st.rerun()

        st.markdown("---")

        # Clear History Button
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            st.session_state.search_history = []
            st.session_state.selected_history_index = None
            st.session_state.crew_result = None
            st.session_state.job_topic_saved = ""
            st.toast("History cleared!", icon="🗑️")
            st.rerun()
    else:
        st.caption("No previous searches yet.")
        st.info("Your search history will appear here after running a search.")

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

    # Show if viewing from history
    if st.session_state.selected_history_index is not None:
        st.info(f"📂 Viewing saved search: **{st.session_state.job_topic_saved}**")

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
                    st.session_state.selected_history_index = None

                    # Add to history
                    history_entry = {
                        "topic": job_topic,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "work_type": work_type,
                        "experience_level": experience_level,
                        "salary_range": salary_range,
                        "result": result,
                    }
                    st.session_state.search_history.append(history_entry)

                    progress_placeholder.empty()
                    st.success("✅ All agents completed successfully!")
                    st.toast("Search complete! Results ready.", icon="🎉")

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

            # PDF Download for Jobs
            if result.get("jobs"):
                pdf_bytes = export_to_pdf(result["jobs"], f"Job List - {st.session_state.job_topic_saved}")
                st.download_button(
                    label="📥 Download Job List (PDF)",
                    data=pdf_bytes,
                    file_name=f"job_list_{st.session_state.job_topic_saved.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="download_jobs_pdf",
                    on_click=lambda: st.toast("PDF ready for download!", icon="📄"),
                )

        with tab2:
            st.subheader("Resume Match Analysis")
            if result.get("analysis"):
                st.markdown(result["analysis"])
            else:
                st.info("Match analysis will appear here.")

            st.markdown("---")

            # PDF Download for Analysis
            if result.get("analysis"):
                pdf_bytes = export_to_pdf(result["analysis"], f"Match Analysis - {st.session_state.job_topic_saved}")
                st.download_button(
                    label="📥 Download Analysis (PDF)",
                    data=pdf_bytes,
                    file_name=f"match_analysis_{st.session_state.job_topic_saved.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="download_analysis_pdf",
                    on_click=lambda: st.toast("PDF ready for download!", icon="📄"),
                )

        with tab3:
            st.subheader("Application Documents")
            if result.get("documents"):
                st.markdown(result["documents"])
            else:
                st.info("Cover letter and resume bullets will appear here.")

            st.markdown("---")

            # PDF Download for Documents
            if result.get("documents"):
                pdf_bytes = export_to_pdf(result["documents"], f"Application Documents - {st.session_state.job_topic_saved}")
                st.download_button(
                    label="📥 Download Documents (PDF)",
                    data=pdf_bytes,
                    file_name=f"application_docs_{st.session_state.job_topic_saved.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="download_docs_pdf",
                    on_click=lambda: st.toast("PDF ready for download!", icon="📄"),
                )

        with tab4:
            st.subheader("Complete Report")
            if result.get("full_report"):
                with st.expander("View Full Report", expanded=True):
                    st.markdown(result["full_report"])
            else:
                st.info("Full report will appear here.")

            st.markdown("---")

            # Professional Full Report PDF
            col_pdf1, col_pdf2 = st.columns(2)

            with col_pdf1:
                if result.get("full_report"):
                    pdf_bytes = export_to_pdf(result["full_report"], f"Complete Report - {st.session_state.job_topic_saved}")
                    st.download_button(
                        label="📥 Download Report (PDF)",
                        data=pdf_bytes,
                        file_name=f"full_report_{st.session_state.job_topic_saved.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key="download_full_pdf",
                        on_click=lambda: st.toast("PDF ready for download!", icon="📄"),
                    )

            with col_pdf2:
                # Comprehensive PDF with all sections
                pdf_bytes = export_full_report_pdf(result, st.session_state.job_topic_saved)
                st.download_button(
                    label="📥 Download All-in-One PDF",
                    data=pdf_bytes,
                    file_name=f"complete_package_{st.session_state.job_topic_saved.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key="download_complete_pdf",
                    on_click=lambda: st.toast("Complete PDF package ready!", icon="📦"),
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
        <small>Multi-Agent Job Search System v3.0</small>
    </div>
    """,
    unsafe_allow_html=True,
)
