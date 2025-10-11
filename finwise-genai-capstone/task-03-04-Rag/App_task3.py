import os
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from transformers import pipeline # For local LLM fallback
import requests # For N8N webhook

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF Insight Agent (RAG with Memory)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Content (Inspired by Tasks 3 & 4) ---
with st.sidebar:
    st.title("📄 AI-Powered PDF Insights")
    st.markdown("""
    This application allows you to **upload a PDF document** (like financial reports, compliance documents, or product prospectuses) and then **ask intelligent questions** about its content.

    **Key Features:**
    -   **Document Upload:** Upload any text-based PDF.
    -   **RAG Pipeline:** Utilizes a Retrieval-Augmented Generation (RAG) system to find relevant information within your document.
    -   **Semantic Search:** Employs **HuggingFace Embeddings** for deep semantic understanding.
    -   **Vector Store:** Stores document chunks in a **FAISS** index for efficient retrieval.
    -   **Intelligent QA:** Powered by **Gemini 2.0 Flash** (with fallback to local LLM) for generating answers.
    -   **Conversation Memory:** Remembers previous turns in the conversation for contextual responses.
    -   **Multi-Query Retrieval:** Enhances retrieval by generating multiple perspectives on a user's question to capture more nuanced information.
    """)
    st.markdown("---")
    st.info("Ensure `GOOGLE_API_KEY` and `HUGGINGFACE_API_KEY` are set in your `.streamlit/secrets.toml`.")
    st.markdown("---")
    st.image("https://img.freepik.com/free-vector/document-security-concept-illustration_114360-5452.jpg", use_container_width=True) # Example image
    st.markdown("---")
    st.markdown("Built with ❤️ using LangChain, LangGraph, HuggingFace & Streamlit")


# --- API Key Loading ---
@st.cache_resource # Cache API keys so they are loaded only once
def load_api_keys():
    keys = {}
    try:
        keys["HUGGINGFACE_API_KEY"] = st.secrets["HUGGINGFACE_API_KEY"]
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = keys["HUGGINGFACE_API_KEY"]
    except KeyError:
        st.sidebar.warning("⚠️ HuggingFace API Key not found. Local embeddings will be attempted, but API-based embeddings/LLM will fail.")
        keys["HUGGINGFACE_API_KEY"] = None
    except Exception as e:
        st.sidebar.error(f"Error loading Hugging Face API key: {e}")
        keys["HUGGINGFACE_API_KEY"] = None

    try:
        keys["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = keys["GOOGLE_API_KEY"]
    except KeyError:
        st.sidebar.error("❌ Google API Key not found. Gemini LLM will not be available.")
        st.stop() # Stop if Gemini key is critical for primary LLM
    except Exception as e:
        st.sidebar.error(f"Error loading Google API key: {e}")
        st.stop()

    return keys

API_KEYS = load_api_keys()

# --- Embedding Model Initialization ---
@st.cache_resource
def get_embeddings(hf_api_key):
    try:
        # Option 1: Local Inference (Default - No Limits)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        st.sidebar.success("✅ Using local Hugging Face embeddings (sentence-transformers/all-MiniLM-L6-v2).")
        return embeddings
    except Exception as e:
        st.sidebar.warning(f"Error initializing local embeddings: {e}")
        st.sidebar.info("Attempting fallback to Hugging Face Inference API for embeddings...")

        # Option 2: Inference API Fallback (Uses API Key)
        if hf_api_key:
            try:
                embeddings = HuggingFaceEndpoint(
                    repo_id="sentence-transformers/all-MiniLM-L6-v2",
                    task="feature-extraction",
                    huggingfacehub_api_token=hf_api_key
                )
                st.sidebar.success("✅ Using Hugging Face Inference API embeddings (sentence-transformers/all-MiniLM-L6-v2).")
                return embeddings
            except Exception as api_e:
                st.sidebar.error(f"❌ Error initializing Inference API embeddings: {api_e}")
                st.sidebar.error("Embeddings initialization failed. Please check your Hugging Face API key and internet connection.")
                st.stop()
        else:
            st.sidebar.error("❌ Hugging Face API key is missing, and local embeddings failed. Cannot proceed without an embedding model.")
            st.stop()

embeddings = get_embeddings(API_KEYS["HUGGINGFACE_API_KEY"])


# --- LLM Initialization ---
@st.cache_resource
def get_llm(google_api_key, hf_api_key):
    try:
        # Try Gemini with API key
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key, temperature=0.2)
        st.sidebar.success("✅ Initialized Gemini 2.0 Flash with API key.")
        return llm
    except Exception as e:
        st.sidebar.warning(f"Gemini authentication or initialization failed: {e}")
        st.sidebar.info("Attempting fallback to local Hugging Face LLM (flan-t5-small)...")

        # Fallback to local Hugging Face LLM
        try:
            # Note: For conversational chains, pipeline output needs to be wrapped or adapted.
            # This fallback is a simplified illustration. For robust local LLM RAG,
            # you might use a specific LangChain HuggingFacePipeline wrapper.
            local_llm_pipeline = pipeline("text-generation", model="google/flan-t5-small")
            # This is a very basic wrapper to make it act like a LangChain LLM
            class LocalLLMWrapper:
                def __init__(self, pipeline_model):
                    self.pipeline_model = pipeline_model
                def invoke(self, prompt, config=None): # Using invoke to match LangChain interface
                    # For RAG, prompt might be complex, simplify for basic pipeline
                    if isinstance(prompt, list):
                        prompt_text = " ".join([m.content for m in prompt if hasattr(m, 'content')])
                    else:
                        prompt_text = str(prompt)
                    # Use a simple prompt structure for the fallback model
                    response = self.pipeline_model(prompt_text, max_new_tokens=100, num_return_sequences=1)
                    return response[0]['generated_text'] if response else ""
                
                # Add other methods expected by LangChain components if needed, e.g., _call
                def _call(self, prompt: str, stop=None, run_manager=None) -> str:
                     return self.invoke(prompt)

            llm = LocalLLMWrapper(local_llm_pipeline)
            st.sidebar.success("✅ Initialized local Hugging Face LLM (flan-t5-small) as fallback.")
            return llm
        except Exception as local_e:
            st.sidebar.error(f"❌ Error initializing local LLM: {local_e}")
            st.sidebar.error("LLM initialization failed. Check dependencies and internet connection.")
            st.stop()

