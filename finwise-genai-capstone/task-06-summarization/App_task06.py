import os
import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.prompts import PromptTemplate as LangchainPromptTemplate
from packaging import version
import langchain
import tempfile

# Page configuration for a clean, wide layout
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility and aesthetics
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .summary-box {
        background-color: #f0f8ff;
        color: #000000;  /* <-- Set text color to black */
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        white-space: pre-wrap;  /* Preserve line breaks */
    }
    .stExpander > div > div > div {
        background-color: #fafafa;
    }
    </style>
""", unsafe_allow_html=True)

# Retrieve API key from Streamlit secrets
try:
    api_key = st.secrets['GOOGLE_API_KEY']
except KeyError:
    st.error("🚨 Please set `GOOGLE_API_KEY` in your Streamlit secrets file (.streamlit/secrets.toml).")
    st.stop()

# Configure environment and GenAI
os.environ['GOOGLE_API_KEY'] = api_key
genai.configure(api_key=api_key)

# Sidebar for options
st.sidebar.header("⚙️ Summarization Options")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
chain_type = st.sidebar.selectbox(
    "Chain Type",
    options=["stuff", "map_reduce", "refine"],
    help="stuff: Fast for short docs; map_reduce: For long docs; refine: High-quality coherent summaries."
)
verbose = st.sidebar.checkbox("Verbose (logs in console)", value=False)

# Initialize LLM
@st.cache_resource
def get_llm(temp):
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=temp)

llm = get_llm(temperature)

# Prompt templates
summary_prompt_template = """Write a concise summary of the following financial document, focusing on key financial figures, strategic developments, and future outlook:

"{text}"

CONCISE SUMMARY:"""

refine_prompt_template = """Your job is to produce a final summary of the provided financial document.
We have an existing summary up to a certain point: {existing_answer}
We have the opportunity to refine the existing summary (only if needed) with some more context below:
------------
{text}
------------
Given the new context, refine the original summary to include any new key financial figures, strategic developments, or future outlook.
If the context isn't useful, return the original summary.
REFINED SUMMARY:"""

# Document loading function
@st.cache_data
def load_documents(uploaded_files):
    raw_documents = []
    for uploaded_file in uploaded_files:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        try:
            # Load based on file type
            if uploaded_file.type == "application/pdf":
                loader = PyPDFLoader(temp_file_path)
                docs = loader.load()
                raw_documents.extend(docs)
                st.info(f"✅ Loaded {len(docs)} pages from PDF: {uploaded_file.name}")
            elif uploaded_file.type == "text/plain":
                loader = TextLoader(temp_file_path)
                docs = loader.load()
                raw_documents.extend(docs)
                st.info(f"✅ Loaded text from TXT: {uploaded_file.name}")
            else:
                st.warning(f"⚠️ Unsupported file type: {uploaded_file.type} for {uploaded_file.name}")
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    return raw_documents

# Text splitter
@st.cache_data
def split_documents(raw_documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    return text_splitter.split_documents(raw_documents)

# Summarization function
def summarize_documents(docs, chain_type, llm, verbose=False):
    if not docs:
        return "No documents provided for summarization."

    summary_prompt = PromptTemplate(template=summary_prompt_template, input_variables=["text"])

    if chain_type == "stuff":
        total_length = sum(len(doc.page_content) for doc in docs)
        if total_length > 50000:
            st.warning("📄 Document is very large; the model may truncate content.")
        chain = load_summarize_chain(
            llm,
            chain_type="stuff",
            prompt=summary_prompt,
            verbose=verbose
        )

    elif chain_type == "map_reduce":
        combine_prompt = PromptTemplate(template=summary_prompt_template, input_variables=["text"])
        if version.parse(langchain.__version__) >= version.parse("0.2.0"):
            chain = load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=summary_prompt,
                combine_prompt=combine_prompt,
                combine_document_variable_name="text",
                verbose=verbose
            )
        else:
            chain = load_summarize_chain(
                llm,
                chain_type="map_reduce",
                map_prompt=summary_prompt,
                reduce_prompt=combine_prompt,
                combine_document_variable_name="text",
                verbose=verbose
            )

    elif chain_type == "refine":
        initial_prompt = PromptTemplate(template=summary_prompt_template, input_variables=["text"])
        refine_prompt = PromptTemplate(template=refine_prompt_template, input_variables=["existing_answer", "text"])
        chain = load_summarize_chain(
            llm,
            chain_type="refine",
            question_prompt=initial_prompt,
            refine_prompt=refine_prompt,
            verbose=verbose
        )
    else:
        return "Invalid chain_type."

    try:
        result = chain.invoke({"input_documents": docs}, return_only_outputs=True)
        return result['output_text']
    except Exception as e:
        return f"❌ Error during summarization: {str(e)}"

# Main content
st.markdown('<h1 class="main-header">💼 Financial Document Summarizer</h1>', unsafe_allow_html=True)
st.write("Upload PDF or TXT financial documents to generate a concise summary highlighting key financial figures, strategic developments, and future outlook.")

# File uploader
uploaded_files = st.file_uploader(
    "Choose files",
    type=['pdf', 'txt'],
    accept_multiple_files=True,
    help="Supports multiple files; content will be combined."
)

if uploaded_files:
    with st.spinner("Loading documents..."):
        raw_documents = load_documents(uploaded_files)
    
    if raw_documents:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Loaded {len(raw_documents)} pages/documents from {len(uploaded_files)} file(s).")
        with col2:
            if st.button("🔄 Reprocess", key="reprocess"):
                st.rerun()
        
        with st.spinner("Splitting into chunks..."):
            docs = split_documents(raw_documents)
        
        st.info(f"📝 Split into {len(docs)} text chunks for processing.")
        
        # Preview
        with st.expander("👀 Preview first 3 chunks", expanded=False):
            for i, doc in enumerate(docs[:3]):
                with st.container():
                    st.write(f"**Chunk {i+1}:**")
                    st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
        
        # Summarize button
        if st.button("🚀 Generate Summary", type="primary"):
            with st.spinner(f"Summarizing with '{chain_type}' chain... This may take a while for long documents."):
                summary = summarize_documents(docs, chain_type, llm, verbose)
            
            st.subheader("📊 Document Summary")
            st.markdown(f'<div class="summary-box"><p>{summary}</p></div>', unsafe_allow_html=True)
            
            # Download summary
            st.download_button(
                label="💾 Download Summary",
                data=summary,
                file_name="financial_summary.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ No valid content loaded from the uploaded files.")
else:
    st.info("👆 Please upload at least one PDF or TXT file to get started.")
