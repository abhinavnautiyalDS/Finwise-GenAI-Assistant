# ===============================
# Financial Chatbot with Memory
# Hugging Face – FIXED with ChatHuggingFace wrapper (Jan 2026)
# Built by Abhinav Nautiyal
# ===============================
import streamlit as st
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Financial Chatbot with Memory",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; color: #e0e0e0; }
    h1 { color: #3498db; text-align: center; padding: 20px 0; }
    div[data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("💰 Financial Chatbot with Memory (Hugging Face)")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("About This Chatbot")
    st.markdown("""
    - Uses **Hugging Face Inference API** (free tier)  
    - Maintains conversation memory  
    - Powered by Mistral-7B-Instruct-v0.3 + ChatHuggingFace wrapper  
    - Built for financial Q&A  
    """)

# --------------------------------------------------
# LOAD HUGGING FACE TOKEN
# --------------------------------------------------
try:
    hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
except KeyError:
    st.error("Hugging Face API token not found. Please add it to your secrets.toml file.")
    st.stop()

# --------------------------------------------------
# LOAD LLM with ChatHuggingFace wrapper (fixes conversational/task mismatch)
# --------------------------------------------------
@st.cache_resource
def load_llm():
    endpoint = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        huggingfacehub_api_token=hf_token,
        temperature=0.7,
        max_new_tokens=512,
        streaming=False,                # Important for stable full responses
    )
    
    # This wrapper uses the correct "conversational" endpoint internally
    return ChatHuggingFace(llm=endpoint)

llm = load_llm()

# --------------------------------------------------
# PROMPT TEMPLATE
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful, accurate and professional financial assistant. Answer clearly, concisely and factually. If unsure, say so."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ]
)

chain = prompt | llm

# --------------------------------------------------
# MEMORY STORE
# --------------------------------------------------
if "store" not in st.session_state:
    st.session_state.store = {}

def get_session_history(session_id: str):
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = InMemoryChatMessageHistory()
    return st.session_state.store[session_id]

conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# --------------------------------------------------
# CHAT HISTORY UI
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------------------------------------
# USER INPUT + PROCESSING
# --------------------------------------------------
user_input = st.chat_input("Ask your financial question...")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Truncate history to avoid token limits & timeouts (critical on free tier)
    MAX_TURNS = 10  # Keep roughly last 5 full exchanges
    if len(st.session_state.messages) > MAX_TURNS * 2:
        st.session_state.messages = st.session_state.messages[-MAX_TURNS * 2 :]

    with st.spinner("Thinking..."):
        try:
            response = conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "user_1"}}
            )
            reply = response.content.strip()
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                reply = "⚠️ Rate limit reached on free Hugging Face tier. Please wait 1–2 minutes and try again."
            elif "token" in error_str or "auth" in error_str:
                reply = "⚠️ Authentication issue with Hugging Face. Check your API token."
            elif "not supported" in error_str or "conversational" in error_str:
                reply = "⚠️ Model endpoint issue detected. The app is using the correct wrapper — try refreshing or wait a minute."
            else:
                reply = f"⚠️ Sorry, something went wrong: {str(e)}\n\nPlease try a simpler question or wait a moment."

    # Display assistant response
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    "<center style='color: #888; margin-top: 40px;'>"
    "Built by Abhinav Nautiyal | Powered by Mistral-7B-Instruct via Hugging Face"
    "</center>",
    unsafe_allow_html=True
)
