import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
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
# --- Database Setup ---
# --------------------------------------------------------
def setup_database():
    st.info(f"Creating database at: {os.path.abspath(DB_FILE)}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create 'clients' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        risk_profile TEXT,
        portfolio_value REAL
    )
    ''')

    # Create 'investments' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investments (
        investment_id INTEGER PRIMARY KEY,
        client_id INTEGER,
        fund_name TEXT,
        amount_invested REAL,
        date TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(client_id)
    )
    ''')

    # --- Generate Sample Data ---
    num_clients = 35
    clients_df = pd.DataFrame({
        'client_id': range(1, num_clients + 1),
        'name': [f'Client {i}' for i in range(1, num_clients + 1)],
        'age': np.random.randint(25, 70, num_clients),
        'risk_profile': np.random.choice(['Low', 'Medium', 'High'], num_clients, p=[0.4, 0.3, 0.3]),
        'portfolio_value': np.random.uniform(50000, 5000000, num_clients).round(2)
    })

    num_investments = 100
    fund_names = ['Equity Growth', 'Bond Stabilizer', 'Tech Innovators', 'Global Diversified', 'Real Estate Income', 'Emerging Markets']
    investment_data = []

    start_date = datetime.now() - timedelta(days=5 * 365)
    for i in range(1, num_investments + 1):
        investment_data.append({
            'investment_id': i,
            'client_id': np.random.randint(1, num_clients + 1),
            'fund_name': np.random.choice(fund_names),
            'amount_invested': np.random.uniform(1000, 500000).round(2),
            'date': (start_date + timedelta(days=np.random.randint(0, 5 * 365))).strftime('%Y-%m-%d')
        })
    investments_df = pd.DataFrame(investment_data)

    # Insert/replace data
    clients_df.to_sql('clients', conn, if_exists='replace', index=False)
    investments_df.to_sql('investments', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    return True

# --- Check DB existence ---
if not os.path.exists(DB_FILE):
    st.warning("Database not found. Setting up new one...")
    with st.spinner("Setting up database..."):
        if setup_database():
            st.success("✅ Database created successfully.")

# Button for manual recreation
if st.sidebar.button("🔄 Recreate Database"):
    with st.spinner("Recreating database..."):
        if setup_database():
            st.sidebar.success("Database reset with fresh sample data.")

# --------------------------------------------------------
# --- LangChain Initialization ---
# --------------------------------------------------------
@st.cache_resource(ttl=3600)
def initialize_langchain_agent():
    if not os.path.exists(DB_FILE):
        st.error("Database missing. Please recreate it first.")
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
