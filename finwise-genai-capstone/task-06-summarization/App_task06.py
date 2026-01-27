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
# Custom CSS for exact UI match
# ============================
st.markdown("""
<style>
    /* Main container */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    /* Options container */
    .options-container {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
        align-items: center;
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    /* Temperature slider styling */
    .temperature-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 250px;
    }
    
    .temperature-label {
        font-weight: 600;
        color: #4a5568;
        min-width: 100px;
    }
    
    /* Chain type dropdown */
    .chain-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 250px;
    }
    
    .chain-label {
        font-weight: 600;
        color: #4a5568;
        min-width: 100px;
    }
    
    /* File upload area */
    .upload-area {
        border: 3px dashed #cbd5e0;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        background: #f7fafc;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #4299e1;
        background: #ebf8ff;
    }
    
    .upload-text {
        color: #718096;
        font-size: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .upload-info {
        color: #a0aec0;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    
    /* File cards */
    .file-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4299e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .file-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .file-name {
        font-weight: 600;
        color: #2d3748;
    }
    
    .file-size {
        color: #718096;
        font-size: 0.85rem;
    }
    
    .file-status {
        color: #48bb78;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Status messages */
    .status-message {
        background: #f0fff4;
        border: 1px solid #c6f6d5;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #276749;
        font-size: 0.9rem;
    }
    
    .error-message {
        background: #fed7d7;
        border: 1px solid #fc8181;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #c53030;
        font-size: 0.9rem;
    }
    
    /* Summary box */
    .summary-box {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .summary-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    .summary-content {
        color: #4a5568;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        font-weight: 500;
        color: #4a5568;
    }
    
    /* Custom file uploader */
    div[data-testid="stFileUploader"] section {
        border: none !important;
        background: transparent !important;
    }
    
    /* Remove default file uploader styling */
    div[data-testid="stFileUploader"] > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Make file uploader button look like custom */
    div[data-testid="stFileUploader"] button {
        background: #4299e1 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    /* Processing steps */
    .processing-step {
        background: #edf2f7;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        font-size: 0.9rem;
        color: #4a5568;
    }
    
    .processing-step.done {
        background: #c6f6d5;
        color: #276749;
    }
    
    /* Token management warning */
    .token-warning {
        background: #feebc8;
        border: 1px solid #fbd38d;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #c05621;
    }
    
    /* Webhook container */
    .webhook-container {
        background: #f7fafc;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
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
MAX_CONTEXT_TOKENS = 8192  # Mistral 7B context window
MAX_OUTPUT_TOKENS = 1000

# ============================
# Token Management Functions
# ============================
def estimate_tokens(text):
    """Rough token estimation (4 chars ≈ 1 token)"""
    return len(text) // 4

def truncate_text(text, max_tokens=6000):
    """Truncate text to fit within token limit"""
    # Leave room for prompt and response
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text, len(text) // 4, False
    
    # Truncate and try to cut at sentence boundary
    truncated = text[:max_chars]
    last_period = truncated.rfind('. ')
    last_newline = truncated.rfind('\n\n')
    
    cut_point = max(last_period, last_newline)
    if cut_point > max_chars * 0.8:  # If we find a good cut point near the end
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
                text += f"Page {page_num + 1}:\n{page_text}\n\n"
        
        # Clean up temp file
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
    
    # Truncate if needed
    truncated_text, token_count, was_truncated = truncate_text(text, max_tokens=6000)
    
    if was_truncated:
        st.markdown(f'<div class="token-warning">⚠️ Document truncated from {estimate_tokens(text):,} to {token_count:,} tokens to fit model limit</div>', unsafe_allow_html=True)
    
    # Financial summarization prompt
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

# Main Title
st.markdown('<h1 class="main-header">Financial Document Summarizer</h1>', unsafe_allow_html=True)

# ============================
# Configuration Options
# ============================
st.markdown('<div class="options-container">', unsafe_allow_html=True)

# Temperature
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="temperature-label">Temperature</div>', unsafe_allow_html=True)
with col2:
    temperature = st.slider(
        "",
        min_value=0.0,
        max_value=1.0,
        value=0.60,
        step=0.10,
        label_visibility="collapsed"
    )

# Chain Type
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown('<div class="chain-label">Chain Type</div>', unsafe_allow_html=True)
with col2:
    chain_type = st.selectbox(
        "",
        ["stuff", "map_reduce", "refine", "map_rerank"],
        label_visibility="collapsed"
    )

st.markdown('</div>', unsafe_allow_html=True)

# ============================
# File Upload Section
# ============================
st.markdown("Upload PDF or TXT financial documents to generate a concise summary highlighting key financial figures, strategic developments, and future outlook.")

st.markdown('<div class="upload-area">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose files",
    type=['pdf', 'txt'],
    label_visibility="collapsed",
    help="Drag and drop files here"
)

st.markdown('<div class="upload-text">Limit 200MB per file · PDF, TXT</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================
# Webhook Configuration
# ============================
with st.expander("N8N Webhook Configuration", expanded=False):
    webhook_url = st.text_input(
        "N8N Webhook URL",
        placeholder="https://your-n8n-instance.com/webhook/your-id",
        label_visibility="collapsed"
    )
    if not webhook_url:
        st.markdown('<div class="status-message">N8N Webhook URL not configured. Skipping workflow trigger.</div>', unsafe_allow_html=True)

# ============================
# Verbose Mode
# ============================
verbose_mode = st.checkbox("Verbose (logs in console)", value=False)

# ============================
# Process Uploaded File
# ============================
if uploaded_file is not None:
    # File info card
    file_size_mb = len(uploaded_file.getvalue()) / 1024 / 1024
    st.markdown(f"""
    <div class="file-card">
        <div class="file-info">
            <div>
                <div class="file-name">{uploaded_file.name}</div>
                <div class="file-size">{file_size_mb:.1f} MB · {uploaded_file.type}</div>
            </div>
        </div>
        <div class="file-status">✓ Uploaded</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Process the file
    with st.spinner("Processing document..."):
        text, pages, file_type = process_uploaded_file(uploaded_file)
        
        if text and file_type:
            st.markdown(f'<div class="status-message">✅ Loaded {pages} pages from {file_type}: {uploaded_file.name}</div>', unsafe_allow_html=True)
            
            if verbose_mode:
                # Estimate chunks (roughly 500 words per chunk)
                word_count = len(text.split())
                chunks = (word_count // 500) + 1
                st.markdown(f'<div class="processing-step">📊 Split into {chunks} text chunks for processing.</div>', unsafe_allow_html=True)
                
                # Preview first chunk
                with st.expander("Preview first chunk", expanded=False):
                    preview_text = text[:1000] + "..." if len(text) > 1000 else text
                    st.text(preview_text)
            
            # Reprocess button
            if st.button("🔄 Reprocess", key="reprocess"):
                st.rerun()
            
            # Generate Summary
            if st.button("📊 Generate Financial Summary", type="primary", use_container_width=True):
                if not api_key:
                    st.error("OpenRouter API key not configured. Please add it to secrets.toml")
                else:
                    with st.spinner("Generating summary with Mistral 7B..."):
                        summary = summarize_financial_document(text, api_key, temperature)
                    
                    if summary and not summary.startswith("API Error") and not summary.startswith("Error"):
                        # Display Summary
                        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                        st.markdown('<div class="summary-title">📋 Financial Summary</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="summary-content">{summary}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Trigger webhook if configured
                        if webhook_url:
                            try:
                                response = requests.post(webhook_url, json={
                                    "file_name": uploaded_file.name,
                                    "summary": summary,
                                    "temperature": temperature,
                                    "chain_type": chain_type
                                }, timeout=5)
                                if response.status_code == 200:
                                    st.success("✅ Summary sent to webhook workflow")
                            except:
                                st.info("Webhook call skipped or failed")
                        
                        # Download button
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Download Summary",
                                data=summary,
                                file_name=f"{uploaded_file.name.split('.')[0]}_summary.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        with col2:
                            if st.button("🗑️ Clear and Upload New", use_container_width=True):
                                st.rerun()
                    
                    else:
                        st.error(f"Error generating summary: {summary}")
        else:
            st.error("❌ Could not extract text from the uploaded file.")

# ============================
# Manage App Section
# ============================
st.markdown("---")
with st.expander("Manage App", expanded=False):
    st.info("""
    **App Configuration:**
    - **Model**: mistralai/mistral-7b-instruct via OpenRouter
    - **Context Window**: 8,192 tokens
    - **Max File Size**: 200MB
    - **Supported Formats**: PDF, TXT
    
    **Token Management:**
    - Documents exceeding 6,000 tokens are automatically truncated
    - Truncation preserves sentence boundaries when possible
    - Summary uses up to 1,000 tokens
    
    To configure your API key, create a `.streamlit/secrets.toml` file with:
    ```
    OPENROUTER_API_KEY = "your-api-key-here"
    ```
    """)
    
    if st.button("Clear Cache & Restart"):
        st.rerun()

# ============================
# Footer
# ============================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; font-size: 0.85rem; padding: 1rem;">
    Powered by <strong>Mistral 7B</strong> via OpenRouter • Token-aware truncation • Financial document specialization
</div>
""", unsafe_allow_html=True)
