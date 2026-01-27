import os
import tempfile
import streamlit as st
import requests
import json
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="AI Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# Modern Clean CSS
# ============================
st.markdown("""
<style>
    /* Main container */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Clean title */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        color: #2D3748;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tagline */
    .tagline {
        text-align: center;
        font-size: 1.2rem;
        color: #718096;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Upload section */
    .upload-section {
        background: white;
        border-radius: 20px;
        padding: 40px;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        border: 2px dashed #E2E8F0;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.15);
    }
    
    /* Upload button styling */
    div[data-testid="stFileUploader"] {
        width: 100%;
    }
    
    div[data-testid="stFileUploader"] > section {
        padding: 0;
        border: none;
        background: transparent;
    }
    
    div[data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px 40px !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin: 0 !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stFileUploader"] button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    div[data-testid="stFileUploader"] button:after {
        content: " 📁";
        font-size: 1.5rem;
    }
    
    /* File cards */
    .file-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
        border: 1px solid #EDF2F7;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #718096;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
    }
    
    .summary-title {
        font-size: 2rem;
        font-weight: 700;
        color: #2D3748;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .summary-content {
        line-height: 1.8;
        font-size: 1.1rem;
        color: #4A5568;
    }
    
    /* Buttons */
    .action-button {
        background: linear-gradient(135deg, #48BB78 0%, #38A169 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px 40px !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        margin: 1rem 0 !important;
    }
    
    .action-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(72, 187, 120, 0.4) !important;
    }
    
    .download-button {
        background: linear-gradient(135deg, #4299E1 0%, #3182CE 100%) !important;
    }
    
    /* Remove drag-drop area */
    div[data-testid="stFileUploader"] div[role="button"] {
        display: none !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

# Initialize API
api_key, api_message = init_openrouter()

# ============================
# Model Configuration
# ============================
MODEL_NAME = "mistralai/mistral-7b-instruct:free"
MAX_TOKENS = 32768  # Mistral 7B context
OUTPUT_TOKENS = 500

# ============================
# Main App Layout
# ============================

# Main Title
st.markdown('<h1 class="main-title">📄 AI Document Summarizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Transform lengthy documents into concise summaries instantly</p>', unsafe_allow_html=True)

# API Status Display
if not api_key:
    st.error("🔐 API Key Required")
    st.markdown("""
    <div style="background: #F7FAFC; padding: 25px; border-radius: 15px; margin: 20px 0;">
        <h4 style="color: #2D3748; margin-top: 0;">Get Your Free API Key:</h4>
        <ol style="color: #4A5568;">
            <li>Visit <a href="https://openrouter.ai/" target="_blank" style="color: #667eea; font-weight: 600;">OpenRouter.ai</a></li>
            <li>Sign up for a free account</li>
            <li>Get your API key from the dashboard</li>
            <li>Add to Streamlit secrets as <code>OPENROUTER_API_KEY</code></li>
        </ol>
        <p style="color: #718096; font-size: 0.9rem; margin-top: 15px;">
            💡 <strong>Free Tier Includes:</strong> 500,000 tokens per month • Mistral 7B • No credit card required
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
else:
    # Model Info Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%); 
                border-radius: 15px; 
                padding: 25px; 
                margin: 20px 0;
                border-left: 5px solid #764ba2;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h4 style="color: #2D3748; margin: 0 0 5px 0;">🤖 Using: Mistral 7B</h4>
                <p style="color: #718096; margin: 0; font-size: 0.95rem;">Free Tier • Max 32,768 tokens</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.9rem; color: #48BB78; font-weight: 600;">✅ API Connected</div>
                <div style="font-size: 0.85rem; color: #718096;">via OpenRouter</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================
# File Upload Section
# ============================
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; margin-bottom: 30px;">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #2D3748; margin-bottom: 10px;">📁 Upload Documents</h3>', unsafe_allow_html=True)
st.markdown('<p style="color: #718096;">Upload PDF or text files for summarization</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload multiple PDF or text files"
)

st.markdown('</div>', unsafe_allow_html=True)

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def process_files(uploaded_files):
    """Process uploaded files"""
    all_text = ""
    file_details = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(temp_path)
                file_type = "📄 PDF"
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                file_type = "📝 TXT"
            else:
                continue
            
            if text and not text.startswith("Error"):
                all_text += f"\n\n{'='*60}\n📄 File: {uploaded_file.name}\n{'='*60}\n\n{text}"
                file_details.append({
                    "name": uploaded_file.name,
                    "type": file_type,
                    "size": len(uploaded_file.getvalue()),
                    "text_length": len(text)
                })
                
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip(), file_details

# ============================
# OpenRouter API Function
# ============================
def summarize_with_mistral(text, api_key):
    """Summarize text using Mistral 7B via OpenRouter"""
    
    # Truncate text if too long (leave room for prompt and response)
    max_chars = 25000  # Leave room for prompt
    if len(text) > max_chars:
        text = text[:max_chars]
    
    # Prepare the prompt
    prompt = f"""Please provide a comprehensive summary of the following document(s). 

Focus on:
1. Key points and main ideas
2. Important facts and figures
3. Conclusions and recommendations
4. Critical insights

Document Content:
{text}

Please provide a well-structured, concise summary:"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://docsum.streamlit.app",  # Optional: your site URL
        "X-Title": "DocSum AI Summarizer"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": OUTPUT_TOKENS,
        "temperature": 0.3,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        
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
# Main App Logic
# ============================
if uploaded_files:
    # Show uploaded files
    with st.expander(f"📋 View Uploaded Files ({len(uploaded_files)} files)", expanded=True):
        for i, file in enumerate(uploaded_files, 1):
            file_size_kb = len(file.getvalue()) / 1024
            file_type = file.type.split('/')[-1].upper()
            
            st.markdown(f"""
            <div class="file-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <strong style="color: #2D3748;">{i}. {file.name}</strong><br>
                        <span style="color: #718096; font-size: 0.9rem;">{file_type} • {file_size_kb:.1f} KB</span>
                    </div>
                    <div style="color: #48BB78; font-weight: 600;">✓</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Process files
    with st.spinner("🔄 Processing documents..."):
        text, file_details = process_files(uploaded_files)
    
    if text and len(text) > 100:
        # Show statistics
        st.markdown("### 📊 Document Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_chars = len(text)
        total_words = len(text.split())
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(file_details)}</div>
                <div class="stat-label">Files</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_chars:,}</div>
                <div class="stat-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{total_words:,}</div>
                <div class="stat-label">Words</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            available_tokens = MAX_TOKENS - OUTPUT_TOKENS
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{available_tokens:,}</div>
                <div class="stat-label">Tokens Available</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Preview
        with st.expander("👁️ Preview Document Text", expanded=False):
            preview_text = text[:3000]
            if len(text) > 3000:
                preview_text += "\n\n[... document continues ...]"
            st.text(preview_text)
        
        # Generate Summary Button
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #2D3748; margin-bottom: 1rem;">Ready to Generate Summary</h3>
            <p style="color: #718096;">Click the button below to process with Mistral 7B AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Generate AI Summary", key="generate", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating summary with Mistral 7B..."):
                summary = summarize_with_mistral(text, api_key)
            
            if summary and not summary.startswith("API Error") and not summary.startswith("Error"):
                # Display Summary
                st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                st.markdown('<div class="summary-title">📋 AI-Generated Summary</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-content">{summary}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Summary Statistics
                st.markdown("---")
                st.markdown("### 📈 Summary Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    compression = 100 - (len(summary) / total_chars * 100) if total_chars > 0 else 0
                    st.metric("Compression", f"{compression:.1f}%")
                with col2:
                    st.metric("Summary Length", f"{len(summary):,} chars")
                with col3:
                    st.metric("Word Count", f"{len(summary.split()):,}")
                
                # Download Button
                st.download_button(
                    label="💾 Download Summary",
                    data=summary,
                    file_name="ai_summary.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download"
                )
                
            else:
                st.error(f"❌ {summary}")
                st.info("""
                **Troubleshooting Tips:**
                1. Check your OpenRouter API key is valid
                2. Ensure you have sufficient free credits
                3. Try reducing the document size
                4. Wait a moment and try again
                """)
    else:
        st.error("❌ Could not extract sufficient text from uploaded files")
else:
    # Empty State
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: #F7FAFC; border-radius: 20px; margin: 2rem 0;">
            <div style="font-size: 5rem; margin-bottom: 1.5rem;">📁</div>
            <h3 style="color: #2D3748; margin-bottom: 1rem;">No Documents Uploaded</h3>
            <p style="color: #718096; line-height: 1.6; margin-bottom: 2rem;">
                Upload PDF or text files to generate AI-powered summaries<br>
                using Mistral 7B via OpenRouter
            </p>
            <div style="color: #A0AEC0; font-size: 0.9rem;">
                📄 PDF • 📝 TXT • 🆓 Free Tier
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================
# Footer
# ============================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem 0;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 10px;">
        <div>🤖 <strong>Mistral 7B</strong></div>
        <div style="width: 4px; height: 4px; background: #CBD5E0; border-radius: 50%;"></div>
        <div>🌐 <strong>OpenRouter</strong></div>
        <div style="width: 4px; height: 4px; background: #CBD5E0; border-radius: 50%;"></div>
        <div>🆓 <strong>Free Tier</strong></div>
    </div>
    <div style="font-size: 0.9rem;">
        Built with Streamlit • 500,000 free tokens per month
    </div>
</div>
""", unsafe_allow_html=True)
