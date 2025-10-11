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
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage # Import message types

# Ignore warnings
warnings.filterwarnings('ignore')

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Agentic Financial Assistant (LangGraph)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Information ---
with st.sidebar:
    st.title("🤖 About This Agent")
    st.markdown("""
    This is an **Autonomous AI Agent** designed to assist with financial calculations and data fetching.
    It uses **LangGraph** for advanced agentic orchestration and **Gemini 2.5 Pro** as its brain.

    **Capabilities:**
    - **Calculations:** Perform complex math, including EMI and compound interest, using a `calculator` or `python_repl` tool.
    - **Stock Data:** Fetch real-time stock prices (requires Alpha Vantage API key).
    - **Web Search:** Find general information using `DuckDuckGoSearch`.

    **How it Works (ReAct Agent):**
    The agent employs a **Reasoning and Acting (ReAct)** approach, thinking step-by-step to:
    1.  **Observe** your query.
    2.  **Reason** which tool is best suited for the task.
    3.  **Act** by calling the selected tool with precise inputs.
    4.  **Observe** the tool's output.
    5.  **Formulate** a comprehensive answer based on observations.

    **Example Queries:**
    - "What is the monthly EMI for a 20 lakh loan over 5 years at 9% annual interest?"
    - "Calculate the future value of an investment of $10,000 at 7% interest compounded annually for 10 years."
    - "What is the current stock price of TSLA?"
    - "Tell me about the latest trends in renewable energy investments."
    """)
    st.markdown("---")
    st.info("Ensure `GOOGLE_API_KEY` and optionally `ALPHA_VANTAGE_KEY` are set in your `.streamlit/secrets.toml` file.")
    st.markdown("---")
    st.markdown("Built with ❤️ using LangChain & LangGraph")

# --- API Key Loading ---
@st.cache_resource # Cache API keys so they are loaded only once
def load_api_keys():
    try:
        # Load Google API Key
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key # Set as environment variable for LangChain

        # Load Alpha Vantage Key (optional)
        alpha_vantage_key = st.secrets.get('ALPHA_VANTAGE_KEY') # Use .get() for optional keys
        if alpha_vantage_key:
            os.environ["ALPHA_VANTAGE_KEY"] = alpha_vantage_key # Set as environment variable
            st.sidebar.success("✅ API Keys loaded successfully (Google & Alpha Vantage).")
        else:
            st.sidebar.warning("⚠️ Alpha Vantage API Key not found. Stock price tool will use simulated data.")
            os.environ["ALPHA_VANTAGE_KEY"] = "" # Ensure it's an empty string if not found
        
        return google_api_key, alpha_vantage_key
    except KeyError as e:
        st.sidebar.error(f"❌ Required API Key not found: {e}. Please add it to `.streamlit/secrets.toml`.")
        st.stop() # Stop the app if a critical key is missing
    except Exception as e:
        st.sidebar.error(f"Error loading API key: {e}")
        st.stop()

GOOGLE_API_KEY, ALPHA_VANTAGE_KEY = load_api_keys()

# --- Initialize Gemini LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY, # Pass the loaded key directly
    temperature=0.1
)

# --- Define Tools ---
@tool(return_direct=False)
def calculator(expression: str) -> str:
    """Perform mathematical calculations or EMI. Input:
    - 'EMI(P, r, n)' for loan EMI where P=principal, r=annual interest rate (e.g., 0.09 for 9%), n=number of months.
    - Simple arithmetic expressions like '2 + 2'.
    Returns result or error message."""
    try:
        if expression.startswith("EMI("):
            args = expression[4:-1].split(",")
            if len(args) != 3:
                return "Error: EMI function requires 3 arguments: principal, annual_rate, months."
            P = float(args[0].strip())
            r_annual = float(args[1].strip())
            n = int(args[2].strip())
            
            if r_annual <= 0 or n <= 0:
                return "Error: Annual rate and number of months must be positive for EMI calculation."

            r_monthly = r_annual / 12
            
            # EMI Formula: P * r * (1 + r)^n / ((1 + r)^n - 1)
            # Handle the case where r_monthly is effectively 0 (very low interest rate)
            if r_monthly == 0:
                emi = P / n # Simple division for 0 interest
            else:
                emi = P * r_monthly * (math.pow(1 + r_monthly, n)) / (math.pow(1 + r_monthly, n) - 1)
            return f"Monthly EMI: ₹{emi:.2f}"
        else:
            # Evaluate simple expressions
            return str(eval(expression))
    except Exception as e:
        return f"Error in calculation: {str(e)}"

@tool(return_direct=False)
def python_repl(code: str) -> str:
    """Run Python code for complex calculations, data manipulation, or logical operations.
    Input: A valid Python code string.
    Example for compound interest: `P = 10000; r = 0.07; t = 10; amount = P * (1 + r)**t; print(f'Future Value: {amount:.2f}')`
    """
    try:
        repl = PythonREPL()
        result = repl.run(code)
        return str(result).strip()
    except Exception as e:
        return f"REPL error: {str(e)}"

