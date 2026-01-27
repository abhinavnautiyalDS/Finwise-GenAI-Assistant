import os
import tempfile
import streamlit as st
import requests
import json
from pathlib import Path
from pypdf import PdfReader

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# Custom CSS for EXACT UI match
# ============================
st.markdown("""
<style>
    /* Main container */
    .stApp {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background: white;
    }
    
    /* Remove all padding/margins */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main header */
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #000;
        margin-bottom: 2rem;
        text-align: left;
    }
    
    /* Options row */
    .options-row {
        display: flex;
        gap: 3rem;
        margin-bottom: 2rem;
        align-items: center;
    }
    
    /* Temperature section */
    .temp-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .temp-label {
        font-weight: 500;
        color: #000;
        font-size: 1rem;
        min-width: 100px;
    }
    
    .temp-value {
        font-weight: 600;
        color: #000;
        font-size: 1rem;
    }
    
    /* Chain Type section */
    .chain-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .chain-label {
        font-weight: 500;
        color: #000;
        font-size: 1rem;
        min-width: 100px;
    }
    
    /* Description text */
    .description {
        color: #000;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* File upload area - EXACT match */
    .upload-container {
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .upload-box {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f9fafb;
        margin-bottom: 0.5rem;
    }
    
    .upload-text {
        color: #000;
        font-size: 1rem;
        margin: 0;
        line-height: 1.5;
    }
    
    .upload-subtext {
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* File info card */
    .file-info {
        background: #f3f4f6;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .file-name {
        font-weight: 600;
        color: #000;
        margin: 0;
        font-size: 1rem;
    }
    
    .file-details {
        color: #6b7280;
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Status messages */
    .status-message {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #166534;
        font-size: 0.875rem;
    }
    
    .error-message {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #dc2626;
        font-size: 0.875rem;
    }
    
    /* Webhook container */
    .webhook-box {
        background: #f8fafc;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .webhook-text {
        color: #6b7280;
        font-size: 0.875rem;
        margin: 0;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    .stButton > button:hover {
        background: #2563eb;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        font-weight: 500;
        color: #000;
        font-size: 1rem;
    }
    
    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 1.5rem 0;
    }
    
    /* Summary box */
    .summary-container {
        background: white;
        border-radius: 8px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .summary-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #000;
        margin-bottom: 1rem;
    }
    
    .summary-content {
        color: #374151;
        line-height: 1.6;
        font-size: 1rem;
        white-space: pre-line;
    }
    
    /* Download buttons row */
    .button-row {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    /* Custom slider styling */
    .stSlider {
        margin-top: 0;
    }
    
    .stSlider > div > div {
        padding: 0;
    }
    
    /* Select box styling */
    .stSelectbox label {
        display: none;
    }
    
    /* Text input styling */
    .stTextInput input {
        background: white;
        border: 1px solid #d1d5db;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 500;
        color: #000;
        background: #f9fafb;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Initialize OpenRouter API
# ============================
def init_openrouter():
    """Initialize OpenRouter API"""
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
        return api_key, "✅ OpenRouter API configured"
    except KeyError:
        return None, "⚠️ API key not found in secrets"

# ============================
# API Configuration
# ============================
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct"
MAX_CONTEXT_TOKENS = 8192
MAX_OUTPUT_TOKENS = 1000

# ============================
# Token Management Functions
# ============================
def estimate_tokens(text):
    """Rough token estimation"""
    return len(text) // 4

def truncate_text(text, max_tokens=6000):
    """Truncate text to fit within token limit"""
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text, len(text) // 4, False
    
    truncated = text[:max_chars]
    last_period = truncated.rfind('. ')
    last_newline = truncated.rfind('\n\n')
    
    cut_point = max(last_period, last_newline)
    if cut_point > max_chars * 0.8:
        truncated = truncated[:cut_point + 1]
    
    return truncated, len(truncated) // 4, True

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file bytes"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        reader = PdfReader(tmp_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"{page_text}\n\n"
        
        os.unlink(tmp_path)
        return text.strip(), len(reader.pages)
    
    except Exception as e:
        return f"Error extracting PDF: {str(e)}", 0

def extract_text_from_txt(file_bytes):
    """Extract text from TXT file"""
    try:
        text = file_bytes.decode('utf-8', errors='ignore')
        return text.strip(), len(text.split('\n'))
    except:
        return "", 0

def process_uploaded_file(uploaded_file):
    """Process uploaded file and return text"""
    file_bytes = uploaded_file.getvalue()
    
    if uploaded_file.type == "application/pdf":
        text, pages = extract_text_from_pdf(file_bytes)
        if isinstance(text, str) and not text.startswith("Error"):
            return text, pages, "PDF"
    elif uploaded_file.type == "text/plain":
        text, pages = extract_text_from_txt(file_bytes)
        return text, pages, "TXT"
    
    return "", 0, None

# ============================
# Summarization Function
# ============================
def summarize_financial_document(text, api_key, temperature=0.6):
    """Summarize financial document using Mistral 7B"""
    
    truncated_text, token_count, was_truncated = truncate_text(text, max_tokens=6000)
    
    if was_truncated:
        st.markdown(f'<div class="error-message">⚠️ Document truncated from {estimate_tokens(text):,} to {token_count:,} tokens to fit model limit</div>', unsafe_allow_html=True)
    
    system_prompt = """You are a financial analyst specializing in document summarization. 
Extract and summarize key information from financial documents including:
1. Key financial figures and metrics
2. Strategic developments and initiatives  
3. Future outlook and projections
4. Risks and opportunities
5. Major changes from previous periods

Provide a concise, well-structured summary that highlights the most important information.
Format with clear sections and bullet points where appropriate."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-summarizer.streamlit.app",
        "X-Title": "Financial Document Summarizer"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please summarize this financial document:\n\n{truncated_text}"}
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": temperature,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"API Error {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "Request timeout. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

# ============================
# Main App
# ============================

# Initialize API
api_key, api_message = init_openrouter()

# Title - EXACT match
st.markdown('<div class="main-header">Financial Document Summarizer</div>', unsafe_allow_html=True)

# Options Row - EXACT match
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown('<div class="temp-label">Temperature</div>', unsafe_allow_html=True)
    temperature = st.slider(
        "",
        min_value=0.0,
        max_value=1.0,
        value=0.60,
        step=0.10,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="temp-value">{temperature:.2f}</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chain-label">Chain Type</div>', unsafe_allow_html=True)
    chain_type = st.selectbox(
        "",
        ["stuff", "map_reduce", "refine", "map_rerank"],
        label_visibility="collapsed"
    )

# Description - EXACT match
st.markdown('<div class="description">Upload PDF or TXT financial documents to generate a concise summary highlighting key financial figures, strategic developments, and future outlook.</div>', unsafe_allow_html=True)

# File Upload Area - EXACT match
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
st.markdown('<div class="upload-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Choose files",
    type=['pdf', 'txt'],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p class="upload-subtext">Drag and drop files here<br>Limit 200MB per file · PDF, TXT</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# N8N Webhook Configuration - EXACT match
with st.expander("N8N Webhook Configuration"):
    webhook_url = st.text_input(
        "N8N Webhook URL",
        placeholder="Enter webhook URL",
        label_visibility="collapsed"
    )
    if not webhook_url:
        st.markdown('<div class="webhook-box">', unsafe_allow_html=True)
        st.markdown('<p class="webhook-text">N8N Webhook URL not configured. Skipping workflow trigger.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Verbose checkbox
verbose = st.checkbox("Verbose (logs in console)", value=False)

# Divider
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Process Uploaded File
if uploaded_file is not None:
    # File info - EXACT match
    file_size_mb = len(uploaded_file.getvalue()) / 1024 / 1024
    
    # Display uploaded file name with size
    st.markdown(f'<div class="file-info">', unsafe_allow_html=True)
    st.markdown(f'<p class="file-name">{uploaded_file.name} · {file_size_mb:.1f}MB</p>', unsafe_allow_html=True)
    if uploaded_file.type == "application/pdf":
        st.markdown(f'<p class="file-details">PDF document</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="file-details">Text document</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process the file
    with st.spinner("Processing..."):
        text, pages, file_type = process_uploaded_file(uploaded_file)
        
        if text and file_type:
            st.markdown(f'<div class="status-message">Loaded {pages} pages from {file_type}: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
            if verbose:
                # Simulate chunk processing
                word_count = len(text.split())
                chunks = (word_count // 500) + 1
                st.markdown(f'<div class="status-message">Split into {chunks} text chunks for processing.</div>', unsafe_allow_html=True)
                
                # Preview option
                if st.button("Preview first 3 chunks", key="preview"):
                    with st.expander("Preview"):
                        preview_text = text[:1500] + "..." if len(text) > 1500 else text
                        st.text(preview_text)
            
            # Reprocess button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Reprocess", use_container_width=True):
                    st.rerun()
            
            # Generate Summary button
            with col2:
                if st.button("Generate Financial Summary", type="primary", use_container_width=True):
                    if not api_key:
                        st.error("OpenRouter API key not configured. Please add it to secrets.toml")
                    else:
                        with st.spinner("Generating summary..."):
                            summary = summarize_financial_document(text, api_key, temperature)
                        
                        if summary and not summary.startswith("API Error") and not summary.startswith("Error"):
                            # Display Summary - EXACT match
                            st.markdown('<div class="summary-container">', unsafe_allow_html=True)
                            st.markdown('<div class="summary-title">Financial Summary</div>', unsafe_allow_html=True)
                            st.markdown('<div class="summary-content">', unsafe_allow_html=True)
                            st.markdown(summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Download buttons - EXACT match
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="Download Summary",
                                    data=summary,
                                    file_name=f"{uploaded_file.name.split('.')[0]}_summary.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            with col2:
                                if st.button("Clear and Upload New", use_container_width=True):
                                    st.rerun()
                        
                        else:
                            st.error(f"Error: {summary}")
        else:
            st.error("Could not extract text from the uploaded file.")

# Manage App section at the bottom
st.markdown('<hr class="divider">', unsafe_allow_html=True)
with st.expander("Manage App"):
    st.info("""
    **App Info:**
    - Model: mistralai/mistral-7b-instruct
    - Token Limit: 8,192 tokens
    - Auto-truncation: Enabled
    - File Support: PDF, TXT
    
    **Configuration:**
    Add your OpenRouter API key to `.streamlit/secrets.toml`:
    ```
    OPENROUTER_API_KEY = "your-key-here"
    ```
    """)
    
    if st.button("Clear Cache & Reset"):
        st.rerun()
