import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import os

# --------------------------
# DATABASE SETUP
# --------------------------
DB_PATH = "/mount/src/finwise-genai-assistant/financial_data.db"

def setup_database():
    if os.path.exists(DB_PATH):
        return False  # Avoid recreating DB

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create clients table
    cursor.execute("""
    CREATE TABLE clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        city TEXT,
        risk_profile TEXT
    );
    """)

    # Create investments table
    cursor.execute("""
    CREATE TABLE investments (
        investment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        investment_type TEXT,
        amount_invested REAL,
        returns REAL,
        date TEXT,
        FOREIGN KEY (client_id) REFERENCES clients (client_id)
    );
    """)

    # Insert sample data
    names = ["John", "Priya", "Rahul", "Sophia", "Ken", "Maria"]
    cities = ["Delhi", "Mumbai", "Tokyo", "London", "Bangalore", "New York"]
    risk_profiles = ["Low", "Medium", "High"]

    clients_data = []
    for i in range(len(names)):
        clients_data.append((
            names[i],
            np.random.randint(25, 65),
            cities[i],
            np.random.choice(risk_profiles)
        ))

    cursor.executemany("INSERT INTO clients (name, age, city, risk_profile) VALUES (?, ?, ?, ?);", clients_data)

    investment_types = ["Stocks", "Mutual Funds", "Bonds", "Real Estate"]

    investments_data = []
    for client_id in range(1, len(names) + 1):
        for _ in range(3):
            investments_data.append((
                client_id,
                np.random.choice(investment_types),
                float(np.random.uniform(1000, 500000).round(2)),
                float(np.random.uniform(-0.1, 0.3).round(3)),
                "2025-10-10"
            ))

    cursor.executemany("""
    INSERT INTO investments (client_id, investment_type, amount_invested, returns, date)
    VALUES (?, ?, ?, ?, ?);
    """, investments_data)

    conn.commit()
    conn.close()
    return True


# --------------------------
# STREAMLIT APP
# --------------------------
st.set_page_config(page_title="Financial Data Question Answering System", page_icon="💰", layout="wide")

st.title("💰 Financial Data Question Answering System")
st.write("Ask natural language questions about our financial database (clients & investments).")

if setup_database():
    st.info(f"Created database at: {DB_PATH}")
else:
    st.info(f"Database already exists at: {DB_PATH}")

# --------------------------
# DATABASE CONNECTION
# --------------------------
conn = sqlite3.connect(DB_PATH)

# Show tables
st.subheader("📊 Tables in Database")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
st.dataframe(tables)

# Show sample data
st.subheader("👥 Clients Table Sample")
clients_df = pd.read_sql_query("SELECT * FROM clients LIMIT 5;", conn)
st.dataframe(clients_df)

st.subheader("💼 Investments Table Sample")
investments_df = pd.read_sql_query("SELECT * FROM investments LIMIT 5;", conn)
st.dataframe(investments_df)

conn.close()
