import os
import tempfile
import streamlit as st

# ============================
# Simplified Imports (Only what works)
# ============================

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

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
# API Key Setup
# ============================

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
except KeyError:
    st.error("🚨 Please set GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

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

# ============================
# LLM Initialization
# ============================

@st.cache_resource
def get_llm(temp):
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=temp,
        convert_system_message_to_human=True
    )

llm = get_llm(temperature)

# ============================
# Document Loader
# ============================

def load_documents(uploaded_files):
    raw_documents = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{uploaded_file.name.split('.')[-1]}"
        ) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name

        try:
            if uploaded_file.type == "application/pdf":
                loader = PyPDFLoader(temp_path)
                docs = loader.load()
                raw_documents.extend(docs)
                st.info(f"✅ Loaded {len(docs)} pages from {uploaded_file.name}")

            elif uploaded_file.type == "text/plain":
                loader = TextLoader(temp_path)
                docs = loader.load()
                raw_documents.extend(docs)
                st.info(f"✅ Loaded text from {uploaded_file.name}")

            else:
                st.warning(f"⚠️ Unsupported file: {uploaded_file.name}")

        except Exception as e:
            st.error(f"Error loading {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    return raw_documents

# ============================
# Text Splitter
# ============================

def split_documents(raw_documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    return splitter.split_documents(raw_documents)

# ============================
# Custom Summarization Logic (No load_summarize_chain)
# ============================

def summarize_stuff_chain(docs, llm):
    """Simple 'stuff' chain implementation"""
    # Combine all chunks into one text
    combined_text = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""Write a concise summary of the following financial document,
focusing on key financial figures, strategic developments, and future outlook:

{combined_text}

CONCISE SUMMARY:"""
    
    response = llm.invoke(prompt)
    return response.content

def summarize_map_reduce_chain(docs, llm):
    """Simple 'map_reduce' chain implementation"""
    # Map step: Summarize each chunk
    summaries = []
    for i, doc in enumerate(docs):
        prompt = f"""Summarize this section of a financial document:

{doc.page_content}

Section Summary:"""
        
        response = llm.invoke(prompt)
        summaries.append(response.content)
    
    # Reduce step: Combine all summaries
    combined_summaries = "\n\n".join(summaries)
    
    prompt = f"""Combine these section summaries into one cohesive summary of the entire financial document:

{combined_summaries}

Focus on key financial figures, strategic developments, and future outlook.

FINAL CONCISE SUMMARY:"""
    
    response = llm.invoke(prompt)
    return response.content

def summarize_refine_chain(docs, llm):
    """Simple 'refine' chain implementation"""
    # Start with first chunk
    initial_prompt = f"""Write a summary of this financial document section:

{docs[0].page_content}

Focus on key financial figures, strategic developments, and future outlook.

INITIAL SUMMARY:"""
    
    current_summary = llm.invoke(initial_prompt).content
    
    # Refine with remaining chunks
    for i in range(1, len(docs)):
        refine_prompt = f"""Your job is to produce a final summary of the financial document.

Existing summary:
{current_summary}

New context:
------------
{docs[i].page_content}
------------

Refine the summary if necessary to incorporate new information.
If not useful, return the original summary.

REFINED SUMMARY:"""
        
        current_summary = llm.invoke(refine_prompt).content
    
    return current_summary

def summarize_documents(docs, chain_type, llm, verbose=False):
    """Main summarization function using custom implementations"""
    if not docs:
        return "No documents provided."
    
    try:
        if verbose:
            st.sidebar.info(f"Summarizing {len(docs)} chunks using {chain_type} method")
        
        if chain_type == "stuff":
            if len(docs) > 10:
                st.warning("⚠️ Using 'stuff' chain with many chunks. Consider 'map_reduce' for better results.")
            return summarize_stuff_chain(docs, llm)
            
        elif chain_type == "map_reduce":
            return summarize_map_reduce_chain(docs, llm)
            
        elif chain_type == "refine":
            return summarize_refine_chain(docs, llm)
            
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
    "Upload PDF or TXT financial documents to generate a concise summary."
)

uploaded_files = st.file_uploader(
    "Choose files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Loading documents..."):
        raw_documents = load_documents(uploaded_files)

    if raw_documents:
        docs = split_documents(raw_documents)
        st.info(f"📝 Split into {len(docs)} chunks")

        if st.button("🚀 Generate Summary", type="primary"):
            with st.spinner("Summarizing..."):
                summary = summarize_documents(
                    docs,
                    chain_type,
                    llm,
                    verbose
                )

            st.subheader("📊 Document Summary")
            st.markdown(
                f'<div class="summary-box">{summary}</div>',
                unsafe_allow_html=True
            )

            # Show token count estimate
            total_chars = sum(len(doc.page_content) for doc in docs)
            st.caption(f"📊 Processed approximately {total_chars:,} characters across {len(docs)} chunks")

            st.download_button(
                label="💾 Download Summary",
                data=summary,
                file_name="financial_summary.txt",
                mime="text/plain"
            )
            
            # Show sample of processed chunks (for debugging)
            if verbose:
                with st.expander("🔍 View Processed Chunks (Debug)"):
                    for i, doc in enumerate(docs[:3]):  # Show first 3 chunks
                        st.write(f"**Chunk {i+1}** (Length: {len(doc.page_content)} chars)")
                        st.text(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
                        st.divider()
    else:
        st.warning("⚠️ No valid content loaded.")
else:
    st.info("👆 Upload at least one PDF or TXT file.")

# ============================
# Footer
# ============================
st.markdown("---")
st.caption("Built with Streamlit and Google Gemini • Uses custom summarization chains")
