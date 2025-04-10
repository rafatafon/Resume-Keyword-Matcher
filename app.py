"""
AI Resume Keyword Matcher - Streamlit Application

This application helps job seekers optimize their resumes by comparing them
to job descriptions and identifying matching and missing keywords.
"""
import os
import tempfile
from typing import Tuple

import streamlit as st
import PyPDF2
from utils.keyword_utils import analyze_resume_job_match

# Set page configuration
st.set_page_config(
    page_title="AI Resume Keyword Matcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B8BBE;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #306998;
        margin-bottom: 1rem;
    }
    .match-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #4B8BBE;
        margin: 1rem 0;
    }
    .keyword-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .matched-keyword {
        display: inline-block;
        background-color: #d1e7dd;
        color: #0a3622;
        border-radius: 15px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .missing-keyword {
        display: inline-block;
        background-color: #f8d7da;
        color: #842029;
        border-radius: 15px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .suggestion-box {
        background-color: #cff4fc;
        color: #055160;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
    .file-upload-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .divider {
        margin: 2rem 0;
        border-top: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: The uploaded PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(pdf_file.getvalue())
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    return text

def process_uploaded_files() -> Tuple[str, str]:
    """
    Process the uploaded resume and job description files.
    
    Returns:
        Tuple containing the resume text and job description text
    """
    resume_text = ""
    job_text = ""
    
    # File upload section
    st.markdown('<div class="file-upload-container">', unsafe_allow_html=True)
    
    # Resume upload
    st.subheader("Upload Your Resume")
    resume_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    
    # Job description upload
    st.subheader("Upload Job Description")
    job_file = st.file_uploader("Upload the job description (PDF or TXT)", type=["pdf", "txt"])
    
    # Text area alternatives
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Or Paste Your Resume")
        resume_text_input = st.text_area("", height=200, placeholder="Paste your resume text here...")
        
    with col2:
        st.subheader("Or Paste Job Description")
        job_text_input = st.text_area("", height=200, placeholder="Paste the job description text here...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process resume
    if resume_file is not None:
        if resume_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_file)
        else:  # txt file
            resume_text = resume_file.getvalue().decode("utf-8")
    elif resume_text_input:
        resume_text = resume_text_input
    
    # Process job description
    if job_file is not None:
        if job_file.type == "application/pdf":
            job_text = extract_text_from_pdf(job_file)
        else:  # txt file
            job_text = job_file.getvalue().decode("utf-8")
    elif job_text_input:
        job_text = job_text_input
    
    # Load sample data if available and no files are uploaded
    if not resume_text and not job_text:
        try:
            sample_resume_path = os.path.join("data", "sample_resume.txt")
            sample_job_path = os.path.join("data", "sample_job.txt")
            
            if os.path.exists(sample_resume_path) and os.path.exists(sample_job_path):
                use_samples = st.checkbox("Use sample resume and job description for demonstration")
                
                if use_samples:
                    with open(sample_resume_path, "r") as f:
                        resume_text = f.read()
                    
                    with open(sample_job_path, "r") as f:
                        job_text = f.read()
                    
                    st.success("Loaded sample resume and job description!")
        except Exception as e:
            st.warning(f"Could not load sample data: {e}")
    
    return resume_text, job_text

def display_results(results):
    """
    Display the analysis results in a visually appealing way.
    
    Args:
        results: Dictionary containing match score and keyword information
    """
    # Match score
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Match Score</p>', unsafe_allow_html=True)
    
    score = results["match_score"]
    score_color = "#4CAF50" if score >= 70 else "#FFC107" if score >= 50 else "#F44336"
    
    st.markdown(
        f'<div class="match-score" style="color: {score_color}">{score}%</div>',
        unsafe_allow_html=True
    )
    
    # Display matched keywords
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="sub-header">Matched Keywords</p>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-box">', unsafe_allow_html=True)
        
        if results["matched_keywords"]:
            keywords_html = ""
            for keyword in sorted(results["matched_keywords"]):
                keywords_html += f'<span class="matched-keyword">{keyword}</span>'
            st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.write("No matching keywords found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display missing keywords
    with col2:
        st.markdown('<p class="sub-header">Missing Keywords</p>', unsafe_allow_html=True)
        st.markdown('<div class="keyword-box">', unsafe_allow_html=True)
        
        if results["missing_keywords"]:
            keywords_html = ""
            for keyword in sorted(results["missing_keywords"]):
                keywords_html += f'<span class="missing-keyword">{keyword}</span>'
            st.markdown(keywords_html, unsafe_allow_html=True)
        else:
            st.write("No missing keywords! Your resume covers all important keywords.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display suggestions
    st.markdown('<p class="sub-header">Suggestions for Improvement</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="suggestion-box">{results["suggestions"]}</div>',
        unsafe_allow_html=True
    )

def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🔍 AI Resume Keyword Matcher</h1>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
    Optimize your resume for Applicant Tracking Systems (ATS) by comparing it with job descriptions.
    This tool identifies matching and missing keywords to help you tailor your resume for specific job applications.
    """)
    
    # Process uploaded files
    resume_text, job_text = process_uploaded_files()
    
    # Analyze button
    if st.button("Analyze Match", type="primary", disabled=not (resume_text and job_text)):
        with st.spinner("Analyzing your resume against the job description..."):
            # Perform analysis
            results = analyze_resume_job_match(resume_text, job_text)
            
            # Display results
            display_results(results)
    
    # Show error if only one file is provided
    elif resume_text and not job_text:
        st.warning("Please provide a job description to analyze.")
    elif job_text and not resume_text:
        st.warning("Please provide your resume to analyze.")
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
        AI Resume Keyword Matcher | Built with Streamlit and spaCy
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
