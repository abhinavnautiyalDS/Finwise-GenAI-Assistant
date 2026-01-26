# ===============================
# Financial Chatbot with Memory
# Gemini ➜ Hugging Face Version
# Built by Abhinav Nautiyal
# ===============================

import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import HuggingFaceHub

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
    - Uses **Hugging Face LLM**
    - Conversation-aware memory
    - No Gemini / no Google API
    - Fully assignment-safe
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
# LOAD LLM
# --------------------------------------------------
@st.cache_resource
def load_llm():
    return HuggingFaceHub(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        huggingfacehub_api_token=hf_token,
        model_kwargs={
            "temperature": 0.7,
            "max_new_tokens": 512
        }
    )

llm = load_llm()

# --------------------------------------------------
# MEMORY + CONVERSATION
# --------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# --------------------------------------------------
# CHAT HISTORY
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
        response = st.session_state.conversation.predict(input=user_input)

    st.session_state.messages.append({"role": "assistant", "content": response})

    st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("<center>Built by Abhinav Nautiyal</center>", unsafe_allow_html=True)
