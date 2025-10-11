

# import streamlit as st
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationBufferMemory

# # Page configuration
# st.set_page_config(
#     page_title="Financial Chatbot with Memory",
#     page_icon="💰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for enhanced styling
# st.markdown("""
#     <style>
#     /* Overall app styling */
#     .stApp {
#         background-color: #f0f4f8;
#         color: #333333;
#     }
    
#     /* Header styling */
#     h1 {
#         color: #2c3e50;
#         text-align: center;
#         font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         padding: 20px 0;
#         border-bottom: 2px solid #3498db;
#     }
    
#     /* Chat message bubbles */
#     .st-chat-message {
#         border-radius: 15px;
#         padding: 10px 15px;
#         margin-bottom: 10px;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.1);
#     }
    
#     /* User messages */
#     div[data-testid="chatMessage"]:nth-child(odd) {
#         background-color: #e8f6ff;
#         border: 1px solid #3498db;
#     }
    
#     /* Bot messages */
#     div[data-testid="chatMessage"]:nth-child(even) {
#         background-color: #ffffff;
#         border: 1px solid #bdc3c7;
#     }
    
#     /* Input box */
#     .stTextInput > div > div > input {
#         border-radius: 20px;
#         border: 1px solid #3498db;
#         padding: 10px;
#         font-size: 16px;
#     }
    
#     /* Button styling */
#     .stButton > button {
#         background-color: #3498db;
#         color: white;
#         border-radius: 20px;
#         border: none;
#         padding: 10px 20px;
#         font-weight: bold;
#         transition: background-color 0.3s;
#     }
#     .stButton > button:hover {
#         background-color: #2980b9;
#     }
    
#     /* Sidebar styling */
#     .css-1lcbmhc {
#         background-color: #ffffff;
#         border-right: 1px solid #e0e0e0;
#         padding: 20px;
#     }
    
#     /* Footer */
#     .footer {
#         text-align: center;
#         font-size: 12px;
#         color: #7f8c8d;
#         padding: 10px 0;
#         border-top: 1px solid #e0e0e0;
#         margin-top: 20px;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Title
# st.title("💰 Financial Chatbot with Memory")

# # Sidebar for additional info
# with st.sidebar:
#     st.header("About This Chatbot")
#     st.markdown("""
#     This chatbot helps with **financial planning** and **asset allocation** advice.
#     - Powered by Gemini-2.0-flash via LangChain.
#     - Remembers conversation history for context-aware responses.
#     - Ask about budgets, investments, retirement, and more!
#     """)
#     st.image("https://img.freepik.com/free-vector/financial-management-concept-illustration_114360-7131.jpg", use_column_width=True)
#     st.markdown("---")

# # Get API key from Streamlit secrets (set in Streamlit Cloud)
# api_key = st.secrets['GOOGLE_API_KEY']

# # Initialize the Gemini chat model
# @st.cache_resource
# def load_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         google_api_key=api_key,
#         temperature=0.7
#     )

# llm = load_llm()

# # Set up conversation memory and chain
# if "memory" not in st.session_state:
#     st.session_state.memory = ConversationBufferMemory()

# if "conversation" not in st.session_state:
#     st.session_state.conversation = ConversationChain(
#         llm=llm,
#         memory=st.session_state.memory,
#         verbose=False
#     )

# # Chat history container
# chat_container = st.container()

# # Display chat history
# with chat_container:
#     if "messages" not in st.session_state:
#         st.session_state.messages = []

#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# # User input at the bottom
# user_input = st.chat_input("Type your financial question here...")

# if user_input:
#     # Append user message
#     st.session_state.messages.append({"role": "user", "content": user_input})
    
#     # Get response
#     with st.spinner("Thinking..."):
#         response = st.session_state.conversation.predict(input=user_input)
    
#     # Append bot message
#     st.session_state.messages.append({"role": "assistant", "content": response})
    
#     # Rerun to update the chat container
#     st.rerun()

# # Footer
# st.markdown('<div class="footer">Built with ❤️ by Grok | Powered by xAI</div>', unsafe_allow_html=True)






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

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* Overall app styling */
    .stApp {
        background-color: #f0f4f8;
        color: #333333;
    }
   
    /* Header styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 20px 0;
        border-bottom: 2px solid #3498db;
    }
   
    /* Chat message bubbles */
    .st-chat-message {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
   
    /* User messages */
    div[data-testid="chatMessage"]:nth-child(odd) {
        background-color: #ffffff;
        border: 1px solid #3498db;
        color: #000000; /* Ensure user text is readable */
    }
   
    /* Bot messages */
    div[data-testid="chatMessage"]:nth-child(even) {
        background-color: #ffffff; /* white background for bot messages */
        border: 1px solid #bdc3c7;
        color: #000000; /* black text for contrast */
    }
   
    /* Input box */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 1px solid #3498db;
        padding: 10px;
        font-size: 16px;
    }
   
    /* Button styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #000000;
    }
   
    /* Sidebar styling */
    .css-1lcbmhc {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
        padding: 20px;
    }
   
    /* Footer */
    .footer {
        text-align: center;
        font-size: 12px;
        color: #7f8c8d;
        padding: 10px 0;
        border-top: 1px solid #e0e0e0;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("💰 Financial Chatbot with Memory")

# Sidebar for additional info
with st.sidebar:
    st.header("About This Chatbot")
    st.markdown("""
    This chatbot helps with **financial planning** and **asset allocation** advice.
    - Powered by Gemini-2.0-flash via LangChain.
    - Remembers conversation history for context-aware responses.
    - Ask about budgets, investments, retirement, and more!
    """)
    st.image("https://img.freepik.com/free-vector/financial-management-concept-illustration_114360-7131.jpg", use_column_width=True)
    st.markdown("---")

# Get API key from Streamlit secrets (set in Streamlit Cloud)
api_key = st.secrets['GOOGLE_API_KEY']

# Initialize the Gemini chat model
@st.cache_resource
def load_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",  # Corrected to Pro model as per task requirement
        google_api_key=api_key,
        temperature=0.7
    )

llm = load_llm()

# Set up conversation memory and chain
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=False
    )

# Chat history container
chat_container = st.container()

# Display chat history
with chat_container:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input at the bottom
user_input = st.chat_input("Type your financial question here...")

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
   
    # Get response
    with st.spinner("Thinking..."):
        response = st.session_state.conversation.predict(input=user_input)
   
    # Append bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
   
    # Rerun to update the chat container
    st.rerun()

# Footer
st.markdown('<div class="footer">Built by Abhinav Nautiyal</div>', unsafe_allow_html=True)
