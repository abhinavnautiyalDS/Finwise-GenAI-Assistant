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
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Custom CSS
# ============================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .summary-box {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #1f77b4;
        line-height: 1.7;
        font-size: 1.05rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .model-card {
        background-color: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-size: 1rem;
    }
    .free-badge {
        background-color: #10b981;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .token-info {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# OpenRouter Configuration
# ============================
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Available FREE models on OpenRouter (as of 2024)
FREE_MODELS = [
    {
        "id": "google/gemma-2-2b-it",
        "name": "Gemma 2B",
        "provider": "Google",
        "free": True,
        "context": 8192,
        "description": "Lightweight & fast, good for basic summarization"
    },
    {
        "id": "microsoft/phi-3-mini-128k-instruct",
        "name": "Phi-3 Mini",
        "provider": "Microsoft",
        "free": True,
        "context": 128000,
        "description": "Excellent for long documents, very capable"
    },
    {
        "id": "mistralai/mistral-7b-instruct",
        "name": "Mistral 7B",
        "provider": "Mistral AI",
        "free": True,
        "context": 32768,
        "description": "Balanced performance, good for all tasks"
    },
    {
        "id": "huggingfaceh4/zephyr-7b-beta",
        "name": "Zephyr 7B",
        "provider": "Hugging Face",
        "free": True,
        "context": 32768,
        "description": "Tuned for instruction following"
    },
    {
        "id": "meta-llama/llama-3.2-3b-instruct",
        "name": "Llama 3.2 3B",
        "provider": "Meta",
        "free": True,
        "context": 128000,
        "description": "Latest Llama 3.2, efficient & powerful"
    }
]

# ============================
# Sidebar Configuration
# ============================
st.sidebar.title("🔧 OpenRouter Setup")

# Get API Key
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    st.sidebar.success("✓ API key loaded from secrets")
except KeyError:
    OPENROUTER_API_KEY = st.sidebar.text_input(
        "Enter OpenRouter API Key:",
        type="password",
        help="Get free key from https://openrouter.ai"
    )
    if OPENROUTER_API_KEY:
        st.sidebar.success("✓ API key entered")
    else:
        st.sidebar.warning("⚠️ API key required for free tier")

# Model Selection
st.sidebar.subheader("🤖 Model Selection")

# Show model cards
for model in FREE_MODELS:
    free_badge = "🆓 FREE" if model["free"] else ""
    st.sidebar.markdown(f"""
    <div class="model-card">
        <b>{model['name']}</b> {free_badge}<br>
        <small>{model['provider']} • {model['context']:,} tokens</small><br>
        <small>{model['description']}</small>
    </div>
    """, unsafe_allow_html=True)

selected_model_id = st.sidebar.selectbox(
    "Choose Model:",
    options=[model["id"] for model in FREE_MODELS],
    format_func=lambda x: next((f"{m['name']} ({m['provider']})" for m in FREE_MODELS if m["id"] == x), x)
)

# Get selected model info
selected_model = next((m for m in FREE_MODELS if m["id"] == selected_model_id), FREE_MODELS[0])

# Summarization Settings
st.sidebar.subheader("⚙️ Summarization Settings")

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Lower = more factual, Higher = more creative"
)

max_tokens = st.sidebar.slider(
    "Max Summary Length",
    min_value=100,
    max_value=2000,
    value=500,
    step=50,
    help="Maximum tokens in summary"
)

# Token info
st.sidebar.markdown(f"""
<div class="token-info">
<strong>Free Tier Info:</strong><br>
• 500 free requests per day<br>
• No credit card required<br>
• {selected_model['context']:,} context window
</div>
""", unsafe_allow_html=True)

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"--- Page {page_num} ---\n{page_text}\n\n"
        
        return text.strip() if text else "No text could be extracted"
        
    except ImportError:
        return "ERROR: Please install pypdf"
    except Exception as e:
        return f"ERROR: {str(e)}"

