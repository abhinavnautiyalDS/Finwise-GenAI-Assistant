import os
import streamlit as st
import math
import requests
import json
import warnings

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_experimental.utilities.python import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

warnings.filterwarnings('ignore')

# ── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic Financial Assistant (LangGraph + Groq)",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 About This Agent")
    st.markdown("""
    Autonomous AI agent for financial calculations & information retrieval.
    
    **Backend:** Groq (Llama-3.1-70B)  
    **Framework:** LangGraph ReAct agent  
    **Tools:** Calculator, Python REPL, Stock prices, Web search
    
    **Example questions:**
    - Monthly EMI for 20 lakh loan, 9% interest, 5 years?
    - Future value of ₹10,000 at 7% for 10 years?
    - Current price of RELIANCE.NS or TSLA?
    - Latest trends in Indian mutual funds?
    """)
    st.markdown("---")
    st.info("Needs `GROQ_API_KEY` in secrets.toml (optional: `ALPHA_VANTAGE_KEY`)")
    st.markdown("---")
    st.markdown("Built with ❤️ using LangChain + LangGraph + Groq")

# ── Load API Keys ────────────────────────────────────────────────────────────
@st.cache_resource
def load_api_keys():
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
        os.environ["GROQ_API_KEY"] = groq_key

        alpha_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")
        if alpha_key:
            os.environ["ALPHA_VANTAGE_KEY"] = alpha_key
            st.sidebar.success("Groq & Alpha Vantage keys loaded")
        else:
            st.sidebar.warning("No Alpha Vantage key → stock tool uses dummy data")

        return groq_key, alpha_key
    except KeyError as e:
        st.sidebar.error(f"Missing key: {e}. Add to secrets.toml")
        st.stop()
    except Exception as e:
        st.sidebar.error(f"Key loading error: {e}")
        st.stop()

GROQ_API_KEY, ALPHA_VANTAGE_KEY = load_api_keys()

# ── LLM (Groq) ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        model_name="llama-3.1-70b-versatile",
        # Alternatives: "llama-3.1-8b-instant", "mixtral-8x7b-32768"
        temperature=0.15,
        max_tokens=1024,
        groq_api_key=GROQ_API_KEY
    )

llm = get_llm()

# ── Tools ────────────────────────────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Calculate EMI or simple math. Use format: EMI(2000000, 0.09, 60)"""
    try:
        if expression.startswith("EMI("):
            args = expression[4:-1].split(",")
            if len(args) != 3:
                return "Error: EMI needs 3 args: principal, annual_rate, months"
            P = float(args[0].strip())
            r_annual = float(args[1].strip())
            n = int(args[2].strip())

            r_monthly = r_annual / 12
            if r_monthly == 0:
                return f"Monthly EMI: ₹{P / n:.2f}"
            emi = P * r_monthly * (1 + r_monthly)**n / ((1 + r_monthly)**n - 1)
            return f"Monthly EMI: ₹{emi:.2f}"
        else:
            return str(eval(expression))
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def python_repl(code: str) -> str:
    """Execute Python code for complex math / finance calculations."""
    try:
        repl = PythonREPL()
        result = repl.run(code)
        return str(result).strip()
    except Exception as e:
        return f"Python REPL error: {str(e)}"


@tool
def stock_price(symbol: str) -> str:
    """Get current stock price (e.g. RELIANCE.NS, TSLA)."""
    if not ALPHA_VANTAGE_KEY:
        return f"Alpha Vantage key missing. Simulated price for {symbol}: $150.00"

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if "Global Quote" in data and data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            return f"Current price for {symbol}: ${price:.2f}"
        return f"No valid quote found for {symbol}"
    except Exception as e:
        return f"Stock fetch error: {str(e)}"


@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Search error: {str(e)}"


tools = [calculator, python_repl, stock_price, web_search]

# Bind tools
llm_with_tools = llm.bind_tools(tools)

# Create ReAct agent
agent = create_react_agent(llm_with_tools, tools)

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a precise financial assistant. Follow ReAct pattern:
1. Think step-by-step
2. Decide which tool(s) to use
3. Call tools with correct arguments
4. Use results to answer clearly and accurately

Preferred tools:
- EMI / simple math → calculator
- Complex formulas / compound interest → python_repl
- Stock prices → stock_price
- General knowledge / news → web_search

Always give a final clear answer after using tools."""
