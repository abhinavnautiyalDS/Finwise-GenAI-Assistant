import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_experimental.utilities.python import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun
import math
import requests
import json
import warnings

# Ignore warnings
warnings.filterwarnings('ignore')

# Get API keys from Colab secrets
google_api_key = st.secrets('GOOGLE_API_KEY')
alpha_vantage_key = st.secrets('ALPHA_VANTAGE_KEY', None)  # Optional for stock tool

def load_api_key():
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key

        alpha_vantage_key = st.secrets('ALPHA_VANTAGE_KEY')
        os.environ["GOOGLE_API_KEY"] = alpha_vantage_key
        
        st.success("✅  API Key loaded successfully.")
    except KeyError:
        st.error("❌  API Key not found. Please add it to `.streamlit/secrets.toml`.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading API key: {e}")
        st.stop()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=google_api_key,
    temperature=0.1
)

# Define Tools
@tool(return_direct=False)
def calculator(expression: str) -> str:
    """Perform mathematical calculations or EMI. Input: 
    - 'EMI(P, r, n)' for loan EMI where P=principal, r=annual rate/12 (e.g., 0.09 for 9%), n=months.
    - Simple expressions like '2 + 2'.
    Returns result or error message."""
    try:
        if expression.startswith("EMI("):
            args = expression[4:-1].split(",")
            P = float(args[0].strip())
            r_annual = float(args[1].strip())
            r = r_annual / 12
            n = int(args[2].strip())
            emi = P * r * (math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
            return f"Monthly EMI: ₹{emi:.2f}"
        else:
            return str(eval(expression))
    except Exception as e:
        return f"Error in calculation: {str(e)}"

@tool(return_direct=False)
def python_repl(code: str) -> str:
    """Run Python code for complex calculations. Input: valid Python code string."""
    try:
        repl = PythonREPL()
        result = repl.run(code)
        return str(result).strip()
    except Exception as e:
        return f"REPL error: {str(e)}"

@tool(return_direct=False)
def stock_price(symbol: str) -> str:
    """Get current stock price for a symbol (e.g., AAPL). Returns price or error."""
    if not alpha_vantage_key:
        return "Alpha Vantage API key not set. Simulated price: $150.00 for AAPL."
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={alpha_vantage_key}"
    try:
        response = requests.get(url)
        data = response.json()
        price = float(data['Global Quote']['05. price'])
        return f"Current price for {symbol}: ${price:.2f}"
    except Exception as e:
        return f"Error fetching {symbol} data: {str(e)}"

@tool(return_direct=False)
def web_search(query: str) -> str:
    """Search the web for general information. Input: search query."""
    try:
        from ddgs import DuckDuckGoSearch  # Using ddgs for better search
        search = DuckDuckGoSearch()
        results = search.text(query, max_results=3)
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Search error: {str(e)}"

# List of tools
tools = [calculator, python_repl, stock_price, web_search]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# System Prompt
system_prompt = """You are a precise financial assistant. ALWAYS use tools for calculations and data fetching. Think step-by-step: 1. Identify the tool needed. 2. Call the tool with exact input. 3. Use the observation to form the answer.
- For EMI: Call 'calculator' with 'EMI(2000000, 0.09, 60)' (r=annual rate 0.09, n=months 60).
- For compound interest: Call 'python_repl' with code 'P = 10000; r = 0.07; t = 10; amount = P * (1 + r)**t; print(f"Interest: {amount - P:.2f}")'.
- For stock prices: Call 'stock_price' with symbol 'AAPL'.
- For general info: Call 'web_search' with query.
Reference prior observations in multi-step queries. End with clear final answer."""

# Create ReAct Agent
agent = create_react_agent(
    llm_with_tools,
    tools,
    messages_modifier=system_prompt
)

# Streamlit App
st.title("Build an Autonomous Agent for Data Fetching and Calculations")
st.write("This app creates an autonomous agent that uses external tools to fetch or calculate data (e.g., interest, stock prices, or general info).")

# Session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("Enter your query (e.g., EMI, stock price, compound interest):"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Invoke agent
    response = agent.invoke({"messages": [("human", prompt)]})
    final_response = response["messages"][-1].content

    # Append and display agent response
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)

    # Display tool calls (if any)
    with st.expander("Tool Calls"):
        for msg in response["messages"]:
            if msg.type == "tool":
                st.write(f"Tool: {msg.name} - {msg.content}")
