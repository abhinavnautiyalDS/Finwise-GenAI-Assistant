import os
import tempfile
import streamlit as st
import requests
from pypdf import PdfReader

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# UI CSS (ONLY chain UI styled)
# ============================
st.markdown("""
<style>

html, body, .stApp {
    background-color: #0b0f14;
    color: white;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
}

.chain-card {
    background: linear-gradient(180deg, #0f172a, #0b1220);
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 12px 16px;
}

.chain-label {
    color: #9ca3af;
    font-size: 0.9rem;
    margin-bottom: 6px;
}

.stSelectbox > div > div {
    background-color: #111827 !important;
    color: white !important;
    border-radius: 6px !important;
    border: 1px solid #374151 !important;
}

.stSlider > div > div > div > div {
    background-color: #ef4444 !important;
}

.upload-box {
    border: 1px solid #2b2f3a;
    border-radius: 10px;
    padding: 24px;
    background: #1b1f2a;
}

.status-green {
    background: #123b2a;
    border-left: 4px solid #22c55e;
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
}

button {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)

# ============================
# API INIT
# ============================
def init_openrouter():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except:
        return None

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-7b-instruct"

# ============================
# FILE HELPERS
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
        t, p = extract_text_from_pdf(data)
        return t, p, "PDF"
    if uploaded_file.type == "text/plain":
        t, p = extract_text_from_txt(data)
        return t, p, "TXT"
    return "", 0, None

# ============================
# SUMMARIZER
# ============================
def summarize_financial_document(text, api_key, temperature):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a financial document summarizer."},
            {"role": "user", "content": text[:24000]}
        ],
        "temperature": temperature,
        "max_tokens": 1000
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
api_key = init_openrouter()

st.markdown('<div class="main-title">💼 Financial Document Summarizer</div>', unsafe_allow_html=True)

# ============================
# OPTIONS ROW
# ============================
col1, col2 = st.columns([1.2, 1.8])

with col1:
    st.markdown("**Temperature**")
    temperature = st.slider(
        "",
        0.0, 1.0, 0.80, 0.05,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <div class="chain-card">
        <div class="chain-label">Chain Type</div>
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
# UPLOAD
# ============================
st.markdown('<div class="upload-box">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag and drop file here",
    type=["pdf", "txt"],
    label_visibility="collapsed"
)

st.markdown("Limit 200MB per file · PDF, TXT")
st.markdown("</div>", unsafe_allow_html=True)

# ============================
# PROCESS
# ============================
if uploaded_file:
    size_kb = len(uploaded_file.getvalue()) / 1024

    st.markdown(
        f"📄 **{uploaded_file.name}** · {size_kb:.1f} KB"
    )

    with st.spinner("Processing document..."):
        text, pages, ftype = process_uploaded_file(uploaded_file)

    if text:
        st.markdown(
            f"""
            <div class="status-green">
            ✅ Loaded {pages} pages from PDF
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Generate Financial Summary"):
            with st.spinner("Generating summary..."):
                summary = summarize_financial_document(
                    text,
                    api_key,
                    temperature
                )

            st.markdown("### 📘 Financial Summary")
            st.markdown(summary)

            st.download_button(
                "Download Summary",
                summary,
                file_name="financial_summary.txt"
            )

# ============================
# MANAGE APP
# ============================
with st.expander("Manage app"):
    st.info("""
Model: mistralai/mistral-7b-instruct  
Context: 8k tokens  
Files: PDF, TXT  
""")
