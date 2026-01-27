import os
import tempfile
import streamlit as st
import langchain
print(f"LangChain version: {langchain.__version__}")
print(f"LangChain path: {langchain.__file__}")

# List available modules
import pkgutil
import langchain as lc
for importer, modname, ispkg in pkgutil.iter_modules(lc.__path__):
    print(f"Module: {modname} (is package: {ispkg})")
# ============================
# LangChain 1.x Imports
# ============================

try:
    # Try different import patterns for LangChain 1.x
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import PromptTemplate
    
    # For LangChain 1.x, try these imports
    try:
        from langchain.chains.summarize import load_summarize_chain
    except ImportError:
        # Alternative import for LangChain 1.x
        from langchain.chains import load_summarize_chain
    
    try:
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
    except ImportError:
        # Fallback to community or base loaders
        from langchain.document_loaders import PyPDFLoader, TextLoader
    
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Installing required packages...")
    
    # Installation instructions
    st.code("""
    # Required packages:
    streamlit==1.53.1
    langchain==1.2.7
    langchain-google-genai==4.2.0
    langchain-community==0.4.1
    langchain-text-splitters==1.1.0
    langchain-core==1.2.7
    pypdf==6.6.2
    """)
    st.stop()

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
# Prompt Templates
# ============================

summary_prompt_template = """
Write a concise summary of the following financial document,
focusing on key financial figures, strategic developments,
and future outlook:

"{text}"

CONCISE SUMMARY:
"""

refine_prompt_template = """
Your job is to produce a final summary of the financial document.

Existing summary:
{existing_answer}

New context:
------------
{text}
------------

Refine the summary if necessary.
If not useful, return the original summary.

REFINED SUMMARY:
"""

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
# Summarization Logic
# ============================

def summarize_documents(docs, chain_type, llm, verbose=False):
    if not docs:
        return "No documents provided."

    try:
        # Create prompt templates
        map_prompt = PromptTemplate.from_template(summary_prompt_template)
        
        if chain_type == "stuff":
            chain = load_summarize_chain(
                llm=llm,
                chain_type="stuff",
                prompt=map_prompt,
                verbose=verbose
            )
            
        elif chain_type == "map_reduce":
            combine_prompt = PromptTemplate.from_template(summary_prompt_template)
            
            chain = load_summarize_chain(
                llm=llm,
                chain_type="map_reduce",
                map_prompt=map_prompt,
                combine_prompt=combine_prompt,
                verbose=verbose
            )
            
        elif chain_type == "refine":
            refine_prompt = PromptTemplate.from_template(refine_prompt_template)
            
            chain = load_summarize_chain(
                llm=llm,
                chain_type="refine",
                question_prompt=map_prompt,
                refine_prompt=refine_prompt,
                verbose=verbose
            )
        else:
            return "Invalid chain type."

        # Invoke the chain
        result = chain.invoke({"input_documents": docs})
        return result["output_text"]
        
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

            st.download_button(
                label="💾 Download Summary",
                data=summary,
                file_name="financial_summary.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ No valid content loaded.")
else:
    st.info("👆 Upload at least one PDF or TXT file.")
