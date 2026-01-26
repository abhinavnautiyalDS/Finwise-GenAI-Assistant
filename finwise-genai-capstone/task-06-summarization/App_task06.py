import os
import tempfile
import streamlit as st
import google.generativeai as genai
import requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader


# =====================================================
# Page configuration
# =====================================================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# Custom CSS (UNCHANGED)
# =====================================================
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
""", unsafe_allow_html=True)

# =====================================================
# API KEY
# =====================================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("🚨 Please set GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

os.environ["GOOGLE_API_KEY"] = api_key
genai.configure(api_key=api_key)

# =====================================================
# Sidebar
# =====================================================
st.sidebar.header("⚙️ Summarization Options")

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3, 0.1)

chain_type = st.sidebar.selectbox(
    "Chain Type",
    options=["stuff", "map_reduce", "refine"],
    help="UI preserved (internally modern LCEL is used)"
)

verbose = st.sidebar.checkbox("Verbose (logs in console)", value=False)

# =====================================================
# LLM
# =====================================================
@st.cache_resource
def get_llm(temp):
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=temp
    )

llm = get_llm(temperature)

# =====================================================
# PROMPTS
# =====================================================
summary_prompt = PromptTemplate(
    template="""
Summarize the following financial document.
Focus on:
- key financial figures
- strategy
- future outlook

TEXT:
{text}
""",
    input_variables=["text"],
)

refine_prompt = PromptTemplate(
    template="""
Existing summary:
{existing_answer}

New context:
{text}

Refine the summary if needed.
If not useful, return the original summary.
""",
    input_variables=["existing_answer", "text"],
)

output_parser = StrOutputParser()

summary_chain = summary_prompt | llm | output_parser
refine_chain = refine_prompt | llm | output_parser

# =====================================================
# LOAD DOCUMENTS
# =====================================================
@st.cache_data
def load_documents(uploaded_files):
    docs = []

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            path = tmp.name

        try:
            if file.type == "application/pdf":
                docs.extend(PyPDFLoader(path).load())
            elif file.type == "text/plain":
                docs.extend(TextLoader(path).load())
        finally:
            os.unlink(path)

    return docs

# =====================================================
# SPLIT DOCUMENTS
# =====================================================
@st.cache_data
def split_documents(raw_docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    return splitter.split_documents(raw_docs)

# =====================================================
# SUMMARIZATION LOGIC (MODERN)
# =====================================================
def summarize_documents(docs, chain_type):
    if not docs:
        return "No documents provided."

    chunks = [doc.page_content for doc in docs]

    # ---------- STUFF ----------
    if chain_type == "stuff":
        combined = "\n\n".join(chunks)
        return summary_chain.invoke({"text": combined})

    # ---------- MAP REDUCE ----------
    if chain_type == "map_reduce":
        partials = []
        for chunk in chunks:
            partials.append(summary_chain.invoke({"text": chunk}))

        combined = "\n\n".join(partials)
        return summary_chain.invoke({"text": combined})

    # ---------- REFINE ----------
    if chain_type == "refine":
        summary = summary_chain.invoke({"text": chunks[0]})

        for chunk in chunks[1:]:
            summary = refine_chain.invoke({
                "existing_answer": summary,
                "text": chunk
            })

        return summary

    return "Invalid chain type."


# =====================================================
# MAIN UI
# =====================================================
st.markdown('<h1 class="main-header">💼 Financial Document Summarizer</h1>', unsafe_allow_html=True)

st.write(
    "Upload PDF or TXT financial documents to generate a concise summary "
    "highlighting key financial figures, strategic developments, and future outlook."
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

        col1, col2 = st.columns([3, 1])

        with col1:
            st.success(
                f"✅ Loaded {len(raw_documents)} pages from {len(uploaded_files)} file(s)."
            )

        with col2:
            if st.button("🔄 Reprocess"):
                st.rerun()

        with st.spinner("Splitting into chunks..."):
            docs = split_documents(raw_documents)

        st.info(f"📝 Split into {len(docs)} text chunks.")

        with st.expander("👀 Preview first 3 chunks"):
            for i, doc in enumerate(docs[:3]):
                st.text(doc.page_content[:300] + "...")

        if st.button("🚀 Generate Summary", type="primary"):

            with st.spinner(f"Summarizing using '{chain_type}' strategy..."):
                summary = summarize_documents(docs, chain_type)

            st.subheader("📊 Document Summary")
            st.markdown(
                f'<div class="summary-box">{summary}</div>',
                unsafe_allow_html=True
            )

            # ===============================
            # N8N WEBHOOK
            # ===============================
            N8N_WEBHOOK_URL = os.environ.get(
                "N8N_SUMMARY_WEBHOOK_URL",
                st.secrets.get("N8N_SUMMARY_WEBHOOK_URL", None)
            )

            if N8N_WEBHOOK_URL:
                try:
                    payload = {
                        "event": "document_summarized",
                        "summary": summary,
                        "chain_type": chain_type,
                        "documents": [f.name for f in uploaded_files],
                        "chunks": len(docs),
                    }

                    requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
                    st.toast("N8N workflow triggered ✅")

                except Exception as e:
                    st.toast(f"N8N error: {e}")

            st.download_button(
                "💾 Download Summary",
                data=summary,
                file_name="financial_summary.txt",
                mime="text/plain"
            )

    else:
        st.warning("⚠️ No readable content found.")

else:
    st.info("👆 Please upload at least one PDF or TXT file.")
