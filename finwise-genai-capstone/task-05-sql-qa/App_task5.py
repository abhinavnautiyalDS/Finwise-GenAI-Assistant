import os
import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

import google.generativeai as genai
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_sql_agent
from langchain.callbacks import StreamlitCallbackHandler

# ── Config ───────────────────────────────────────────────────────────────────
DB_FILE = "financial_data.db"
GITHUB_DB_URL = "https://github.com/abhinavnautiyalDS/Finwise-GenAI-Assistant/raw/main/finwise-genai-capstone/task-05-sql-qa/financial_data.db"

st.set_page_config(page_title="💰 Financial Data QA System", layout="wide")
st.title("💰 Financial Data Question Answering System")
st.markdown("Clients & investments ke baare mein natural language mein poochho.")

# ── Load Google API Key ──────────────────────────────────────────────────────
@st.cache_resource
def load_api_key():
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = key
        genai.configure(api_key=key)
        return key
    except KeyError:
        st.error("GOOGLE_API_KEY secrets.toml mein nahi hai")
        st.stop()
    except Exception as e:
        st.error(f"API key load fail: {e}")
        st.stop()

load_api_key()

# ── DB Download if missing ───────────────────────────────────────────────────
if not os.path.exists(DB_FILE):
    st.info("DB GitHub se download ho raha hai...")
    try:
        r = requests.get(GITHUB_DB_URL, timeout=15)
        r.raise_for_status()
        with open(DB_FILE, "wb") as f:
            f.write(r.content)
        st.success("DB download ho gaya ✓")
    except Exception as e:
        st.error(f"DB download fail: {e}")
        st.stop()
else:
    st.info("Local DB use kar raha hoon.")

# ── Initialize SQL Agent ─────────────────────────────────────────────────────
@st.cache_resource(ttl=3600)
def init_sql_agent():
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
        db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        CUSTOM_PROMPT = """
        Financial database expert ho tum.
        Tables:
        - clients(client_id, name, age, risk_profile, portfolio_value)
        - investments(investment_id, client_id, fund_name, amount_invested, date)

        Rules:
        - User question ko accurate SQL mein convert karo
        - 'lakh' = 100000, 'crore' = 10000000, 'k' = 1000 ko handle karo
        - Data nahi mila toh "No matching records" bolo
        - Clear answer do query ke baad

        Question: {input}
        """

        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="openai-tools",
            handle_parsing_errors=True,
            prefix=CUSTOM_PROMPT.strip()
        )
        return agent
    except Exception as e:
        st.error(f"Agent init fail: {e}")
        return None

agent = init_sql_agent()
if not agent:
    st.stop()

# ── Chat UI ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Sawaal poochho")

if "history" not in st.session_state:
    st.session_state.history = []

user_question = st.text_input(
    "Sawaal:",
    placeholder="e.g. High risk clients with portfolio > 10 lakh?"
)

if st.button("Jawaab do →", type="primary") and user_question.strip():
    st.session_state.history.append({"role": "user", "content": user_question})

    with st.spinner("Database query kar raha hoon..."):
        try:
            callback = StreamlitCallbackHandler(st.container())
            response = agent.invoke(
                {"input": user_question},
                config={"callbacks": [callback]}
            )
            answer = response["output"]
            st.session_state.history.append({"role": "assistant", "content": answer})

            st.subheader("Jawaab:")
            st.success(answer)

            # N8N webhook (optional)
            N8N_URL = st.secrets.get("N8N_SQL_QA_WEBHOOK_URL") or os.getenv("N8N_SQL_QA_WEBHOOK_URL")
            if N8N_URL:
                try:
                    requests.post(
                        N8N_URL,
                        json={
                            "event": "sql_question_asked",
                            "question": user_question,
                            "answer": answer,
                            "timestamp": datetime.now().isoformat()
                        },
                        timeout=8
                    )
                    st.toast("N8N trigger ho gaya ✓", icon="✅")
                except Exception as e:
                    st.toast(f"N8N fail: {e}", icon="⚠️")

        except Exception as e:
            st.error(f"Query fail: {str(e)}")

# History show karo
if st.session_state.history:
    with st.expander("History", expanded=True):
        for msg in st.session_state.history:
            role = "Tum" if msg["role"] == "user" else "Agent"
            st.markdown(f"**{role}:** {msg['content']}")
            st.markdown("---")

# ── DB Preview ───────────────────────────────────────────────────────────────
st.markdown("---")
st.header("DB Preview (first 5 rows)")

col1, col2 = st.columns(2)
with col1:
    with st.expander("Clients Table"):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query("SELECT * FROM clients LIMIT 5", conn)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Clients table read fail: {e}")

with col2:
    with st.expander("Investments Table"):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query("SELECT * FROM investments LIMIT 5", conn)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Investments table read fail: {e}")

st.caption("Streamlit + LangChain + Gemini • Abhinav Nautiyal • 2026")
