pip install to-requirements.txt

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
from transformers import pipeline

# Set up Hugging Face API key (optional for local, required for Inference API)
try:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.secrets["HUGGINGFACE_API_KEY"]
except Exception as e:
    st.error(f"Error retrieving Hugging Face API key: {e}")
    st.warning("Please set 'HUGGINGFACE_API_KEY' in Streamlit Secrets (optional for local use).")
    raise

# Option 1: Local Inference (Default - No Limits)
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    st.success("Using local Hugging Face embeddings (sentence-transformers/all-MiniLM-L6-v2).")
except Exception as e:
    st.error(f"Error initializing local embeddings: {e}")
    st.warning("Falling back to Hugging Face Inference API...")

    # Option 2: Inference API Fallback (Uses API Key)
    try:
        embeddings = HuggingFaceEndpoint(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
            huggingfacehub_api_token=st.secrets["HUGGINGFACE_API_KEY"]
        )
        st.success("Using Hugging Face Inference API embeddings (sentence-transformers/all-MiniLM-L6-v2).")
    except Exception as e:
        st.error(f"Error initializing Inference API embeddings: {e}")
        st.warning("Check your API key, internet connection, or use a local model.")
        raise

# Initialize LLM with fallback to local model
try:
    # Try Gemini with API key
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
    st.success("Initialized Gemini 2.0 Flash with API key.")
except Exception as e:
    st.error(f"Gemini authentication failed: {e}")
    st.warning("Falling back to local Hugging Face LLM...")

    # Fallback to local Hugging Face LLM
    try:
        llm = pipeline("text-generation", model="google/flan-t5-small")
        st.success("Initialized local Hugging Face LLM (flan-t5-small) as fallback.")
    except Exception as local_e:
        st.error(f"Error initializing local LLM: {local_e}")
        st.warning("LLM initialization failed. Check dependencies and internet connection.")
        raise

# Upload PDF file
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Upload your PDF file (e.g., financial prospectus or compliance report)", type="pdf")
if uploaded_file is not None:
    try:
        with open("uploaded.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        loader = PyPDFLoader("uploaded.pdf")
        documents = loader.load()
        if not documents:
            raise ValueError("No content extracted from PDF")
        st.sidebar.success("PDF uploaded and loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading PDF: {e}")
        st.sidebar.warning("Ensure the uploaded file is a valid, text-based PDF (not scanned images).")
        raise

    # Split documents into chunks
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        if not splits:
            raise ValueError("No document chunks created")
        st.sidebar.success("Document chunks created successfully.")
    except Exception as e:
        st.sidebar.error(f"Error splitting documents: {e}")
        raise

    # Create FAISS vector store
    try:
        vectorstore = FAISS.from_documents(splits, embeddings)
        st.sidebar.success("FAISS vector store created successfully.")
    except Exception as e:
        st.sidebar.error(f"Error creating FAISS vector store: {e}")
        st.sidebar.warning("Check if embeddings were generated correctly.")
        raise

    # Create basic retriever
    try:
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        st.sidebar.success("Retriever set up successfully.")
    except Exception as e:
        st.sidebar.error(f"Error setting up retriever: {e}")
        raise

    # Enhance with MultiQueryRetriever for multi-step retrieval
    try:
        multi_retriever = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=llm,
            include_original=True
        )
        st.sidebar.success("MultiQueryRetriever set up successfully.")
    except Exception as e:
        st.sidebar.error(f"Error setting up MultiQueryRetriever: {e}")
        raise

    # Set up conversation memory
    try:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        st.sidebar.success("Conversation memory initialized.")
    except Exception as e:
        st.sidebar.error(f"Error setting up memory: {e}")
        raise

    # Create the conversational retrieval chain
    try:
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=multi_retriever,
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        st.sidebar.success("Conversational retrieval chain created.")
    except Exception as e:
        st.sidebar.error(f"Error creating ConversationalRetrievalChain: {e}")
        raise

# Streamlit app layout
st.title("AI-Powered PDF Insights")
st.markdown("Ask questions about your uploaded PDF and get intelligent answers!")

# Chat interface
if "qa_chain" in locals() and uploaded_file is not None:
    st.session_state.setdefault("chat_history", [])
    
    # Display chat history
    for question, response, sources in st.session_state.chat_history:
        st.markdown(f"**Question:** {question}")
        st.markdown(f"**Answer:** {response}")
        if sources:
            st.markdown(f"**Sources:** {', '.join(str(s) for s in sources)}")

    # Input for new question
    question = st.text_input("Enter your question here (e.g., 'What are the key risks?')", key="question_input")
    if st.button("Submit", key="submit_button"):
        if question:
            try:
                result = qa_chain.invoke({"question": question})
                response = result["answer"]
                sources = [doc.metadata for doc in result["source_documents"]]
                st.session_state.chat_history.append((question, response, sources))
                
                st.markdown(f"**Question:** {question}")
                st.markdown(f"**Answer:** {response}")
                if sources:
                    st.markdown(f"**Sources:** {', '.join(str(s) for s in sources)}")
            except Exception as e:
                st.error(f"Error processing question: {e}")
                st.warning("Check API quotas, document content, or try a different question.")
else:
    st.info("Please upload a PDF file in the sidebar to start asking questions.")
