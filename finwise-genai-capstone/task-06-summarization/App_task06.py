import os
import tempfile
import streamlit as st
import requests
import json
import time

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
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        line-height: 1.6;
    }
    .model-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Available FREE Hugging Face Models with Inference
# ============================
FREE_MODELS = {
    "meta-llama/Llama-3.1-8B-Instruct": {
        "name": "BART Large CNN",
        "description": "Specialized for summarization, very fast",
        "max_length": 1024,
        "type": "summarization"
    },
    "google/pegasus-xsum": {
        "name": "Pegasus XSum",
        "description": "Excellent for abstractive summarization",
        "max_length": 512,
        "type": "summarization"
    },
    "Falconsai/text_summarization": {
        "name": "Falcon Text Summarization",
        "description": "General purpose summarization model",
        "max_length": 1000,
        "type": "summarization"
    },
    "sshleifer/distilbart-cnn-12-6": {
        "name": "DistilBART CNN",
        "description": "Lightweight but effective summarization",
        "max_length": 1024,
        "type": "summarization"
    },
    "mrm8488/bert2bert_shared-german-finetuned-summarization": {
        "name": "BERT2BERT Summarization",
        "description": "Good for financial/technical documents",
        "max_length": 512,
        "type": "summarization"
    }
}

# ============================
# Model Selection
# ============================
st.sidebar.title("🤖 Model Selection")

selected_model_id = st.sidebar.selectbox(
    "Choose Model",
    list(FREE_MODELS.keys()),
    format_func=lambda x: FREE_MODELS[x]["name"]
)

model_info = FREE_MODELS[selected_model_id]

st.sidebar.markdown(f'<div class="model-card"><b>{model_info["name"]}</b><br>{model_info["description"]}</div>', unsafe_allow_html=True)

# Optional Hugging Face token for better rate limits
use_token = st.sidebar.checkbox("Use HF Token (optional, improves rate limits)")
if use_token:
    try:
        HF_TOKEN = st.secrets["HF_TOKEN"]
        HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
    except:
        HF_TOKEN = st.sidebar.text_input("HF Token", type="password")
        HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
else:
    HEADERS = {}

# ============================
# API Function
# ============================
def summarize_with_hf(text, model_id, model_type="summarization"):
    """Summarize text using Hugging Face Inference API"""
    
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    
    # Truncate text based on model limits
    max_input_len = model_info["max_length"] * 8  # Approximate character limit
    if len(text) > max_input_len:
        text = text[:max_input_len]
        st.info(f"⚠️ Text truncated to {max_input_len} characters for model limits")
    
    try:
        if model_type == "summarization":
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": model_info["max_length"],
                    "min_length": max(50, model_info["max_length"] // 4),
                    "do_sample": False
                },
                "options": {
                    "use_cache": True,
                    "wait_for_model": True
                }
            }
        else:
            # For text generation models
            prompt = f"Summarize the following financial document concisely:\n\n{text}\n\nSummary:"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.3
                }
            }
        
        # Make request
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=120  # Long timeout for model loading
        )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            
            if model_type == "summarization":
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('summary_text', str(result))
                else:
                    return str(result)
            else:
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', str(result))
                return str(result)
                
        elif response.status_code == 503:
            # Model is loading
            try:
                error_data = response.json()
                estimate = error_data.get('estimated_time', 30)
                return f"⏳ Model is loading. Please wait {int(estimate)} seconds and try again."
            except:
                return "⏳ Model is loading. Please try again in 30 seconds."
                
        else:
            return f"❌ API Error {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================
# File Processing
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except ImportError:
        return "Please install pypdf: pip install pypdf"

def process_files(uploaded_files):
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
            
            if text and not text.startswith("Please install"):
                all_text += f"\n\n--- Document: {uploaded_file.name} ---\n{text}"
                
        except Exception as e:
            st.error(f"Error with {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip()

# ============================
# Main App
# ============================
st.markdown('<h1 class="main-header">📄 Free Document Summarizer</h1>', unsafe_allow_html=True)
st.write(f"Using: **{model_info['name']}**")

# File upload
uploaded_files = st.file_uploader(
    "Upload PDF or TXT files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Multiple files will be combined"
)

if uploaded_files:
    with st.spinner("Processing files..."):
        text = process_files(uploaded_files)
    
    if text and len(text) > 50:
        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files", len(uploaded_files))
        with col2:
            st.metric("Characters", f"{len(text):,}")
        with col3:
            words = len(text.split())
            st.metric("Words", f"{words:,}")
        
        # Preview
        with st.expander("📋 Preview Text"):
            st.text(text[:1500] + "..." if len(text) > 1500 else text)
        
        # Summarize button
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            with st.spinner(f"Summarizing with {model_info['name']}..."):
                summary = summarize_with_hf(text, selected_model_id, model_info["type"])
            
            # Display results
            st.subheader("📋 Summary")
            
            if summary and not summary.startswith("❌") and not summary.startswith("⏳"):
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Stats
                st.caption(f"Summary length: {len(summary):,} characters")
                
                # Download
                st.download_button(
                    "💾 Download Summary",
                    summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.error(summary)
                if "loading" in summary.lower():
                    st.info("""
                    **Model Loading Tips:**
                    1. First request loads the model (takes 30-60 seconds)
                    2. Wait and try again
                    3. Subsequent requests are faster
                    """)
    else:
        st.error("Could not extract text from files")

# ============================
# Model Information
# ============================
with st.expander("ℹ️ About Available Models"):
    st.markdown("""
    ### **Free Hugging Face Models with Inference Support**
    
    These models are **guaranteed to work** with Hugging Face's free Inference API:
    
    1. **facebook/bart-large-cnn**
       - Purpose-built for summarization
       - Very fast and reliable
       - Max length: 1024 tokens
       
    2. **google/pegasus-xsum**
       - Excellent abstractive summarization
       - Trained on news articles
       - Max length: 512 tokens
       
    3. **Falconsai/text_summarization**
       - General purpose summarization
       - Good for various document types
       - Max length: 1000 tokens
       
    4. **sshleifer/distilbart-cnn-12-6**
       - Distilled version of BART
       - Lightweight but effective
       - Max length: 1024 tokens
       
    5. **mrm8488/bert2bert_shared-german-finetuned-summarization**
       - Good for technical/financial documents
       - Multilingual support
       - Max length: 512 tokens
    
    ### **Rate Limits**
    - Without token: ~30 requests/hour
    - With HF_TOKEN: ~500 requests/hour
    - First request loads model (30-60 seconds)
    """)

with st.expander("🛠️ Setup Instructions"):
    st.markdown("""
    ### **1. requirements.txt**
    ```txt
    streamlit>=1.28.0
    requests>=2.28.0
    pypdf>=3.0.0
    ```
    
    ### **2. Optional: Get HF Token (recommended)**
    1. Go to https://huggingface.co/settings/tokens
    2. Create new token with "read" access
    3. Add to Streamlit secrets:
    ```toml
    # .streamlit/secrets.toml
    HF_TOKEN = "your-token-here"
    ```
    
    ### **3. File Structure**
    ```
    your-app/
    ├── App_task06.py
    ├── requirements.txt
    └── .streamlit/
        └── secrets.toml  # optional
    ```
    
    ### **4. Tips for Best Results**
    - Start with **facebook/bart-large-cnn** (most reliable)
    - Use **HF Token** for better rate limits
    - For long documents, the app auto-truncates
    - First request loads model - be patient
    """)

st.caption("Built with Streamlit • Powered by Hugging Face Free Inference API")