llm = get_llm(API_KEYS["GOOGLE_API_KEY"], API_KEYS["HUGGINGFACE_API_KEY"])


# --- PDF Processing and RAG Setup ---
@st.cache_resource(hash_funcs={ChatGoogleGenerativeAI: lambda _: None, HuggingFaceEmbeddings: lambda _: None})
def process_pdf_and_setup_rag(uploaded_file_buffer, current_llm, current_embeddings):
    # Temporary save uploaded file
    file_path = "uploaded.pdf"
    with open(file_path, "wb") as f:
        f.write(uploaded_file_buffer.getbuffer())

    # Load documents
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        raise ValueError("No content extracted from PDF. Ensure it's a valid, text-based PDF.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    splits = text_splitter.split_documents(documents)
    if not splits:
        raise ValueError("No document chunks created. Document might be too short or content extraction failed.")

    # Create FAISS vector store
    vectorstore = FAISS.from_documents(splits, current_embeddings)

    # Create basic retriever
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Enhance with MultiQueryRetriever
    multi_retriever = MultiQueryRetriever.from_llm(
        retriever=retriever,
        llm=current_llm,
        include_original=True # Ensures the original query is also used for retrieval
    )

    # Set up conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # Create the conversational retrieval chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=current_llm,
        retriever=multi_retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    return qa_chain

# --- Main App Logic ---
st.title("🚀 AI-Powered PDF Insight Agent")
st.markdown("Ask questions about your uploaded PDF and get intelligent, contextual answers!")

uploaded_file = st.sidebar.file_uploader("Upload your PDF file (e.g., financial prospectus or compliance report)", type="pdf")

qa_chain = None
if uploaded_file is not None:
    st.sidebar.success("PDF uploaded successfully! Processing document...")
    try:
        qa_chain = process_pdf_and_setup_rag(uploaded_file, llm, embeddings)
        st.sidebar.success("✅ RAG pipeline and memory initialized!")
        st.session_state["qa_chain"] = qa_chain # Store in session state
    except Exception as e:
        st.error(f"Error setting up RAG pipeline: {e}")
        st.warning("Please check your PDF file and ensure it is text-based and contains extractable content.")
        qa_chain = None # Reset qa_chain if setup fails

# --- Chat Interface ---
if "qa_chain" in st.session_state and st.session_state["qa_chain"] is not None:
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for entry in st.session_state.chat_history:
        st.chat_message("user").markdown(entry["question"])
        st.chat_message("assistant").markdown(entry["answer"])
        if entry["sources"]:
            with st.expander(f"Sources for: '{entry['question'][:50]}...'"):
                for s in entry["sources"]:
                    st.write(s)

    # Input for new question
    question = st.chat_input("Enter your question here (e.g., 'What are the key risks mentioned in the report?')")
    if question:
        st.chat_message("user").markdown(question)
        
        # Add N8N Workflow Trigger (Placeholder)
        N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "YOUR_N8N_WEBHOOK_URL_HERE") # Get from env or set default
        
        if N8N_WEBHOOK_URL and N8N_WEBHOOK_URL != "YOUR_N8N_WEBHOOK_URL_HERE":
            try:
                # Trigger N8N workflow
                n8n_payload = {
                    "event": "user_question",
                    "question": question,
                    "timestamp": st.session_state.get("last_query_time", "N/A")
                }
                response = requests.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=5)
                if response.status_code == 200:
                    st.toast("N8N workflow triggered successfully!", icon="✅")
                else:
                    st.toast(f"N8N workflow trigger failed: {response.status_code}", icon="⚠️")
            except requests.exceptions.RequestException as e:
                st.toast(f"N8N request error: {e}", icon="⚠️")
            except Exception as e:
                st.toast(f"Unexpected N8N error: {e}", icon="⚠️")
        else:
            st.toast("N8N webhook URL not configured.", icon="ℹ️")


        with st.spinner("Searching and generating answer..."):
            try:
                # Invoke the QA chain
                result = st.session_state["qa_chain"].invoke({"question": question})
                response_text = result["answer"]
                
                # Extract source documents and format them
                sources = []
                if "source_documents" in result and result["source_documents"]:
                    sources = [
                        {
                            "page": doc.metadata.get("page", "N/A"),
                            "source": doc.metadata.get("source", "N/A"),
                            "content_preview": doc.page_content[:150] + "..."
                        }
                        for doc in result["source_documents"]
                    ]

                # Store history with question, answer, and processed sources
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": response_text,
                    "sources": sources
                })
                
                # Display the assistant's response
                st.chat_message("assistant").markdown(response_text)
                if sources:
                    with st.expander("Show Sources"):
                        for i, s in enumerate(sources):
                            st.markdown(f"**Source {i+1}:** Page {s['page']} (File: {s['source']})")
                            st.code(s['content_preview'], language="text")

            except Exception as e:
                st.chat_message("assistant").error(f"Error processing question: {e}")
                st.warning("Check API quotas, document content, or try a different question.")
else:
    st.info("Please upload a PDF file in the sidebar to start asking questions.")
