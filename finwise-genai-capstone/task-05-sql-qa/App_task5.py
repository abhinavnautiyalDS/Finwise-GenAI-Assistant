import os
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import requests # Import requests for N8N webhook
from datetime import datetime, timedelta
import google.generativeai as genai
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_sql_agent
from langchain.callbacks import StreamlitCallbackHandler  # For verbose output in Streamlit

# --------------------------------------------------------
# --- Configuration ---
# --------------------------------------------------------
DB_FILE = "financial_data.db"
GITHUB_DB_URL = "https://github.com/abhinavnautiyalDS/Finwise-GenAI-Assistant/raw/main/finwise-genai-capstone/task-05-sql-qa/financial_data.db"

st.set_page_config(page_title="💰 Financial Data QA System", layout="wide")
st.title("💰 Financial Data Question Answering System")
st.markdown("Ask natural language questions about our financial database (clients & investments).")

# --------------------------------------------------------
# --- Load API Key ---
# --------------------------------------------------------
@st.cache_resource
def load_api_key():
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key
        genai.configure(api_key=google_api_key)
        st.success("✅ Google API Key loaded successfully.")
        return True
    except KeyError:
        st.error("❌ Google API Key not found. Please add it to `.streamlit/secrets.toml`.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading API key: {e}")
        st.stop()

if 'api_key_loaded' not in st.session_state:
    st.session_state.api_key_loaded = load_api_key()

# --------------------------------------------------------
# --- GitHub Database Fetch ---
# --------------------------------------------------------
def fetch_github_db():
    if not os.path.exists(DB_FILE):
        st.info("Database not found locally. Downloading from GitHub...")
        try:
            response = requests.get(GITHUB_DB_URL)
            response.raise_for_status()
            with open(DB_FILE, "wb") as f:
                f.write(response.content)
            st.success("✅ Database downloaded from GitHub successfully.")
        except Exception as e:
            st.error(f"❌ Failed to fetch database from GitHub: {e}")
            st.stop()
    else:
        st.info("✅ Using local cached database.")

fetch_github_db()

# --------------------------------------------------------
# --- LangChain Initialization ---
# --------------------------------------------------------
@st.cache_resource(ttl=3600)
def initialize_langchain_agent():
    if not os.path.exists(DB_FILE):
        st.error("Database missing. Please ensure the GitHub DB is accessible.")
        return None

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Improved prompt
    prompt_template = """
    You are an expert AI assistant interacting with a financial database.
    Convert the user question into an accurate SQL query, execute it, and explain the answer clearly.

    Database tables:
    - clients(client_id, name, age, risk_profile, portfolio_value)
    - investments(investment_id, client_id, fund_name, amount_invested, date)

    Interpret number units correctly:
    - 'L' or 'lakh' = ×100,000
    - 'Cr' or 'crore' = ×10,000,000
    - 'K' or 'thousand' = ×1,000

    Answer only using available data. Never invent or assume data.
    If data isn’t found, state that clearly.

    Question: {input}
    """

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent, prompt_template

if 'agent_executor' not in st.session_state:
    agent_data = initialize_langchain_agent()
    if agent_data:
        st.session_state.agent_executor, st.session_state.prompt_template = agent_data
        st.sidebar.success("✅ LangChain agent initialized!")

# --------------------------------------------------------
# --- Question Handling ---
# --------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = []

if 'agent_executor' in st.session_state:
    st.markdown("---")
    st.subheader("Ask Your Question")

    user_question = st.text_input(
        "Enter a question related to clients or investments:",
        "Show all high-risk clients with portfolio value greater than 1,000,000."
    )

    st.markdown("**Examples:**")
    st.markdown("- Who are clients with medium risk and portfolio < 5L?")
    st.markdown("- Total amount invested in 'Tech Innovators' fund?")
    st.markdown("- Average portfolio value by risk profile?")

    if st.button("Get Answer", type="primary"):
        if user_question.strip():
            st.info("⏳ Querying the database...")
            st_callback = StreamlitCallbackHandler(st.empty())

            try:
                formatted_prompt = PromptTemplate.from_template(st.session_state.prompt_template).format(input=user_question)
                with st.spinner("Generating SQL and fetching answer..."):
                    response = st.session_state.agent_executor.invoke(
                        {"input": formatted_prompt},
                        config={"callbacks": [st_callback]}
                    )
                st.subheader("🧠 AI Answer:")
                st.success(response['output'])

                # Save history
                st.session_state.history.append({
                    "question": user_question,
                    "answer": response['output']
                })

                # --- N8N Workflow Trigger ---
                # Get N8N Webhook URL from environment variables or Streamlit secrets
                # You should set this in .streamlit/secrets.toml: N8N_SQL_QA_WEBHOOK_URL="your_n8n_webhook_url"
                N8N_WEBHOOK_URL = os.environ.get("N8N_SQL_QA_WEBHOOK_URL", st.secrets.get("N8N_SQL_QA_WEBHOOK_URL"))
                
                if N8N_WEBHOOK_URL: # Check if a URL is provided
                    try:
                        # Prepare payload with relevant QA data
                        n8n_payload = {
                            "event": "sql_qa_query_answered",
                            "user_question": user_question,
                            "ai_answer": response['output'],
                            "timestamp": datetime.now().isoformat()
                        }
                        # Send a POST request to the N8N webhook
                        n8n_response = requests.post(N8N_WEBHOOK_URL, json=n8n_payload, timeout=10) # 10-second timeout
                        
                        if n8n_response.status_code == 200:
                            st.toast("N8N workflow triggered successfully!", icon="✅")
                        else:
                            st.toast(f"N8N workflow trigger failed: HTTP {n8n_response.status_code}", icon="⚠️")
                            st.info(f"N8N Response: {n8n_response.text}") # Show n8n's response for debugging
                    except requests.exceptions.Timeout:
                        st.toast("N8N workflow trigger timed out.", icon="⚠️")
                    except requests.exceptions.RequestException as e:
                        st.toast(f"N8N request error: {e}", icon="⚠️")
                    except Exception as e:
                        st.toast(f"Unexpected N8N error: {e}", icon="⚠️")
                else:
                    st.sidebar.info("N8N Webhook URL for SQL QA not configured. Skipping workflow trigger.")
                # --- End N8N Workflow Trigger ---

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Please enter a question first.")

    # Display history
    if st.session_state.history:
        with st.expander("📜 Conversation History"):
            for h in reversed(st.session_state.history):
                st.write(f"**Q:** {h['question']}")
                st.write(f"**A:** {h['answer']}")
                st.markdown("---")

else:
    st.info("Please ensure the API key and database are set up before asking questions.")

# --------------------------------------------------------
# --- Database Preview ---
# --------------------------------------------------------
st.markdown("---")
st.header("📊 Database Schema Preview")

col1, col2 = st.columns(2)
with col1:
    with st.expander("Clients Table"):
        if os.path.exists(DB_FILE):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    df_clients = pd.read_sql_query("SELECT * FROM clients LIMIT 5;", conn)
                    st.dataframe(df_clients)
            except Exception as e:
                st.error(f"Error loading clients table: {e}")

with col2:
    with st.expander("Investments Table"):
        if os.path.exists(DB_FILE):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    df_invest = pd.read_sql_query("SELECT * FROM investments LIMIT 5;", conn)
                    st.dataframe(df_invest)
            except Exception as e:
                st.error(f"Error loading investments table: {e}")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, LangChain, Google Gemini, and SQLite.")