def process_uploaded_files(uploaded_files):
    """Process uploaded files and extract text"""
    all_text = ""
    file_details = []
    
    for uploaded_file in uploaded_files:
        # Create temporary file
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            file_text = ""
            if uploaded_file.type == "application/pdf":
                file_text = extract_text_from_pdf(temp_path)
                file_type = "📄 PDF"
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_text = f.read()
                file_type = "📝 TXT"
            else:
                st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                continue
            
            if file_text and not file_text.startswith("ERROR"):
                # Add to combined text
                all_text += f"\n\n{'='*60}\n📁 File: {uploaded_file.name}\n{'='*60}\n\n{file_text}"
                
                # Store file details
                file_details.append({
                    "name": uploaded_file.name,
                    "type": file_type,
                    "size": len(uploaded_file.getvalue()),
                    "text_length": len(file_text),
                    "pages": file_text.count("--- Page") if uploaded_file.type == "application/pdf" else 1
                })
                
                st.success(f"✅ Processed: {uploaded_file.name}")
            else:
                st.error(f"❌ Failed to process: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip(), file_details

# ============================
# OpenRouter API Function
# ============================
def summarize_with_openrouter(text, model_id, temperature=0.3, max_tokens=500):
    """Summarize text using OpenRouter API"""
    
    if not OPENROUTER_API_KEY:
        return "❌ Please provide OpenRouter API key"
    
    # Truncate text based on model context window
    max_chars = selected_model["context"] * 4  # Rough estimate: 4 chars per token
    if len(text) > max_chars:
        text = text[:max_chars]
        st.info(f"📝 Text truncated to {max_chars:,} characters for model limits")
    
    # Prepare the prompt based on model type
    if "gemma" in model_id.lower():
        prompt = f"""<start_of_turn>user
Please summarize the following document concisely and accurately:

{text}

Focus on key points, important facts, and main conclusions. Provide a clear, structured summary.

Summary:<end_of_turn>
<start_of_turn>model
"""
    elif "phi" in model_id.lower():
        prompt = f"""<|user|>
Please provide a comprehensive summary of the following document:

{text}

Focus on key insights, important details, and overall conclusions.<|end|>
<|assistant|>
"""
    elif "llama" in model_id.lower():
        prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Please summarize the following document:

{text}

Focus on the main points and key information.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    else:
        # Default prompt for other models
        prompt = f"""Please summarize the following document concisely:

{text}

Provide a clear summary focusing on:
1. Main points and key ideas
2. Important facts and figures
3. Conclusions and recommendations

Summary:"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://document-summarizer.streamlit.app",  # Your site
        "X-Title": "Document Summarizer"
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert document summarizer. Provide concise, accurate summaries focusing on key information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                summary = result["choices"][0]["message"]["content"].strip()
                # Clean up any leftover prompt fragments
                summary = summary.split("<|")[0].split("<end_of_turn>")[0].strip()
                return summary
            else:
                return f"❌ No summary in response: {result}"
                
        elif response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please wait a moment and try again."
            
        elif response.status_code == 401:
            return "❌ Invalid API key. Please check your OpenRouter API key."
            
        else:
            error_msg = response.text[:200] if response.text else "Unknown error"
            return f"❌ API Error {response.status_code}: {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ============================
# Main App Interface
# ============================
st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align: center; color: #4b5563; margin-bottom: 2rem;">
Using: <b>{selected_model['name']}</b> • {selected_model['provider']} • 🆓 FREE Tier
</div>
""", unsafe_allow_html=True)

