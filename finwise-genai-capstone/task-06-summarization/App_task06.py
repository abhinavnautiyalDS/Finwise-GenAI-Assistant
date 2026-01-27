import os
import tempfile
import streamlit as st
import requests
import json

# ============================
# Basic Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide"
)

# Add debug information in sidebar
st.sidebar.title("Debug Info")
st.sidebar.write("App starting...")

# ============================
# API Key Setup
# ============================
try:
    # Check for DeepSeek API key
    if 'DEEPSEEK_API_KEY' in st.secrets:
        DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
        st.sidebar.success("✓ API key found in secrets")
    else:
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        if DEEPSEEK_API_KEY:
            st.sidebar.success("✓ API key found in env")
        else:
            st.sidebar.warning("⚠ No API key found")
except Exception as e:
    st.sidebar.error(f"Error checking API key: {e}")
    DEEPSEEK_API_KEY = None

# ============================
# Simple Text Extraction
# ============================
def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file"""
    try:
        if uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            # Try to extract text from PDF
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except ImportError:
                return "PDF processing requires PyPDF2. Please install it."
        else:
            return None
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# ============================
# DeepSeek Client
# ============================
class SimpleDeepSeekClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def summarize(self, text):
        """Summarize text using DeepSeek API"""
        if not self.api_key:
            return "Error: No API key provided. Please set DEEPSEEK_API_KEY in secrets."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Please summarize the following financial document in 3-5 paragraphs.
Focus on key financial figures, strategic developments, and future outlook:

{text[:15000]}  # Limit text to avoid token limits

Summary:"""
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a financial analyst summarizing documents."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Response parsing error: {str(e)}"

# ============================
# Main App
# ============================
st.title("💼 Financial Document Summarizer")
st.write("Upload financial documents (PDF or TXT) for summarization")

# Initialize client
client = SimpleDeepSeekClient(DEEPSEEK_API_KEY)

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "txt"],
    accept_multiple_files=False
)

if uploaded_file:
    st.sidebar.info(f"File uploaded: {uploaded_file.name}")
    
    # Extract text
    with st.spinner("Extracting text..."):
        text = extract_text_from_file(uploaded_file)
    
    if text and not text.startswith("Error"):
        st.success(f"✓ Extracted {len(text)} characters")
        
        # Show preview
        with st.expander("📄 View extracted text"):
            st.text(text[:1000] + "..." if len(text) > 1000 else text)
        
        # Summarize button
        if st.button("Generate Summary", type="primary"):
            if not DEEPSEEK_API_KEY:
                st.error("Please set DEEPSEEK_API_KEY in Streamlit secrets")
            else:
                with st.spinner("Summarizing with DeepSeek..."):
                    summary = client.summarize(text)
                
                st.subheader("📊 Summary")
                st.write(summary)
                
                # Download button
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
    else:
        st.error(f"Could not extract text: {text}")

# ============================
# Debug Information
# ============================
with st.sidebar.expander("Debug Info"):
    st.write("Python version:", os.sys.version)
    st.write("Working directory:", os.getcwd())
    st.write("Files in directory:", os.listdir("."))
    
    # Check for requirements.txt
    if os.path.exists("requirements.txt"):
        st.success("requirements.txt found")
        with open("requirements.txt", "r") as f:
            st.code(f.read())
    else:
        st.error("requirements.txt not found")

# ============================
# Setup Instructions
# ============================
with st.sidebar.expander("Setup Instructions"):
    st.markdown("""
    1. **Get DeepSeek API key** from https://platform.deepseek.com/
    
    2. **Add to Streamlit secrets** (.streamlit/secrets.toml):
    ```
    DEEPSEEK_API_KEY = "your-key-here"
    ```
    
    3. **requirements.txt** should contain:
    ```
    streamlit>=1.28.0
    requests>=2.28.0
    PyPDF2>=3.0.0
    ```
    
    4. **File structure**:
    ```
    your-app/
    ├── App_task06.py
    ├── requirements.txt
    └── .streamlit/
        └── secrets.toml
    ```
    """)
