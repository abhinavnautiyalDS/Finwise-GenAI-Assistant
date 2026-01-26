import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers import MultiQueryRetriever              # ← yeh sahi import hai
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from transformers import pipeline
import requests

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF Insight Agent (RAG + Memory)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📄 PDF Insight Agent")
    st.markdown("""
    Upload karo PDF (financial report, prospectus, compliance docs etc.)  
    aur intelligent sawaal poochho.
    
    **Features:**
    - HuggingFace embeddings
    - FAISS vector store
    - Multi-query retrieval
    - Conversational memory
    - Primary LLM → Gemini 2.0 Flash
    - Fallback → local flan-t5-small
    """)
    st.info("secrets.toml mein `GOOGLE_API_KEY` aur optional `HUGGINGFACE_API_KEY` daalo")
    st.markdown("---")
    st.caption("Abhinav Nautiyal • Jan 2026")

# ── API Keys ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_api_keys():
    keys = {}
    try:
        keys["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = keys["GOOGLE_API_KEY"]
    except KeyError:
        st.error("GOOGLE_API_KEY nahi mila. Gemini nahi chalega.")
        st.stop()

    keys["HUGGINGFACE_API_KEY"] = st.secrets.get("HUGGINGFACE_API_KEY")
    if keys.get("HUGGINGFACE_API_KEY"):
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = keys["HUGGINGFACE_API_KEY"]

    return keys

API_KEYS = load_api_keys()

# ── Embeddings ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_embeddings(hf_key):
    try:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        st.warning(f"Local embeddings fail: {e}")
        if hf_key:
            try:
                return HuggingFaceEndpoint(
                    repo_id="sentence-transformers/all-MiniLM-L6-v2",
                    task="feature-extraction",
                    huggingfacehub_api_token=hf_key
                )
            except Exception as api_e:
                st.error(f"HF Inference API bhi fail: {api_e}")
        st.error("Embeddings nahi ban pa rahe. App ruk gaya.")
        st.stop()

embeddings = get_embeddings(API_KEYS.get("HUGGINGFACE_API_KEY"))

# ── LLM ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm(google_key, hf_key):
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_key,
            temperature=0.2
        )
    except Exception as e:
        st.warning(f"Gemini fail: {e}. Local fallback use kar raha hoon.")
        try:
            pipe = pipeline("text-generation", model="google/flan-t5-small")

            class SimpleWrapper:
                def invoke(self, input, **kwargs):
                    if isinstance(input, list):
                        text = " ".join([m.content for m in input if hasattr(m, 'content')])
                    else:
                        text = str(input)
                    res = pipe(text, max_new_tokens=150, num_return_sequences=1)
                    return res[0]["generated_text"] if res else "No response"

            return SimpleWrapper()
        except Exception as le:
            st.error(f"Local LLM bhi fail: {le}")
            st.stop()

llm = get_llm(API_KEYS["GOOGLE_API_KEY"], API_KEYS.get("HUGGINGFACE_API_KEY"))

# ── RAG Pipeline ─────────────────────────────────────────────────────────────
@st.cache_resource
def build_rag_pipeline(uploaded_file, current_llm, current_embeddings):
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    if not docs:
        raise ValueError("PDF se text nahi mila")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(chunks, current_embeddings)
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    multi_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=current_llm,
        include_original_query=True
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=current_llm,
        retriever=multi_retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )

    return chain

# ── UI ───────────────────────────────────────────────────────────────────────
st.title("🚀 PDF Insight Agent – Document ke baare mein poochho")

uploaded_file = st.sidebar.file_uploader("PDF upload karo", type="pdf")

if uploaded_file:
    # Naya file upload hone par history reset
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        st.session_state.chat_history = []
        st.session_state.qa_chain = None
        st.session_state.last_uploaded = uploaded_file.name

    if "qa_chain" not in st.session_state or st.session_state.qa_chain is None:
        with st.spinner("PDF process ho raha hai, vector index ban raha hai..."):
            try:
                st.session_state.qa_chain = build_rag_pipeline(uploaded_file, llm, embeddings)
                st.sidebar.success("PDF ready hai!")
            except Exception as e:
                st.error(f"PDF process fail: {e}")
                st.session_state.qa_chain = None

if "qa_chain" in st.session_state and st.session_state.qa_chain:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for src in msg["sources"]:
                        st.markdown(f"**Page {src['page']}**  \n{src['preview']}")

    if question := st.chat_input("Document ke baare mein sawaal poochho..."):
        st.chat_message("user").markdown(question)
        st.session_state.chat_history.append({"role": "user", "content": question})

        with st.spinner("Jawaab dhoondh raha hoon..."):
            try:
                result = st.session_state.qa_chain.invoke({"question": question})
                answer = result["answer"]
                sources = [
                    {"page": doc.metadata.get("page", "?"), "preview": doc.page_content[:200] + "..."}
                    for doc in result.get("source_documents", [])
                ]

                st.chat_message("assistant").markdown(answer)
                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            st.markdown(f"**Page {s['page']}**  \n{s['preview']}")

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            except Exception as e:
                st.chat_message("assistant").error(f"Error: {str(e)}")
else:
    st.info("Sidebar se PDF upload karo tab sawaal poochh sakte ho.")
