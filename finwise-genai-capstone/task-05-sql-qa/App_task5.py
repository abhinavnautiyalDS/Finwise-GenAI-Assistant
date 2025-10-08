import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import io

import google.generativeai as genai
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_sql_agent
from langchain.callbacks import StreamlitCallbackHandler # For verbose output in Streamlit

# --- Configuration ---
DB_FILE = "financial_data.db"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Financial Data QA System", layout="wide")
st.title("💰 Financial Data Question Answering System")
st.markdown("Ask natural language questions about our dummy financial database!")

# --- API Key Loading ---
@st.cache_resource
def load_api_key():
    try:
        # Assuming GOOGLE_API_KEY is in Streamlit secrets
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = google_api_key
        genai.configure(api_key=google_api_key)
        st.success("Google API Key loaded successfully from Streamlit secrets.")
        return True
    except KeyError:
        st.error("Google API Key not found in Streamlit secrets. Please add it to your `.streamlit/secrets.toml` file.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading API key: {e}")
        st.stop()

if 'api_key_loaded' not in st.session_state:
    st.session_state.api_key_loaded = load_api_key()

# --- Database Setup Function ---
@st.cache_resource
def setup_database():
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
    client_data = {
        'client_id': range(1, num_clients + 1),
        'name': [f'Client {i}' for i in range(1, num_clients + 1)],
        'age': np.random.randint(25, 70, num_clients),
        'risk_profile': np.random.choice(['Low', 'Medium', 'High'], num_clients, p=[0.4, 0.3, 0.3]),
        'portfolio_value': np.random.uniform(50000, 5000000, num_clients).round(2)
    }
    clients_df = pd.DataFrame(client_data)

    num_investments = 100
    investment_data = []
    fund_names = ['Equity Growth', 'Bond Stabilizer', 'Tech Innovators', 'Global Diversified', 'Real Estate Income', 'Emerging Markets']

    for i in range(1, num_investments + 1):
        client_id = np.random.randint(1, num_clients + 1)
        fund_name = np.random.choice(fund_names)
        amount_invested = np.random.uniform(1000, 500000).round(2)
        start_date = datetime.now() - timedelta(days=5*365)
        random_days = np.random.randint(0, 5*365)
        investment_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        investment_data.append({
            'investment_id': i,
            'client_id': client_id,
            'fund_name': fund_name,
            'amount_invested': amount_invested,
            'date': investment_date
        })

    investments_df = pd.DataFrame(investment_data)

    # Insert data (if tables are empty or always replace for fresh data)
    # Using if_exists='replace' ensures fresh data every time setup_database is called if it's not cached
    clients_df.to_sql('clients', conn, if_exists='replace', index=False)
    investments_df.to_sql('investments', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    return True

# Ensure the database is set up
if st.sidebar.button("Setup/Recreate Database (resets data)", type="secondary"):
    with st.spinner("Setting up database with sample data..."):
        if setup_database():
            st.sidebar.success("Database 'financial_data.db' created and populated.")
            # Clear cache for LangChain components to pick up new DB
            st.session_state.langchain_initialized = False # Force re-initialization

if not os.path.exists(DB_FILE):
    st.warning("Database file not found. Please click 'Setup/Recreate Database' in the sidebar.")
else:
    st.sidebar.success(f"Database '{DB_FILE}' found.")

# --- LangChain Initialization ---
@st.cache_resource(ttl=3600) # Cache for 1 hour, or until manually cleared
def initialize_langchain_agent():
    if not os.path.exists(DB_FILE):
        st.error("Database file not found. Cannot initialize LangChain agent.")
        return None

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    db_langchain = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
    toolkit = SQLDatabaseToolkit(db=db_langchain, llm=llm)

    custom_prompt_template = """You are an AI assistant that interacts with a financial database.
    Your primary goal is to answer user questions by converting them into SQL queries, executing those queries, and then providing a clear, natural language answer.
    Only use the tables provided: clients, investments.
    Here are the schemas:
    clients: client_id (PK), name, age, risk_profile, portfolio_value
    investments: investment_id (PK), client_id (FK), fund_name, amount_invested, date

    When responding:
    - If the question involves 'portfolio > 10L', interpret '10L' as 1,000,000.
    - If the question involves 'portfolio < 5L', interpret '5L' as 500,000.
    - Always be concise and directly answer the question.
    - If you cannot find relevant information, state that clearly.
    - Do not make assumptions or invent data.
    - Double-check your SQL query before executing.
    
    Question: {input}
    """
    
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent_executor, custom_prompt_template

if 'langchain_initialized' not in st.session_state or not st.session_state.langchain_initialized:
    if os.path.exists(DB_FILE) and st.session_state.api_key_loaded:
        with st.spinner("Initializing LangChain agent..."):
            agent_data = initialize_langchain_agent()
            if agent_data:
                st.session_state.agent_executor = agent_data[0]
                st.session_state.custom_prompt_template = agent_data[1]
                st.session_state.langchain_initialized = True
                st.sidebar.success("LangChain agent initialized!")
            else:
                st.session_state.langchain_initialized = False
    else:
        st.info("Waiting for database setup and API key.")


# --- User Input and Query ---
if st.session_state.get('langchain_initialized', False):
    st.markdown("---")
    user_question = st.text_input("Ask a question about the financial data:", "Show me all high-risk clients with portfolio value greater than 1,500,000.")

    if st.button("Get Answer", type="primary"):
        if user_question:
            st.info("Querying the database...")
            # Use StreamlitCallbackHandler to display verbose output
            st_callback = StreamlitCallbackHandler(st.container())
            
            try:
                with st.spinner("Generating SQL and fetching answer..."):
                    # Capture the verbose output for display
                    # Redirect stdout to capture agent's thoughts
                    old_stdout = io.StringIO()
                    import sys
                    sys.stdout = old_stdout

                    response = st.session_state.agent_executor.invoke(
                        {"input": st.session_state.custom_prompt_template.format(input=user_question)},
                        config={"callbacks": [st_callback]} # Pass callback for direct Streamlit output
                    )
                    
                    sys.stdout = sys.__stdout__ # Restore stdout
                    verbose_output = old_stdout.getvalue()

                st.subheader("AI Answer:")
                st.success(response['output'])

                with st.expander("Show Agent's Thought Process (Verbose Output)"):
                    st.code(verbose_output)
                    # The StreamlitCallbackHandler already prints steps,
                    # but this captures the final 'observation' which might not be in the callback.
                    # We print it just in case, though st_callback should show most.

            except Exception as e:
                st.error(f"An error occurred during query: {e}")
                st.warning("Please check the question format or try recreating the database.")
        else:
            st.warning("Please enter a question.")
else:
    st.info("Please set up the database and ensure the API key is loaded to proceed.")

st.markdown("---")
st.markdown("#### Database Schema:")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Clients Table")
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            clients_df_preview = pd.read_sql_query("SELECT * FROM clients LIMIT 5;", conn)
            st.dataframe(clients_df_preview)
            conn.close()
        except Exception as e:
            st.error(f"Could not load clients table preview: {e}")
with col2:
    st.subheader("Investments Table")
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            investments_df_preview = pd.read_sql_query("SELECT * FROM investments LIMIT 5;", conn)
            st.dataframe(investments_df_preview)
            conn.close()
        except Exception as e:
            st.error(f"Could not load investments table preview: {e}")

st.markdown("---")
st.info("Built with Streamlit, LangChain, Google Gemini Pro, and SQLite.")
