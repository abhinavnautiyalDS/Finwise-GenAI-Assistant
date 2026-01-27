    import os
import tempfile
import streamlit as st
import requests
import json

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide"
)

# ============================
# Custom CSS
# ============================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .summary-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Model Selection
# ============================
st.sidebar.title("Model Configuration")

model_option = st.sidebar.selectbox(
    "Choose Model Provider",
    ["Local Ollama", "Groq (Free Tier)", "Together AI (Free Credits)"],
    help="Select where to run the model"
)

# ============================
# Option 1: Local Ollama with Qwen
# ============================
if model_option == "Local Ollama":
    st.sidebar.info("Run Ollama locally: `ollama run qwen2.5:3b`")
    
    OLLAMA_URL = st.sidebar.text_input(
        "Ollama Server URL",
        value="http://localhost:11434",
        help="URL where Ollama is running"
    )
    
    def summarize_with_ollama(text):
        """Summarize using local Ollama with Qwen"""
        try:
            prompt = f"""Please summarize the following financial document concisely:
            
{text[:10000]}

Focus on:
1. Key financial figures
2. Strategic developments
3. Future outlook

Summary:"""
            
            payload = {
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response")
            else:
                return f"Ollama Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

# ============================
# Option 2: Groq API (Free Tier Available)
# ============================
elif model_option == "Groq (Free Tier)":
    st.sidebar.info("Get free API key from groq.com")
    
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except:
        GROQ_API_KEY = st.sidebar.text_input(
            "Groq API Key",
            type="password",
            help="Get from groq.com (free tier available)"
        )
    
    def summarize_with_groq(text):
        """Summarize using Groq API (has free tier)"""
        if not GROQ_API_KEY:
            return "Please provide Groq API key"
        
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Summarize this financial document:

{text[:8000]}

Provide a concise summary focusing on financial metrics, strategy, and outlook."""

            payload = {
                "model": "llama-3.3-70b-versatile",  # Groq has fast free models
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Groq API Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

# ============================
# Option 3: Use OpenRouter (Aggregator with free models)
# ============================
else:  # Together AI or alternatives
    st.sidebar.info("Using OpenRouter with free options")
    
    try:
        OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    except:
        OPENROUTER_API_KEY = st.sidebar.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get from openrouter.ai (has free credits)"
        )
    
    def summarize_with_openrouter(text):
        """Summarize using OpenRouter (has free models)"""
        if not OPENROUTER_API_KEY:
            return "Please provide OpenRouter API key"
        
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Summarize this financial document concisely:

{text[:8000]}"""
            
            payload = {
                "model": "google/gemma-2-2b-it",  # Free model on OpenRouter
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"OpenRouter Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

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
    except ImportError:
        return "Please install pypdf"

def process_uploaded_files(uploaded_files):
    """Process uploaded files"""
    all_text = ""
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
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
            
            if text:
                all_text += f"\n\n--- From: {uploaded_file.name} ---\n{text}"
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text

# ============================
# Main App
# ============================
st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)
st.write(f"Using: **{model_option}**")

# File upload
uploaded_files = st.file_uploader(
    "Upload PDF or TXT files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing files..."):
        text = process_uploaded_files(uploaded_files)
    
    if text and len(text) > 100:
        st.info(f"📊 Extracted {len(text)} characters")
        
        with st.expander("Preview text"):
            st.text(text[:2000] + "..." if len(text) > 2000 else text)
        
        if st.button("Generate Summary", type="primary"):
            with st.spinner("Generating summary..."):
                if model_option == "Local Ollama":
                    summary = summarize_with_ollama(text)
                elif model_option == "Groq (Free Tier)":
                    summary = summarize_with_groq(text)
                else:
                    summary = summarize_with_openrouter(text)
            
            st.subheader("Summary")
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
            
            st.download_button(
                "Download Summary",
                summary,
                file_name="summary.txt"
            )
    else:
        st.error("Could not extract sufficient text")

# ============================
# Setup Instructions
# ============================
with st.expander("🛠️ Setup Instructions"):
    st.markdown("""
    ## **Option 1: Local Ollama (Recommended for Qwen)**
    
    1. **Install Ollama**: https://ollama.com/
    2. **Pull Qwen model**: 
    ```bash
    ollama pull qwen2.5:3b
    ```
    3. **Run the model**:
    ```bash
    ollama run qwen2.5:3b
    ```
    4. **Keep Ollama running** in background
    5. **Update Ollama URL** in sidebar if needed
    
    ## **Option 2: Groq Cloud (Free Tier)**
    
    1. **Sign up at**: https://console.groq.com/
    2. **Get free API key**
    3. **Add to Streamlit secrets**:
    ```toml
    GROQ_API_KEY = "your-key-here"
    ```
    
    ## **Option 3: OpenRouter (Free Credits)**
    
    1. **Sign up at**: https://openrouter.ai/
    2. **Get free credits** (0.5M tokens free)
    3. **Add to Streamlit secrets**:
    ```toml
    OPENROUTER_API_KEY = "your-key-here"
    ```
    
    ## **requirements.txt**
    ```txt
    streamlit>=1.28.0
    requests>=2.28.0
    pypdf>=3.0.0
    ```
    """)
