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
    page_title="Agentic Financial Assistant",
    page_icon="💰🤖",
    layout="centered",                # ← This fixes missing chat input / title issues
    initial_sidebar_state="expanded"
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Financial Agent")
    st.markdown("""
    **Autonomous AI Agent** for financial calculations and information.

    **Powered by:**
    - Groq (Llama-3.1-70B)
    - LangGraph ReAct pattern

    **Tools available:**
    - EMI & simple math calculator
    - Python code execution (complex finance)
    - Real-time stock prices (Alpha Vantage)
    - Web search (DuckDuckGo)

    **Example questions:**
    - Monthly EMI for 20 lakh loan at 9% for 5 years?
    - Future value of ₹10,000 at 7% for 10 years?
    - Current price of RELIANCE.NS or TSLA?
    - Latest trends in Indian mutual funds?
    """)
    st.markdown("---")
    st.info("Requires `GROQ_API_KEY` in secrets.toml\nOptional: `ALPHA_VANTAGE_KEY`")
    st.markdown("---")
    st.caption("Built by Abhinav Nautiyal • 2026")

# ── Load API Keys ────────────────────────────────────────────────────────────
@st.cache_resource
def load_api_keys():
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
        os.environ["GROQ_API_KEY"] = groq_key

        alpha_key = st.secrets.get("ALPHA_VANTAGE_KEY", "")
        if alpha_key:
            os.environ["ALPHA_VANTAGE_KEY"] = alpha_key

        return groq_key, alpha_key
    except KeyError as e:
        st.error(f"Missing key: {e}\nPlease add to secrets.toml")
        st.stop()
    except Exception as e:
        st.error(f"Error loading keys: {e}")
        st.stop()

GROQ_API_KEY, ALPHA_VANTAGE_KEY = load_api_keys()

st.sidebar.success("Groq key loaded ✓")

# ── LLM (Groq) ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        model_name="llama-3.1-70b-versatile",
        temperature=0.15,
        max_tokens=1024,
        groq_api_key=GROQ_API_KEY
    )

llm = get_llm()

# ── Tools ────────────────────────────────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """Calculate EMI or simple math. Example: EMI(2000000, 0.09, 60)"""
    try:
        if expression.startswith("EMI("):
            args = expression[4:-1].split(",")
            if len(args) != 3:
                return "Error: EMI needs 3 args: principal, rate, months"
            P = float(args[0].strip())
            r_annual = float(args[1].strip())
            n = int(args[2].strip())
            r_monthly = r_annual / 12
            if r_monthly == 0:
                return f"EMI: ₹{P / n:.2f}"
            emi = P * r_monthly * (1 + r_monthly)**n / ((1 + r_monthly)**n - 1)
            return f"Monthly EMI: ₹{emi:.2f}"
        else:
            return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def python_repl(code: str) -> str:
    """Run Python code for complex calculations."""
    try:
        repl = PythonREPL()
        return str(repl.run(code)).strip()
    except Exception as e:
        return f"REPL error: {str(e)}"

@tool
def stock_price(symbol: str) -> str:
    """Get stock price. Example: RELIANCE.NS, TSLA"""
    if not ALPHA_VANTAGE_KEY:
        return f"No API key → simulated price for {symbol}: $150.00"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if "Global Quote" in data and data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            return f"{symbol}: ${price:.2f}"
        return "No quote found"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Web search for information."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Search error: {str(e)}"

tools = [calculator, python_repl, stock_price, web_search]

llm_with_tools = llm.bind_tools(tools)
agent = create_react_agent(llm_with_tools, tools)

# ── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a precise financial assistant using ReAct pattern.
Always think step-by-step.
Choose the right tool:
- EMI/simple math → calculator
- Complex finance → python_repl
- Stock price → stock_price
- General info/news → web_search

Provide clear final answer after using tools."""

# ── Chat Interface ───────────────────────────────────────────────────────────
st.title("💰 Agentic Financial Assistant")
st.markdown("Ask anything about loans, investments, stocks, or finance trends")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your financial question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Agent thinking..."):
        try:
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            for m in st.session_state.messages:
                if m["role"] == "user":
                    messages.append(HumanMessage(content=m["content"]))
                else:
                    messages.append(AIMessage(content=m["content"]))

            response = agent.invoke({"messages": messages})

            final_msg = response["messages"][-1].content
            st.session_state.messages.append({"role": "assistant", "content": final_msg})

            with st.chat_message("assistant"):
                st.markdown(final_msg)

            # Optional debug expander
            with st.expander("Agent trace (tools & thoughts)"):
                for m in response["messages"]:
                    if hasattr(m, "tool_calls") and m.tool_calls:
                        st.json(m.tool_calls)
                    elif m.type == "tool":
                        st.code(m.content, language="text")

        except Exception as e:
            error_text = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_text})
            st.error(error_text)

# Footer
st.markdown(
    "<p style='text-align:center; color:#888; margin-top:40px;'>"
    "Built by Abhinav Nautiyal • Powered by Groq + LangGraph"
    "</p>",
    unsafe_allow_html=True
)
