# ===============================
# Financial Chatbot with Memory
# Hugging Face (LATEST – FIXED)
# Built by Abhinav Nautiyal
# ===============================

import streamlit as st

from langchain_huggingface import HuggingFaceEndpoint
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
div[data-testid="chatMessage"] {
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
    - Uses **Hugging Face Inference API**
    - Memory-based conversation
    - LangChain latest architecture
    - Assignment ready
    """)

# --------------------------------------------------
# LOAD HUGGING FACE TOKEN
# --------------------------------------------------
try:
    hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
except KeyError:
    st.error("Hugging Face token not found. Add it in secrets.toml")
    st.stop()

# --------------------------------------------------
# LOAD LLM (CORRECT WAY)
# --------------------------------------------------

@st.cache_resource
def load_llm():
    return HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.2-3B-Instruct",
        huggingfacehub_api_token=hf_token,
        temperature=0.7,
        max_new_tokens=512,
        # Important additions for stability & chat behavior on free tier
        streaming=False,                    # Avoids common streaming bugs / partial responses
        task="conversational"        # Usually auto-detected, but safe to include
    )
llm = load_llm()



# --------------------------------------------------
# PROMPT TEMPLATE
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful financial assistant."),
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
# USER INPUT
# --------------------------------------------------
user_input = st.chat_input("Ask your financial question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = conversation.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "user_1"}}
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response.content
    })

    st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("<center>Built by Abhinav Nautiyal</center>", unsafe_allow_html=True)
