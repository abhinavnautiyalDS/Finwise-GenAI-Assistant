import os
import tempfile
import streamlit as st
import requests
import json

# ============================
# Simplified Imports (No LangChain dependencies)
# ============================

# We'll implement everything without LangChain dependencies
# This makes the app more stable and portable

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
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        white-space: pre-wrap;
    }
    .stExpander > div > div > div {
        background-color: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# DeepSeek API Configuration
# ============================

# Try to get API key from Streamlit secrets
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"
except KeyError:
    # If not in secrets, try environment variable
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"
    
    if not DEEPSEEK_API_KEY:
        st.error("🚨 Please set DEEPSEEK_API_KEY in Streamlit secrets or environment variables.")
        st.info("""
        To set up DeepSeek API:
        1. Get API key from https://platform.deepseek.com/
        2. Add to Streamlit secrets (recommended):
        
        In .streamlit/secrets.toml:
        ```
        DEEPSEEK_API_KEY = "your-api-key-here"
        ```
        
        Or set environment variable:
        ```
        export DEEPSEEK_API_KEY="your-api-key-here"
        ```
        """)
        st.stop()

# ============================
# DeepSeek LLM Client
# ============================

class DeepSeekClient:
    def __init__(self, api_key, temperature=0.3, model="deepseek-chat"):
        self.api_key = api_key
        self.temperature = temperature
        self.model = model
        self.base_url = DEEPSEEK_API_BASE
    
    def invoke(self, prompt, system_message=None):
        """Send a request to DeepSeek API and return the response"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            st.error(f"Failed to parse API response: {e}")
            return None

@st.cache_resource
def get_llm(temp):
    return DeepSeekClient(
        api_key=DEEPSEEK_API_KEY,
        temperature=temp,
        model="deepseek-chat"  # Can also use "deepseek-coder" for code-related tasks
    )

# ============================
# Sidebar Options
# ============================

st.sidebar.header("⚙️ Summarization Options")

temperature = st.sidebar.slider(
    "Temperature",
    0.0,
    1.0,
    0.3,
    0.1
)

chain_type = st.sidebar.selectbox(
    "Chain Type",
    options=["stuff", "map_reduce", "refine"],
    help="stuff: short docs | map_reduce: long docs | refine: best quality"
)

verbose = st.sidebar.checkbox("Verbose (console logs)", value=False)

# Initialize LLM
llm = get_llm(temperature)

# ============================
# Document Processing Functions
# ============================

def extract_text_from_pdf(file_path):
    """Extract text from PDF without PyPDF dependency issues"""
    try:
        # Try PyPDF2 first
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except ImportError:
        try:
            # Try pypdf as fallback
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except ImportError:
            st.error("Please install pypdf: pip install pypdf")
            return ""

def load_documents(uploaded_files):
    """Load documents from uploaded files"""
    raw_texts = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{uploaded_file.name.split('.')[-1]}"
        ) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(temp_path)
                if text:
                    raw_texts.append({
                        "filename": uploaded_file.name,
                        "text": text,
                        "type": "pdf"
                    })
                    st.info(f"✅ Loaded PDF: {uploaded_file.name}")
                else:
                    st.warning(f"⚠️ Could not extract text from {uploaded_file.name}")
            
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                raw_texts.append({
                    "filename": uploaded_file.name,
                    "text": text,
                    "type": "txt"
                })
                st.info(f"✅ Loaded text: {uploaded_file.name}")
            
            else:
                st.warning(f"⚠️ Unsupported file: {uploaded_file.name}")
        
        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return raw_texts

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=100):
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to end at a sentence boundary
        if end < text_length:
            # Look for sentence endings
            sentence_endings = ['. ', '! ', '? ', '\n\n', '\n']
            for ending in sentence_endings:
                pos = text.rfind(ending, start, end)
                if pos != -1 and pos > start + chunk_size * 0.5:  # Don't cut too early
                    end = pos + len(ending)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - chunk_overlap  # Overlap
        
        # Prevent infinite loop
        if start >= text_length:
            break
    
    return chunks

def split_documents(raw_texts, chunk_size=1000, chunk_overlap=100):
    """Split all documents into chunks"""
    all_chunks = []
    
    for doc in raw_texts:
        chunks = split_text_into_chunks(doc["text"], chunk_size, chunk_overlap)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "filename": doc["filename"],
                "chunk_index": i,
                "text": chunk,
                "type": doc["type"]
            })
    
    return all_chunks

# ============================
# Custom Summarization Logic
# ============================

def summarize_stuff_chain(chunks, llm):
    """Simple 'stuff' chain implementation"""
    # Combine all chunks into one text
    combined_text = "\n\n".join([chunk["text"] for chunk in chunks])
    
    prompt = f"""Write a concise summary of the following financial document,
focusing on key financial figures, strategic developments, risks, and future outlook:

{combined_text}

CONCISE SUMMARY (3-5 paragraphs):"""
    
    response = llm.invoke(prompt)
    return response

def summarize_map_reduce_chain(chunks, llm):
    """Simple 'map_reduce' chain implementation"""
    # Map step: Summarize each chunk
    summaries = []
    
    for i, chunk in enumerate(chunks):
        if verbose:
            st.sidebar.write(f"Summarizing chunk {i+1}/{len(chunks)}...")
        
        prompt = f"""Summarize this section of a financial document:

{chunk["text"]}

Focus on key information. Return a brief 2-3 sentence summary:

Section Summary:"""
        
        response = llm.invoke(prompt)
        if response:
            summaries.append(response)
    
    # Reduce step: Combine all summaries
    combined_summaries = "\n\n".join(summaries)
    
    prompt = f"""Combine these section summaries into one cohesive summary of the entire financial document:

{combined_summaries}

Focus on:
1. Key financial figures and performance metrics
2. Strategic developments and initiatives
3. Risks and challenges mentioned
4. Future outlook and guidance

Structure your response in clear paragraphs.

FINAL CONCISE SUMMARY:"""
    
    response = llm.invoke(prompt)
    return response

def summarize_refine_chain(chunks, llm):
    """Simple 'refine' chain implementation"""
    # Start with first chunk
    initial_prompt = f"""Write a summary of this financial document section:

{chunks[0]["text"]}

Focus on key financial figures, strategic developments, and future outlook.

INITIAL SUMMARY:"""
    
    current_summary = llm.invoke(initial_prompt)
    if not current_summary:
        return "Error in initial summarization"
    
    # Refine with remaining chunks
    for i in range(1, len(chunks)):
        if verbose:
            st.sidebar.write(f"Refining with chunk {i+1}/{len(chunks)}...")
        
        refine_prompt = f"""Your job is to produce a final summary of the financial document.

Existing summary:
{current_summary}

New context:
------------
{chunks[i]["text"]}
------------

Refine the summary to incorporate new information from the context.
Maintain focus on financial figures, strategic developments, risks, and future outlook.

REFINED SUMMARY:"""
        
        refined = llm.invoke(refine_prompt)
        if refined:
            current_summary = refined
    
    return current_summary

def summarize_documents(chunks, chain_type, llm, verbose=False):
    """Main summarization function"""
    if not chunks:
        return "No content to summarize."
    
    try:
        if verbose:
            st.sidebar.info(f"Summarizing {len(chunks)} chunks using {chain_type} method")
        
        if chain_type == "stuff":
            if len(chunks) > 15:
                st.warning("⚠️ Using 'stuff' chain with many chunks. Consider 'map_reduce' for better results.")
            return summarize_stuff_chain(chunks, llm)
            
        elif chain_type == "map_reduce":
            return summarize_map_reduce_chain(chunks, llm)
            
        elif chain_type == "refine":
            return summarize_refine_chain(chunks, llm)
            
        else:
            return "Invalid chain type. Using 'map_reduce' as default."
            
    except Exception as e:
        return f"❌ Error during summarization: {str(e)}"

# ============================
# Main UI
# ============================

st.markdown(
    '<h1 class="main-header">💼 Financial Document Summarizer</h1>',
    unsafe_allow_html=True
)

st.write(
    "Upload PDF or TXT financial documents to generate a concise summary using DeepSeek AI."
)

# Model selection
model_option = st.sidebar.selectbox(
    "DeepSeek Model",
    options=["deepseek-chat", "deepseek-coder"],
    help="deepseek-chat: General purpose | deepseek-coder: Better for structured data"
)

# Update LLM with selected model
llm.model = model_option

uploaded_files = st.file_uploader(
    "Choose files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Loading documents..."):
        raw_documents = load_documents(uploaded_files)
    
    if raw_documents:
        # Calculate total text length
        total_text = sum(len(doc["text"]) for doc in raw_documents)
        st.info(f"📄 Loaded {len(raw_documents)} document(s) with {total_text:,} total characters")
        
        # Split documents
        chunks = split_documents(raw_documents)
        st.info(f"📝 Split into {len(chunks)} chunks")
        
        # Show chunk preview
        with st.expander("📋 View Document Chunks"):
            for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
                st.write(f"**{chunk['filename']} - Chunk {chunk['chunk_index']+1}**")
                st.text(chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'])
                st.divider()
        
        if st.button("🚀 Generate Summary", type="primary"):
            with st.spinner("Summarizing with DeepSeek..."):
                summary = summarize_documents(
                    chunks,
                    chain_type,
                    llm,
                    verbose
                )
            
            if summary:
                st.subheader("📊 Document Summary")
                st.markdown(
                    f'<div class="summary-box">{summary}</div>',
                    unsafe_allow_html=True
                )
                
                # Stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Documents", len(raw_documents))
                with col2:
                    st.metric("Chunks", len(chunks))
                with col3:
                    st.metric("Summary Length", f"{len(summary):,} chars")
                
                # Download button
                st.download_button(
                    label="💾 Download Summary",
                    data=summary,
                    file_name="financial_summary.txt",
                    mime="text/plain"
                )
            else:
                st.error("Failed to generate summary. Please check your API key and try again.")
    else:
        st.warning("⚠️ No valid content loaded.")
else:
    st.info("👆 Upload at least one PDF or TXT file.")

# ============================
# Footer
# ============================
st.markdown("---")
st.caption("Built with Streamlit • Powered by DeepSeek AI • No LangChain dependencies")
