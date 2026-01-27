import os
import tempfile
import streamlit as st
import google.generativeai as genai
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide"
)

# ============================
# Simple CSS
# ============================
st.markdown("""
<style>
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .summary-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Title
# ============================
st.title("📄 Document Summarizer")
st.markdown("Upload PDF or TXT files for AI-powered summarization")

# ============================
# API Configuration
# ============================
st.sidebar.header("🔑 API Configuration")

# Get API key
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("API key loaded")
except KeyError:
    api_key = st.sidebar.text_input(
        "Enter Gemini API Key:",
        type="password",
        help="Get free key from https://makersuite.google.com/app/apikey"
    )
    if not api_key:
        st.warning("Please enter your Gemini API key")
        st.info("Get a FREE API key from: https://makersuite.google.com/app/apikey")
        st.stop()

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    st.sidebar.success("Gemini API configured")
except Exception as e:
    st.error(f"API configuration failed: {e}")
    st.stop()

# ============================
# Model Selection
# ============================
model_name = st.sidebar.selectbox(
    "Select Model",
    ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
    index=0
)

# ============================
# Simple Model Initialization (No Caching)
# ============================
def init_model():
    """Initialize Gemini model without caching"""
    try:
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None

# Initialize model
model = init_model()
if not model:
    st.error("Could not initialize Gemini model. Please try a different model.")
    st.stop()

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Simple PDF text extraction"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def process_files(uploaded_files):
    """Process uploaded files"""
    all_text = ""
    
    for uploaded_file in uploaded_files:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if uploaded_file.type == "application/pdf" else ".txt") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(temp_path)
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = ""
            
            if text and not text.startswith("Error"):
                all_text += f"\n\n--- Document: {uploaded_file.name} ---\n{text}"
                st.success(f"Processed: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text

# ============================
# Summarization Function
# ============================
def generate_summary(text):
    """Generate summary using Gemini"""
    try:
        prompt = f"""Please summarize the following document concisely:
        
{text[:10000]}

Summary:"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ============================
# Main App
# ============================

# File upload
uploaded_files = st.file_uploader(
    "Choose files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    # Process files
    text = process_files(uploaded_files)
    
    if text:
        st.info(f"Extracted {len(text)} characters")
        
        # Show preview
        with st.expander("Preview text"):
            st.text(text[:1000] + "..." if len(text) > 1000 else text)
        
        # Generate summary
        if st.button("Generate Summary", type="primary"):
            with st.spinner("Generating summary..."):
                summary = generate_summary(text)
            
            if summary and not summary.startswith("Error"):
                st.subheader("Summary")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    "Download Summary",
                    summary,
                    file_name="summary.txt"
                )
            else:
                st.error(summary)
else:
    st.info("Please upload files to begin")

# ============================
# Simple Instructions
# ============================
with st.expander("Setup Instructions"):
    st.markdown("""
    **Requirements.txt:**
    ```txt
    streamlit>=1.28.0
    google-generativeai>=0.3.0
    pypdf>=3.0.0
    ```
    
    **Get FREE API Key:**
    1. Go to https://makersuite.google.com/app/apikey
    2. Sign in with Google account
    3. Create API key
    4. Add to Streamlit secrets:
    
    ```toml
    GOOGLE_API_KEY = "your-key-here"
    ```
    """)
