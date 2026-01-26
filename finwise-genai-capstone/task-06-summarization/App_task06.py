import os
import streamlit as st
from sqlalchemy import create_engine

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

# -----------------------------------------------------
# STREAMLIT UI (UNCHANGED)
# -----------------------------------------------------
st.set_page_config(
    page_title="SQL QA Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    text-align: center;
    color: #1f77b4;
}
.answer-box {
    background-color: #f0f8ff;
    color: black;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #1f77b4;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# API KEY
# -----------------------------------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("Please add GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

os.environ["GOOGLE_API_KEY"] = api_key

# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------
st.sidebar.header("⚙️ Settings")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.1)

# -----------------------------------------------------
# LLM
# -----------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=temperature
)

# -----------------------------------------------------
# DATABASE
# -----------------------------------------------------
DB_URI = st.secrets.get("DATABASE_URL")

if not DB_URI:
    st.error("DATABASE_URL not found in secrets.")
    st.stop()

engine = create_engine(DB_URI)
db = SQLDatabase(engine)

# -----------------------------------------------------
# SQL TOOL
# -----------------------------------------------------
sql_tool = QuerySQLDatabaseTool(db=db)

tools = [sql_tool]

# -----------------------------------------------------
# LANGGRAPH AGENT (2026 WAY)
# -----------------------------------------------------
agent = create_react_agent(
    llm=llm,
    tools=tools
)

# -----------------------------------------------------
# MAIN UI
# -----------------------------------------------------
st.markdown(
    "<h1 class='main-header'>🧠 SQL Question Answering Assistant</h1>",
    unsafe_allow_html=True
)

question = st.text_input(
    "Ask a question about your database:",
    placeholder="e.g. What is the total revenue in 2024?"
)

if st.button("🚀 Run Query"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Querying database..."):
            result = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=question)
                    ]
                }
            )

        final_answer = result["messages"][-1].content

        st.subheader("📊 Answer")
        st.markdown(
            f"<div class='answer-box'>{final_answer}</div>",
            unsafe_allow_html=True
        )
