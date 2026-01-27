import os
import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime
from openai import OpenAI

# Updated LangChain imports for newer versions
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_openai import ChatOpenAI  # Using ChatOpenAI for OpenRouter compatibility
from langchain_core.prompts import PromptTemplate
from langchain.callbacks import StreamlitCallbackHandler

# ── Config ───────────────────────────────────────────────────────────────────
DB_FILE = "financial_data.db"
GITHUB_DB_URL = "https://github.com/abhinavnautiyalDS/Finwise-GenAI-Assistant/raw/main/finwise-genai-capstone/task-05-sql-qa/financial_data.db"

st.set_page_config(page_title="💰 Financial Data QA System", layout="wide")
st.title("💰 Financial Data Question Answering System")
st.markdown("Clients & investments ke baare mein natural language mein poochho.")

# ── Load OpenRouter API Key ──────────────────────────────────────────────────
@st.cache_resource
def load_api_key():
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        os.environ["OPENROUTER_API_KEY"] = key
        os.environ["OPENAI_API_KEY"] = key  # For compatibility with ChatOpenAI
        return key
    except KeyError:
        st.error("OPENROUTER_API_KEY secrets.toml mein nahi hai. Please add it.")
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
        # Configure LLM for OpenRouter with Mistral 7B
        llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct:free",  # You can change to other Mistral models
            temperature=0.0,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=os.environ.get("OPENROUTER_API_KEY")
        )
        
        db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        CUSTOM_PROMPT = """
        You are a financial database expert.
        Tables:
        - clients(client_id, name, age, risk_profile, portfolio_value)
        - investments(investment_id, client_id, fund_name, amount_invested, date)

        Rules:
        - Convert user questions to accurate SQL queries
        - Handle number conversions: 'lakh' = 100000, 'crore' = 10000000, 'k' = 1000
        - If no data found, say "No matching records found"
        - Provide clear, concise answers after executing queries
        - Return only the SQL query when asked to generate SQL
        - For questions about data, execute the query and return the results

        Question: {input}
        
        Thought Process: {agent_scratchpad}
        """

        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="openai-tools",
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate",
            prefix=CUSTOM_PROMPT.strip()
        )
        return agent
    except Exception as e:
        st.error(f"Agent initialization failed: {e}")
        st.error("Check your OpenRouter API key and internet connection.")
        return None

agent = init_sql_agent()
if not agent:
    st.stop()

# ── Chat UI ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Sawaal poochho")

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input(
    "Sawaal: (e.g., High risk clients with portfolio > 10 lakh?)"
)

if user_question:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Prepare for agent response
    with st.chat_message("assistant"):
        with st.spinner("Database query kar raha hoon..."):
            try:
                # Create a container for the agent's thought process
                thought_container = st.container()
                callback = StreamlitCallbackHandler(thought_container)
                
                # Execute the agent
                response = agent.invoke(
                    {"input": user_question},
                    config={"callbacks": [callback]}
                )
                answer = response.get("output", "No response generated")
                
                # Display the final answer
                st.markdown("### 🎯 Jawaab:")
                st.success(answer)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.history.append({"role": "user", "content": user_question})
                st.session_state.history.append({"role": "assistant", "content": answer})

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
                                "timestamp": datetime.now().isoformat(),
                                "model": "mistral-7b-instruct"
                            },
                            timeout=8
                        )
                        st.toast("N8N trigger ho gaya ✓", icon="✅")
                    except Exception as e:
                        st.toast(f"N8N fail: {e}", icon="⚠️")

            except Exception as e:
                error_msg = f"Query failed: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ── History Section ──────────────────────────────────────────────────────────
if st.session_state.history:
    with st.expander("📜 Conversation History", expanded=False):
        for i, msg in enumerate(st.session_state.history):
            role = "🧑‍💻 Tum" if msg["role"] == "user" else "🤖 Assistant"
            st.markdown(f"**{role}:**")
            st.markdown(msg["content"])
            if i < len(st.session_state.history) - 1:
                st.markdown("---")

# ── DB Preview ───────────────────────────────────────────────────────────────
st.markdown("---")
st.header("🔍 Database Preview (first 5 rows)")

col1, col2 = st.columns(2)
with col1:
    with st.expander("👥 Clients Table"):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query("SELECT * FROM clients LIMIT 5", conn)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Clients table read fail: {e}")

with col2:
    with st.expander("💰 Investments Table"):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                df = pd.read_sql_query("SELECT * FROM investments LIMIT 5", conn)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Investments table read fail: {e}")

# ── SQL Schema Info ──────────────────────────────────────────────────────────
with st.expander("📋 Database Schema Information"):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                st.subheader(f"Table: `{table_name}`")
                
                # Get schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                schema_data = []
                for col in columns:
                    schema_data.append({
                        "Column": col[1],
                        "Type": col[2],
                        "Nullable": "No" if col[3] else "Yes",
                        "Default": col[4] if col[4] else "None",
                        "PK": "Yes" if col[5] else "No"
                    })
                
                df_schema = pd.DataFrame(schema_data)
                st.dataframe(df_schema, use_container_width=True)
                st.markdown("---")
    except Exception as e:
        st.error(f"Schema extraction failed: {e}")

st.caption("Streamlit + LangChain + Mistral 7B • Abhinav Nautiyal • 2026")
