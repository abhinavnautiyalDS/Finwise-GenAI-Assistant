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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Custom CSS
# ============================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .summary-box {
        background-color: #f0f8ff;
        color: #000000;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 1.1rem;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Hugging Face Configuration for Qwen2.5-3B-Instruct
# ============================
HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-3B-Instruct"

# Try to get Hugging Face token from secrets (optional, improves rate limits)
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
    st.sidebar.success("✓ Hugging Face token loaded")
except (KeyError, AttributeError):
    HF_TOKEN = None
    HEADERS = {}
    st.sidebar.info("ℹ️ Using Hugging Face without token (rate limits apply)")

# ============================
# Sidebar Options
# ============================
st.sidebar.header("⚙️ Summarization Options")

temperature = st.sidebar.slider(
    "Temperature", 0.1, 1.0, 0.7, 0.1,
    help="Controls randomness: Lower = more deterministic, Higher = more creative"
)

max_length = st.sidebar.slider(
    "Max Summary Length", 100, 500, 300, 50,
    help="Maximum length of summary in tokens"
)

min_length = st.sidebar.slider(
    "Min Summary Length", 50, 200, 100, 25,
    help="Minimum length of summary in tokens"
)

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF using pypdf"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()
    except ImportError:
        st.error("Please install pypdf: pip install pypdf")
        return ""
    except Exception as e:
        return f"PDF extraction error: {str(e)}"

def process_uploaded_files(uploaded_files):
    """Process uploaded files and extract text"""
    all_text = ""
    file_details = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{uploaded_file.name.split('.')[-1]}"
        ) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            file_text = ""
            if uploaded_file.type == "application/pdf":
                file_text = extract_text_from_pdf(temp_path)
                if file_text and not file_text.startswith("PDF extraction error"):
                    file_details.append({
                        "name": uploaded_file.name,
                        "type": "PDF",
                        "chars": len(file_text)
                    })
                else:
                    st.warning(f"⚠️ Could not extract text from {uploaded_file.name}")
                    continue
                    
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_text = f.read()
                file_details.append({
                    "name": uploaded_file.name,
                    "type": "TXT",
                    "chars": len(file_text)
                })
                
            else:
                st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                continue
            
            if file_text:
                all_text += f"\n\n{'='*60}\nDocument: {uploaded_file.name}\n{'='*60}\n\n{file_text}"
                
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip(), file_details