@tool(return_direct=False)
def stock_price(symbol: str) -> str:
    """Get current stock price for a given stock ticker symbol (e.g., AAPL, GOOGL).
    Returns the current price or an error message."""
    if not ALPHA_VANTAGE_KEY:
        return f"Alpha Vantage API key not set. Returning simulated price for {symbol}: $150.00."
    
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        
        if "Global Quote" in data:
            price = float(data['Global Quote']['05. price'])
            return f"Current price for {symbol}: ${price:.2f}"
        elif "Error Message" in data:
            return f"Error fetching {symbol} data from Alpha Vantage: {data['Error Message']}"
        else:
            return f"Could not retrieve stock price for {symbol}. Raw response: {json.dumps(data)}"
    except requests.exceptions.RequestException as e:
        return f"Network error fetching {symbol} data: {str(e)}"
    except ValueError as e:
        return f"Data parsing error for {symbol}: {str(e)}. Response might not be valid JSON."
    except Exception as e:
        return f"An unexpected error occurred while fetching {symbol} data: {str(e)}"

@tool(return_direct=False)
def web_search(query: str) -> str:
    """Search the web for general information, news, or explanations.
    Input: A search query string."""
    try:
        search = DuckDuckGoSearchRun() # Corrected instantiation
        results = search.run(query) # DuckDuckGoSearchRun has a .run() method
        return results # Returns a string of search results
    except Exception as e:
        return f"Search error: {str(e)}"

# List of tools
tools = [calculator, python_repl, stock_price, web_search]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# --- System Prompt ---
SYSTEM_PROMPT = """You are a highly capable and precise AI financial assistant. ALWAYS use the provided tools for calculations and data fetching when appropriate. Your workflow should be step-by-step:
1.  **Analyze the User's Query:** Understand the core request.
2.  **Identify Required Tools:** Determine which tool(s) are best suited for the task (e.g., calculator for EMI, python_repl for complex math, stock_price for market data, web_search for general info).
3.  **Formulate Tool Calls:** Construct the exact input for the chosen tool.
    -   For **EMI**: Call `calculator` with `EMI(PRINCIPAL, ANNUAL_RATE_DECIMAL, MONTHS)` (e.g., `EMI(2000000, 0.09, 60)`).
    -   For **Compound Interest/Complex Math**: Call `python_repl` with Python code (e.g., `P = 10000; r = 0.07; t = 10; amount = P * (1 + r)**t; print(f"Future Value: {amount:.2f}")`).
    -   For **Stock Prices**: Call `stock_price` with the ticker symbol (e.g., `AAPL`).
    -   For **General Information**: Call `web_search` with a clear query.
4.  **Execute Tool Calls:** Run the tool.
5.  **Process Observations:** Use the tool's output to inform your next steps or form the final answer.
6.  **Refine and Answer:** Construct a clear, concise, and accurate final answer. If multiple steps or tools are needed, demonstrate multi-step reasoning.

**Important Instructions:**
-   If a calculation involves steps not directly covered by a simple `calculator` expression, prefer `python_repl`.
-   Be explicit about which tool you are using and why, if asked to explain.
-   Always provide a definitive final answer to the user's request.
"""

# Create ReAct Agent (without system_message here)
agent = create_react_agent(
    llm_with_tools,
    tools,
)

# --- Streamlit App UI ---
st.title("💰 Agentic Financial Assistant")
st.markdown("### Powered by LangGraph & Gemini 2.5 Pro")

# Session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    # Use msg.content for displaying, assuming messages are stored as dicts or similar
    # If you store actual BaseMessage objects, you might need msg.content
    if isinstance(msg, dict):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    else: # Assume it's a BaseMessage object
         with st.chat_message(msg.type): # 'human' or 'ai'
            st.markdown(msg.content)


# User input
if prompt := st.chat_input("Ask me about financial calculations, stock prices, or general financial advice..."):
    # Append user message (as a dict for consistent display logic, or as HumanMessage)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            # Prepare messages for the agent, including the SystemMessage
            # The agent expects a list of BaseMessage objects for input
            agent_input_messages = [SystemMessage(content=SYSTEM_PROMPT)] + \
                                   [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) 
                                    for m in st.session_state.messages if m["role"] != "user" or m["content"] != prompt] + \
                                   [HumanMessage(content=prompt)]

            response = agent.invoke({"messages": agent_input_messages})
            
            # The final response from the agent is typically the last message content
            final_response = response["messages"][-1].content

            # Append and display agent response
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            with st.chat_message("assistant"):
                st.markdown(final_response)

            # Optional: Display tool calls for debugging/transparency
            with st.expander("Detailed Agent Trace (Tool Calls & Thoughts)"):
                for msg in response["messages"]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        st.write(f"**Agent Thought (Tool Call):**")
                        for tool_call in msg.tool_calls:
                            st.json(tool_call.dict())
                    elif msg.type == 'tool':
                        st.write(f"**Tool Observation ({msg.name}):**")
                        st.code(msg.content, language="json")
                    elif msg.type == 'ai':
                        st.write(f"**Agent AI Message:** {msg.content}")
                    elif msg.type == 'human':
                        st.write(f"**Human Input:** {msg.content}")

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})
            with st.chat_message("assistant"):
                st.error(f"An error occurred: {e}. Please try again.")
