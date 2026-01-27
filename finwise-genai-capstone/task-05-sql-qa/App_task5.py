import os
import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

# Updated LangChain imports
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_openai import ChatOpenAI

# Try multiple import locations for StreamlitCallbackHandler
try:
    from langchain_community.callbacks import StreamlitCallbackHandler
except ImportError:
    try:
        from langchain.callbacks import StreamlitCallbackHandler
    except ImportError:
        # Fallback: create a simple callback handler
        class StreamlitCallbackHandler:
            def __init__(self, container):
                self.container = container
            
            def __call__(self, *args, **kwargs):
                pass

# ── Config ───────────────────────────────────────────────────────────────────
DB_FILE = "financial_data.db"
GITHUB_DB_URL = "https://github.com/abhinavnautiyalDS/Finwise-GenAI-Assistant/raw/main/finwise-genai-capstone/task-05-sql-qa/financial_data.db"

st.set_page_config(page_title="💰 Financial Data QA System", layout="wide")
st.title("💰 Financial Data Question Answering System")
st.markdown("Ask questions about clients and investments in natural language.")

# ── Load OpenRouter API Key ──────────────────────────────────────────────────
@st.cache_resource
def load_api_key():
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        os.environ["OPENROUTER_API_KEY"] = key
        os.environ["OPENAI_API_KEY"] = key  # For compatibility
        return key
    except KeyError:
        st.error("OPENROUTER_API_KEY not found in secrets.toml. Please add it.")
        st.stop()
    except Exception as e:
        st.error(f"API key load failed: {e}")
        st.stop()

load_api_key()

# ── DB Download if missing ───────────────────────────────────────────────────
if not os.path.exists(DB_FILE):
    st.info("Downloading database from GitHub...")
    try:
        r = requests.get(GITHUB_DB_URL, timeout=15)
        r.raise_for_status()
        with open(DB_FILE, "wb") as f:
            f.write(r.content)
        st.success("Database downloaded successfully ✓")
    except Exception as e:
        st.error(f"Database download failed: {e}")
        st.stop()
else:
    st.info("Using local database.")

# ── Initialize SQL Agent ─────────────────────────────────────────────────────
@st.cache_resource(ttl=3600)
def init_sql_agent():
    try:
        # Configure LLM for OpenRouter with Mistral 7B
        llm = ChatOpenAI(
            model="nousresearch/hermes-3-llama-3.1-8b:free",
            temperature=0.0,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
            max_tokens=500
        )
        
        # Create database connection
        db = SQLDatabase.from_uri(f"sqlite:///{DB_FILE}")
        
        # Create toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        
        # Create agent with simpler configuration
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="openai-tools",
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate",
        )
        return agent
    except Exception as e:
        st.error(f"Agent initialization failed: {str(e)}")
        # Show more detailed error
        with st.expander("Detailed error information"):
            import traceback
            st.code(traceback.format_exc())
        
        st.info("""
        **Troubleshooting tips:**
        1. Check if your OpenRouter API key is valid
        2. Make sure you have internet connectivity
        3. Try using a different model (e.g., `openai/gpt-3.5-turbo` for testing)
        4. Check if the database has the correct tables
        """)
        return None

# Initialize agent
agent = init_sql_agent()

if agent is None:
    st.stop()

# ── Chat Interface ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Ask Questions")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Create callback handler
                thought_container = st.container()
                callback = StreamlitCallbackHandler(thought_container)
                
                # Run the agent
                response = agent.invoke(
                    {"input": prompt},
                    config={"callbacks": [callback]}
                )
                
                # Get answer
                answer = response.get("output", "I couldn't process your question. Please try again.")
                
                # Display answer
                st.markdown("**Answer:**")
                st.success(answer)
                
                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Optional: Send to N8N webhook
                N8N_URL = st.secrets.get("N8N_SQL_QA_WEBHOOK_URL") or os.getenv("N8N_SQL_QA_WEBHOOK_URL")
                if N8N_URL:
                    try:
                        requests.post(
                            N8N_URL,
                            json={
                                "question": prompt,
                                "answer": answer,
                                "timestamp": datetime.now().isoformat()
                            },
                            timeout=5
                        )
                    except:
                        pass  # Silently fail if N8N not available
                        
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

# ── Database Preview ─────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Database Preview")

# Test database connection
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if tables:
        st.info(f"Found {len(tables)} table(s): {', '.join([t[0] for t in tables])}")
        
        # Show preview for each table
        cols = st.columns(min(2, len(tables)))
        for idx, table in enumerate(tables):
            table_name = table[0]
            with cols[idx % 2]:
                with st.expander(f"📊 {table_name} (first 3 rows)"):
                    try:
                        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
                        st.dataframe(df, use_container_width=True)
                        
                        # Show row count
                        count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table_name}", conn)
                        st.caption(f"Total rows: {count_df['count'].iloc[0]}")
                    except Exception as e:
                        st.error(f"Could not read {table_name}: {e}")
    else:
        st.warning("No tables found in the database!")
        
    conn.close()
    
except Exception as e:
    st.error(f"Database connection error: {e}")

# ── Sample Questions ─────────────────────────────────────────────────────────
with st.expander("💡 Try these sample questions"):
    st.markdown("""
    **Simple queries:**
    - How many clients are there?
    - What is the total portfolio value?
    - List all clients with high risk profile
    
    **Complex queries:**
    - Show clients with portfolio value greater than 10 lakh
    - Which fund has the highest total investment?
    - What is the average age of clients?
    - Show investments made in 2024
    
    **Join queries:**
    - Show all investments with client names
    - Which client has the highest total investment?
    - List clients and their total investment amounts
    """)

# ── Clear Chat Button ────────────────────────────────────────────────────────
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

st.caption("Powered by Streamlit, LangChain, and Mistral 7B via OpenRouter • 2026")
