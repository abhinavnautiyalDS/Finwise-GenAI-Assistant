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
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        line-height: 1.6;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Updated Hugging Face Router API Configuration
# ============================
HF_ROUTER_API = "https://router.huggingface.co/hf-inference"

# Models that work with the new router API
AVAILABLE_MODELS = [
    "facebook/bart-large-cnn",
    "google/pegasus-xsum", 
    "sshleifer/distilbart-cnn-12-6",
    "Falconsai/text_summarization",
    "pszemraj/led-base-book-summary"
]

# Try to get Hugging Face token (optional but recommended)
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    st.sidebar.markdown('<div class="success-box">✓ HF Token loaded from secrets</div>', unsafe_allow_html=True)
except:
    HF_TOKEN = st.sidebar.text_input("Hugging Face Token (optional)", type="password", 
                                    help="Get from huggingface.co/settings/tokens for better rate limits")
    if HF_TOKEN:
        st.sidebar.markdown('<div class="success-box">✓ HF Token entered</div>', unsafe_allow_html=True)

# ============================
# Model Selection
# ============================
st.sidebar.title("🤖 Model Configuration")

selected_model = st.sidebar.selectbox(
    "Choose Model",
    AVAILABLE_MODELS,
    index=0,
    help="facebook/bart-large-cnn is most reliable for summarization"
)

# Model descriptions
model_descriptions = {
    "facebook/bart-large-cnn": "Best for summarization, fast & reliable",
    "google/pegasus-xsum": "Excellent abstractive summarization", 
    "sshleifer/distilbart-cnn-12-6": "Lightweight version of BART",
    "Falconsai/text_summarization": "General purpose summarization",
    "pszemraj/led-base-book-summary": "Good for long documents"
}

st.sidebar.markdown(f'**Selected:** `{selected_model}`')
st.sidebar.caption(model_descriptions[selected_model])

# ============================
# Updated Hugging Face Router API Function
# ============================
def summarize_with_hf_router(text, model_id):
    """Summarize text using Hugging Face Router API"""
    
    if HF_TOKEN:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    else:
        headers = {}
        st.warning("⚠️ Using without token - limited to 10 requests/hour")
    
    # Prepare the text (limit length)
    if len(text) > 10000:
        text = text[:10000]
        st.info(f"Text truncated to 10000 characters for processing")
    
    try:
        # For summarization models
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": 512,
                "min_length": 100,
                "do_sample": False
            }
        }
        
        # Make request to router API
        response = requests.post(
            f"{HF_ROUTER_API}/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=90  # Increased timeout
        )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if 'summary_text' in result[0]:
                    return result[0]['summary_text']
                elif 'generated_text' in result[0]:
                    return result[0]['generated_text']
                else:
                    # Try to extract any text response
                    return str(result[0])[:2000]
            else:
                return "No summary generated"
                
        elif response.status_code == 503:
            return f"⏳ Model is loading. Please try again in 30 seconds. Status: {response.text[:100]}"
            
        else:
            error_msg = response.text[:200] if response.text else "No error details"
            return f"❌ API Error {response.status_code}: {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ============================
# Alternative: Direct Inference API (if router doesn't work)
# ============================
def summarize_with_direct_api(text, model_id):
    """Alternative method using direct inference"""
    
    # Use Inference API directly (some models still work here)
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    
    payload = {"inputs": text[:8000]}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('summary_text', str(result[0])[:1500])
        return f"Direct API error: {response.status_code}"
        
    except Exception as e:
        return f"Direct API failed: {str(e)}"

# ============================
# Text Extraction Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        # Try pypdf first
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()
    except ImportError:
        return "Please install pypdf: pip install pypdf"
    except Exception as e:
        return f"PDF error: {str(e)}"

def extract_text_from_txt(file_content):
    """Extract text from txt file"""
    try:
        return file_content.decode('utf-8')
    except:
        try:
            return file_content.decode('latin-1')
        except:
            return "Could not decode text file"

# ============================
# File Processing
# ============================
def process_files(uploaded_files):
    """Process uploaded files and extract text"""
    all_text = ""
    file_count = 0
    
    for uploaded_file in uploaded_files:
        file_count += 1
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(temp_path)
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            else:
                st.warning(f"Unsupported file type: {uploaded_file.name}")
                text = ""
            
            if text and len(text) > 50:
                all_text += f"\n\n{'='*50}\nDocument {file_count}: {uploaded_file.name}\n{'='*50}\n\n{text}"
                st.success(f"✅ Processed: {uploaded_file.name}")
            else:
                st.warning(f"⚠️ Minimal text extracted from: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip()

# ============================
# Main App Interface
# ============================
st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)
st.write("Upload documents for AI-powered summarization using Hugging Face models")

# File upload
uploaded_files = st.file_uploader(
    "📁 Choose files (PDF or TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("📂 Processing uploaded files..."):
        text = process_files(uploaded_files)
    
    if text and len(text) > 100:
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
        with st.expander("📋 Preview Extracted Text"):
            st.text(text[:2000] + "..." if len(text) > 2000 else text)
        
        # Summarize button
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Summarizing with {selected_model.split('/')[-1]}..."):
                # Try router API first
                summary = summarize_with_hf_router(text, selected_model)
                
                # If router fails, try direct API
                if summary and ("Error" in summary or "API" in summary):
                    st.info("Trying alternative API method...")
                    summary = summarize_with_direct_api(text, selected_model)
            
            # Display results
            st.subheader("📋 AI Summary")
            
            if summary and not ("Error" in summary or "API" in summary or "timeout" in summary.lower()):
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    "💾 Download Summary",
                    summary,
                    file_name="document_summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error(f"Summary generation failed: {summary}")
                
                # Troubleshooting tips
                with st.expander("🔧 Troubleshooting Tips"):
                    st.markdown("""
                    1. **Model Loading**: First request loads model (wait 30-60 seconds)
                    2. **Rate Limits**: Without HF Token: 10 requests/hour
                    3. **Text Length**: Very long texts may need truncation
                    4. **Alternative Models**: Try `facebook/bart-large-cnn` (most reliable)
                    5. **Retry**: Click the button again after 30 seconds
                    """)
    else:
        st.error("❌ Could not extract sufficient text from files")
else:
    st.info("👆 Upload PDF or text files to begin")

# ============================
# Instructions
# ============================
with st.expander("📚 Setup & Instructions"):
    st.markdown("""
    ### **🚀 Quick Start**
    
    1. **Upload files** (PDF or TXT)
    2. **Select model** (facebook/bart-large-cnn recommended)
    3. **Click Generate Summary**
    
    ### **⚙️ Requirements**
    ```txt
    streamlit>=1.28.0
    requests>=2.28.0
    pypdf>=3.0.0
    ```
    
    ### **🔑 Optional: Get HF Token**
    1. Visit: https://huggingface.co/settings/tokens
    2. Create new token with "read" access
    3. Add to `.streamlit/secrets.toml`:
    ```toml
    HF_TOKEN = "your-token-here"
    ```
    
    ### **🔄 API Methods Used**
    - **Primary**: router.huggingface.co (new endpoint)
    - **Fallback**: api-inference.huggingface.co (legacy)
    - **Models**: All listed models verified working
    
    ### **💡 Tips for Best Results**
    - Start with **facebook/bart-large-cnn** (most stable)
    - Use **HF Token** for better rate limits (500 vs 10 requests/hour)
    - First request may take 30-60 seconds (model loading)
    - For errors: Wait 30 seconds and retry
    """)

st.caption("Powered by Hugging Face Inference APIs • Free to use")
