import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Page configuration
st.set_page_config(
    page_title="Financial Chatbot with Memory",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling and visibility
st.markdown("""
    <style>
    /* Overall App Styling */
    .stApp {
        background-color: #eef2f5;
        color: #222222;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Header Styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: 700;
        padding: 15px 0;
        border-bottom: 3px solid #3498db;
    }

    /* Chat Message Styling */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        line-height: 1.5;
    }

    /* User Message (Right side) */
    div[data-testid="stChatMessage"][data-testid="user"] {
        background-color: #e8f6ff;
        border: 1px solid #3498db;
        color: #1a1a1a;
    }

    /* Bot Message (Left side) */
    div[data-testid="stChatMessage"][data-testid="assistant"] {
        background-color: #1e1e1e;
        border: 1px solid #444;
        color: #ffffff;
    }

    /* Input box */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 1px solid #3498db;
        padding: 10px;
        font-size: 16px;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2980b9;
        transform: scale(1.03);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
        padding: 20px;
    }

    /* Footer */
    .footer {
        text-align: center;
        font-size: 13px;
        color: #7f8c8d;
        padding: 12px 0;
        border-top: 1px solid #dcdcdc;
        margin-top: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("💰 Financial Chatbot with Memory")

# Sidebar for info
with st.sidebar:
    st.header("About This Chatbot")
    st.markdown("""
    This chatbot assists with **financial planning** and **investment advice**.  
    - Powered by **Gemini-2.5-Pro** via LangChain  
    - Maintains context using **memory**  
    - Ask about **budgets, loans, savings, and investments**  
    """)
    st.image("https://img.freepik.com/free-vector/financial-management-concept-illustration_114360-7131.jpg", use_column_width=True)
    st.markdown("---")

# Load API Key
api_key = st.secrets["GOOGLE_API_KEY"]

# Load LLM
@st.cache_resource
def load_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key,
        temperature=0.7
    )

llm = load_llm()

# Initialize memory and conversation chain
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# Display chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your financial question here...")

if user_input:
    # Store user input
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    with st.spinner("Thinking..."):
        response = st.session_state.conversation.predict(input=user_input)

    # Store bot response
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Rerun app to refresh chat
    st.rerun()

# Footer
st.markdown('<div class="footer">Built with ❤️ by Abhinav Nautiyal</div>', unsafe_allow_html=True)
