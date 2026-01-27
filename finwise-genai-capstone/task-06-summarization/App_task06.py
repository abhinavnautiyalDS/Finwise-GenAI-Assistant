import os
import tempfile
import streamlit as st
import google.generativeai as genai
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="DocSum | AI Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"  # Cleaner without sidebar
)

# ============================
# Modern, Clean CSS
# ============================
st.markdown("""
<style>
    /* Remove Streamlit default styling */
    .stApp {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Clean title styling */
    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Enhanced file uploader styling */
    .upload-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        margin: 2rem auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .upload-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .upload-label {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .upload-instructions {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Custom file upload button */
    div[data-testid="stFileUploader"] {
        width: 100%;
    }
    
    div[data-testid="stFileUploader"] > section {
        padding: 0;
        border: none;
        background: white;
        border-radius: 10px;
    }
    
    div[data-testid="stFileUploader"] button {
        background: white !important;
        color: #764ba2 !important;
        border: 2px dashed #764ba2 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin: 0 !important;
    }
    
    div[data-testid="stFileUploader"] button:hover {
        background: #f8f9fa !important;
        border: 2px solid #764ba2 !important;
    }
    
    /* Summary box styling */
    .summary-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 30px;
        margin: 2rem 0;
        border-left: 5px solid #1f77b4;
    }
    
    .summary-title {
        color: #1f77b4;
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1f77b4 0%, #2c8ed6 100%);
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
        padding: 15px 40px;
        border: none;
        border-radius: 50px;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 2rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(31, 119, 180, 0.3);
    }
    
    .download-btn {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* File cards */
    .file-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    /* Remove the drag-and-drop box */
    div[data-testid="stFileUploader"] div[role="button"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Initialize Gemini API
# ============================
def init_gemini():
    """Initialize Gemini API"""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True, "Connected to Gemini API"
    except KeyError:
        return False, "API key not found in secrets"
    except Exception as e:
        return False, f"API error: {str(e)}"

# ============================
# Main App - Clean Layout
# ============================

# Header Section
st.markdown('<h1 class="main-title">📄 DocSum</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Document Summarization</p>', unsafe_allow_html=True)

# Initialize API
api_status, api_message = init_gemini()
if not api_status:
    st.error(f"🔒 {api_message}")
    st.info("""
    **To get a free Gemini API key:**
    1. Visit https://makersuite.google.com/app/apikey
    2. Sign in with Google account
    3. Create API key
    4. Add to Streamlit secrets as `GOOGLE_API_KEY`
    """)
    st.stop()

# File Upload Section - Clean and Prominent
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
st.markdown('<span class="upload-label">📁 Upload Your Documents</span>', unsafe_allow_html=True)
st.markdown('<span class="upload-instructions">Upload PDF or text files for summarization</span>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload multiple files"
)

st.markdown('</div>', unsafe_allow_html=True)

# File Processing Functions
def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
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
            st.error(f"Error: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip(), file_details

# Process uploaded files
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
    
    # Show file details
    with st.expander("📋 View Uploaded Files", expanded=False):
        for i, file in enumerate(uploaded_files, 1):
            file_size = len(file.getvalue()) / 1024  # Convert to KB
            st.markdown(f"""
            <div class="file-card">
                <strong>{i}. {file.name}</strong><br>
                <small>{file.type.split('/')[-1].upper()} • {file_size:.1f} KB</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Process files
    with st.spinner("🔄 Processing documents..."):
        text, file_details = process_files(uploaded_files)
    
    if text and len(text) > 100:
        # Show statistics
        st.subheader("📊 Document Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_chars = len(text)
        total_words = len(text.split())
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(uploaded_files)}</div>
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
            avg_words = total_words // len(uploaded_files) if uploaded_files else 0
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{avg_words:,}</div>
                <div class="stat-label">Avg per file</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Preview text
        with st.expander("👁️ Preview Document Text", expanded=False):
            preview = text[:2000] + "..." if len(text) > 2000 else text
            st.text(preview)
        
        # Generate summary button
        st.markdown("---")
        
        if st.button("✨ Generate Summary", type="primary"):
            with st.spinner("🤖 Generating summary with AI..."):
                try:
                    # Initialize Gemini model
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    
                    # Create prompt
                    prompt = f"""Please summarize the following document(s) concisely and accurately:

{text[:30000]}

Focus on key points, main ideas, and important conclusions. Provide a clear, well-structured summary."""

                    # Generate summary
                    response = model.generate_content(prompt)
                    summary = response.text
                    
                    # Display summary
                    st.markdown('<div class="summary-container">', unsafe_allow_html=True)
                    st.markdown('<div class="summary-title">📋 AI-Generated Summary</div>', unsafe_allow_html=True)
                    st.write(summary)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Summary statistics
                    st.markdown("---")
                    st.subheader("📈 Summary Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        compression = 100 - (len(summary) / total_chars * 100) if total_chars > 0 else 0
                        st.metric("Compression", f"{compression:.1f}%")
                    with col2:
                        st.metric("Summary Length", f"{len(summary):,} chars")
                    with col3:
                        st.metric("Word Count", f"{len(summary.split()):,}")
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary,
                        file_name="document_summary.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error generating summary: {str(e)}")
    else:
        st.error("Could not extract sufficient text from the uploaded files")
else:
    # Empty state with clear instructions
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px; margin-top: 2rem;">
            <div style="font-size: 4rem;">📁</div>
            <h3 style="color: #495057;">No Documents Uploaded</h3>
            <p style="color: #6c757d;">Upload PDF or text files to generate AI-powered summaries</p>
            <p style="color: #adb5bd; font-size: 0.9rem;">Supported formats: PDF, TXT</p>
        </div>
        """, unsafe_allow_html=True)

# ============================
# Simple Footer
# ============================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    <small>Powered by Google Gemini AI • Free Tier • Made with Streamlit</small>
</div>
""", unsafe_allow_html=True)