# ============================
# Qwen2.5-3B-Instruct Summarization
# ============================
def summarize_with_qwen(text, temperature=0.7, max_length=300, min_length=100):
    """Summarize text using Qwen2.5-3B-Instruct via Hugging Face Inference API"""
    
    # Prepare the prompt for Qwen
    prompt = f"""<|im_start|>system
You are a financial analyst expert. Summarize the following financial document(s) concisely and accurately.
Focus on key financial figures, strategic developments, risks, and future outlook.<|im_end|>
<|im_start|>user
Please provide a comprehensive summary of this financial document:

{text[:15000]}  # Truncate to avoid token limits

Structure your response with clear paragraphs covering:
1. Key financial metrics and performance
2. Strategic initiatives and developments  
3. Identified risks and challenges
4. Future outlook and guidance
5. Important recommendations or conclusions

Financial Summary:<|im_end|>
<|im_start|>assistant
"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "min_new_tokens": min_length,
            "temperature": temperature,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True,
            "return_full_text": False
        },
        "options": {
            "use_cache": False,
            "wait_for_model": True
        }
    }
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                summary = result[0].get('generated_text', '')
                # Clean up the response
                summary = summary.split('<|im_end|>')[0].strip()
                return summary
            else:
                return f"Unexpected response format: {result}"
                
        elif response.status_code == 503:
            # Model is loading, get estimate
            try:
                estimate = response.json().get('estimated_time', 30)
                return f"Model is loading. Please try again in about {int(estimate)} seconds."
            except:
                return "Model is loading. Please try again in 30 seconds."
                
        else:
            return f"API Error {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "Request timeout. The model might be busy. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# ============================
# Text Chunking for Long Documents
# ============================
def chunk_text(text, chunk_size=10000):
    """Split text into chunks for processing"""
    chunks = []
    words = text.split()
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_long_document(text, temperature=0.7):
    """Summarize long documents using map-reduce approach"""
    chunks = chunk_text(text, chunk_size=8000)
    
    if len(chunks) == 1:
        return summarize_with_qwen(text, temperature, max_length, min_length)
    
    st.info(f"📊 Document is long. Processing {len(chunks)} chunks...")
    
    # Summarize each chunk
    chunk_summaries = []
    progress_bar = st.progress(0)
    
    for i, chunk in enumerate(chunks):
        progress_bar.progress((i + 1) / len(chunks), text=f"Summarizing chunk {i+1}/{len(chunks)}")
        chunk_summary = summarize_with_qwen(
            chunk,
            temperature,
            max_length=150,
            min_length=50
        )
        if chunk_summary and not chunk_summary.startswith("Error"):
            chunk_summaries.append(chunk_summary)
    
    # Combine chunk summaries
    if chunk_summaries:
        combined_summaries = "\n\n".join(chunk_summaries)
        final_summary = summarize_with_qwen(
            f"Combine these partial summaries into one comprehensive summary:\n\n{combined_summaries}",
            temperature,
            max_length,
            min_length
        )
        return final_summary
    else:
        return "Failed to generate chunk summaries."

# ============================
# Main App Interface
# ============================
st.markdown('<h1 class="main-header">💼 Financial Document Summarizer</h1>', unsafe_allow_html=True)
st.write("Upload financial documents (PDF/TXT) for AI-powered summarization using **Qwen2.5-3B-Instruct**")

# File uploader
uploaded_files = st.file_uploader(
    "📁 Choose files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Upload multiple PDF or text files"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
    
    # Process files
    with st.spinner("🔍 Extracting text from documents..."):
        extracted_text, file_details = process_uploaded_files(uploaded_files)
    
    if extracted_text:
        # Display file details
        st.subheader("📄 Uploaded Files")
        col1, col2, col3 = st.columns(3)
        total_chars = 0
        for detail in file_details:
            total_chars += detail['chars']
        
        with col1:
            st.metric("Total Files", len(file_details))
        with col2:
            st.metric("Total Characters", f"{total_chars:,}")
        with col3:
            st.metric("Average per File", f"{total_chars//len(file_details):,}")
        
        # Show preview
        with st.expander("📋 Preview Extracted Text"):
            preview_text = extracted_text[:3000]
            if len(extracted_text) > 3000:
                preview_text += "\n\n[...truncated...]"
            st.text(preview_text)
        
        # Warning for very long documents
        if total_chars > 20000:
            st.markdown(
                '<div class="warning-box">'
                '⚠️ <b>Note:</b> Document is quite long. Summarization may take longer. '
                'The app will process it in chunks for better results.'
                '</div>',
                unsafe_allow_html=True
            )
        
        # Generate summary
        if st.button("🚀 Generate Summary with Qwen2.5-3B-Instruct", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating summary (this may take 30-60 seconds)..."):
                if total_chars > 15000:
                    summary = summarize_long_document(extracted_text, temperature)
                else:
                    summary = summarize_with_qwen(
                        extracted_text,
                        temperature,
                        max_length,
                        min_length
                    )
            
            # Display summary
            st.subheader("📋 AI-Generated Financial Summary")
            
            if summary and not summary.startswith("Error") and not summary.startswith("API"):
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Stats
                st.subheader("📊 Summary Statistics")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Original", f"{total_chars:,} chars")
                with cols[1]:
                    st.metric("Summary", f"{len(summary):,} chars")
                with cols[2]:
                    if total_chars > 0:
                        compression = 100 - (len(summary) / total_chars * 100)
                        st.metric("Compression", f"{compression:.1f}%")
                    else:
                        st.metric("Compression", "N/A")
                with cols[3]:
                    word_count = len(summary.split())
                    st.metric("Words", word_count)
                
                # Download button
                st.download_button(
                    label="💾 Download Summary",
                    data=summary,
                    file_name="financial_summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error(f"❌ Could not generate summary: {summary}")
                st.info("""
                **Troubleshooting tips:**
                1. The model might be loading (wait 30 seconds and try again)
                2. Try reducing the document size
                3. Check your internet connection
                4. If using HF_TOKEN, ensure it's valid
                """)
    else:
        st.error("❌ Could not extract text from uploaded files")
else:
    st.info("👆 Upload PDF or text files to begin summarization")

# ============================
# Instructions & Info
# ============================
st.markdown("---")
with st.expander("ℹ️ About Qwen2.5-3B-Instruct & Setup Instructions"):
    st.markdown("""
    ### 🤖 About Qwen2.5-3B-Instruct
    - **Model**: Qwen2.5-3B-Instruct from Alibaba Cloud
    - **Size**: 3 Billion parameters (lightweight but capable)
    - **License**: Apache 2.0 (commercially usable)
    - **Best for**: Text summarization, analysis, and Q&A
    
    ### ⚙️ Setup Instructions
    
    **1. Requirements.txt:**
    ```txt
    streamlit>=1.28.0
    requests>=2.28.0
    pypdf>=3.0.0
    ```
    
    **2. Optional: Get Hugging Face Token (for better rate limits):**
    1. Go to https://huggingface.co/settings/tokens
    2. Create a new token (select "read" role)
    3. Add to Streamlit secrets:
    ```toml
    # .streamlit/secrets.toml
    HF_TOKEN = "your-huggingface-token-here"
    ```
    
    **3. File Structure:**
    ```
    your-app/
    ├── App_task06.py
    ├── requirements.txt
    └── .streamlit/
        └── secrets.toml  # optional
    ```
    
    ### ⏱️ Performance Notes
    - First request may take 30-60 seconds (model loading)
    - Subsequent requests are faster
    - Free tier has rate limits (10-30 requests/hour without token)
    - With HF_TOKEN: ~500 requests/hour
    
    ### 📝 Tips for Best Results
    1. **Document size**: Works best with documents under 20,000 characters
    2. **Temperature**: Use 0.7 for balanced results
    3. **Format**: Clean, well-structured documents work best
    4. **Retry**: If model is loading, wait 30 seconds and try again
    """)

st.caption("Built with Streamlit • Powered by Qwen2.5-3B-Instruct (Free via Hugging Face)")