# File upload section
uploaded_files = st.file_uploader(
    "📁 Drag and drop files here",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Upload multiple PDF or text files"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    # Process files
    with st.spinner("🔍 Extracting text from documents..."):
        extracted_text, file_details = process_uploaded_files(uploaded_files)
    
    if extracted_text and len(extracted_text) > 100:
        # Display file statistics
        st.subheader("📊 Document Statistics")
        
        col1, col2, col3 = st.columns(3)
        total_chars = sum(fd["text_length"] for fd in file_details)
        
        with col1:
            st.metric("Total Files", len(file_details))
        with col2:
            st.metric("Total Characters", f"{total_chars:,}")
        with col3:
            st.metric("Words", f"{len(extracted_text.split()):,}")
        
        # Preview extracted text
        with st.expander("📋 Preview Extracted Text", expanded=False):
            preview = extracted_text[:2000]
            if len(extracted_text) > 2000:
                preview += "\n\n[... document truncated for preview ...]"
            st.text(preview)
        
        # Generate summary button
        st.divider()
        
        if st.button("🚀 Generate Summary with AI", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Summarizing with {selected_model['name']}..."):
                summary = summarize_with_openrouter(
                    extracted_text,
                    selected_model_id,
                    temperature,
                    max_tokens
                )
            
            # Display results
            if summary and not summary.startswith("❌") and not summary.startswith("⚠️"):
                st.subheader("📋 AI Summary")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Summary statistics
                st.subheader("📈 Summary Statistics")
                
                cols = st.columns(4)
                with cols[0]:
                    compression = 100 - (len(summary) / total_chars * 100) if total_chars > 0 else 0
                    st.metric("Compression", f"{compression:.1f}%")
                with cols[1]:
                    st.metric("Summary Length", f"{len(summary):,} chars")
                with cols[2]:
                    st.metric("Words", len(summary.split()))
                with cols[3]:
                    st.metric("Model", selected_model['name'])
                
                # Download button
                st.download_button(
                    "💾 Download Summary",
                    summary,
                    file_name=f"summary_{selected_model['name'].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error(f"Summary generation failed: {summary}")
    else:
        st.error("❌ Could not extract sufficient text from files")
else:
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #f8fafc; border-radius: 15px;">
        <div style="font-size: 4rem;">📁</div>
        <h3 style="color: #1f77b4;">Ready to Summarize</h3>
        <p style="color: #64748b;">Upload documents to get AI-powered summaries</p>
        <p style="color: #94a3b8;">Free • Fast • Multiple Models</p>
        </div>
        """, unsafe_allow_html=True)

# ============================
# Instructions & Information
# ============================
with st.expander("ℹ️ About OpenRouter & Setup Instructions", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **🎯 Why OpenRouter?**
        
        - **Multiple free models**: Access to Llama, Mistral, Gemma, etc.
        - **No credit card required**: Truly free tier
        - **500 free requests/day**: More than enough for personal use
        - **Easy setup**: Just API key needed
        
        ### **🚀 Recommended Models**
        
        1. **Phi-3 Mini** (Microsoft)
           - Best for long documents
           - 128K context window
           
        2. **Gemma 2B** (Google)
           - Fast and lightweight
           - Good for basic summarization
           
        3. **Llama 3.2 3B** (Meta)
           - Latest technology
           - Good balance of speed & quality
        """)
    
    with col2:
        st.markdown("""
        ### **⚙️ Setup Instructions**
        
        1. **Get FREE API Key**:
           - Visit [OpenRouter](https://openrouter.ai)
           - Sign up (email only, no credit card)
           - Get 500 free requests/day
        
        2. **Add to Streamlit Secrets**:
           ```toml
           # .streamlit/secrets.toml
           OPENROUTER_API_KEY = "your-key-here"
           ```
        
        3. **requirements.txt**:
           ```txt
           streamlit>=1.28.0
           requests>=2.28.0
           pypdf>=3.0.0
           ```
        
        4. **Deploy** to Streamlit Cloud
        
        ### **💡 Tips for Best Results**
        - Use **Phi-3 Mini** for long documents
        - Keep **temperature** low (0.3) for factual summaries
        - **Truncation** happens automatically if text is too long
        - First request might be slower (model loading)
        """)

st.markdown("---")
st.caption("""
<div style="text-align: center; color: #94a3b8;">
Built with ❤️ using Streamlit • Powered by OpenRouter • 
<a href="https://openrouter.ai" target="_blank" style="color: #667eea;">Get your free API key</a>
</div>
""", unsafe_allow_html=True)

# ============================
# Debug Section (Optional)
# ============================
if st.sidebar.checkbox("Show debug info", value=False):
    st.sidebar.write("**Debug Information:**")
    st.sidebar.write(f"API Key exists: {bool(OPENROUTER_API_KEY)}")
    st.sidebar.write(f"Selected model: {selected_model_id}")
    st.sidebar.write(f"Model context: {selected_model['context']:,} tokens")
