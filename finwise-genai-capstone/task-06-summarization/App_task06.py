import os
import tempfile
import streamlit as st
import requests
import json
from pathlib import Path
from pypdf import PdfReader

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# Custom CSS (ONLY chain UI added)
# ============================
st.markdown("""
<style>

.chain-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 14px;
    width: 100%;
}

.chain-label-ui {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-bottom: 6px;
}

.chain-select select {
    background-color: #020617 !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid #374151 !important;
}

</style>
""", unsafe_allow_html=True)

# ============================
# Initialize OpenRouter API
# ============================
def init_openrouter():
    try:
        return st.secrets["OPENROUTER_API_KEY"], "ok"
    except KeyError:
        return None, "missing"

# ============================
# API Configuration
# ============================
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct"
MAX_OUTPUT_TOKENS = 1000

# ============================
# Token helpers
# ============================
def truncate_text(text, max_tokens=6000):
    max_chars = max_tokens * 4
    return text[:max_chars], len(text) // 4, len(text) > max_chars

# ============================
# File processing
# ============================
def extract_text_from_pdf(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(file_bytes)
        path = f.name

    reader = PdfReader(path)
    text = ""
    for p in reader.pages:
        t = p.extract_text()
        if t:
            text += t + "\n\n"

    os.unlink(path)
    return text.strip(), len(reader.pages)

def extract_text_from_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore"), 1

def process_uploaded_file(uploaded_file):
    data = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        return (*extract_text_from_pdf(data), "PDF")
    if uploaded_file.type == "text/plain":
        return (*extract_text_from_txt(data), "TXT")
    return "", 0, None

# ============================
# Summarizer
# ============================
def summarize_financial_document(text, api_key, temperature):
    truncated, _, _ = truncate_text(text)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a financial document summarizer."},
            {"role": "user", "content": truncated}
        ],
        "temperature": temperature,
        "max_tokens": MAX_OUTPUT_TOKENS
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    r = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=120)
    return r.json()["choices"][0]["message"]["content"]

# ============================
# MAIN APP
# ============================

api_key, _ = init_openrouter()

st.markdown("## 💼 Financial Document Summarizer")

# ============================
# OPTIONS ROW
# ============================
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Temperature**")
    temperature = st.slider("", 0.0, 1.0, 0.6, 0.1, label_visibility="collapsed")

with col2:
    st.markdown("""
    <div class="chain-card">
        <div class="chain-label-ui">Chain Type</div>
    </div>
    """, unsafe_allow_html=True)

    chain_type = st.selectbox(
        "",
        ["stuff", "map_reduce", "refine", "map_rerank"],
        label_visibility="collapsed"
    )

st.markdown(
    "Upload PDF or TXT financial documents to generate a concise financial summary."
)

# ============================
# FILE UPLOAD
# ============================
uploaded_file = st.file_uploader("", type=["pdf", "txt"])

# ============================
# PROCESS
# ============================
if uploaded_file:
    text, pages, file_type = process_uploaded_file(uploaded_file)

    st.success(f"Loaded {pages} pages from {file_type}")

    if st.button("Generate Financial Summary"):
        with st.spinner("Generating..."):
            summary = summarize_financial_document(text, api_key, temperature)

        st.markdown("### Financial Summary")
        st.markdown(summary)

        st.download_button(
            "Download Summary",
            summary,
            file_name="summary.txt"
        )
