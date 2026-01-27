import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS to hide the drag-and-drop box and style the button
st.markdown("""
<style>
    /* Hide the drag-and-drop box */
    section[data-testid="stFileUploader"] > div {
        border: none !important;
        background: none !important;
    }
    
    section[data-testid="stFileUploader"] > div > div {
        display: none !important;
    }
    
    /* Style the browse button */
    .stFileUploader button {
        background-color: #1E88E5 !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        width: 100% !important;
        margin-top: 20px !important;
    }
    
    .stFileUploader button:hover {
        background-color: #1565C0 !important;
    }
    
    /* Remove the subheading */
    h3, h4, h5, h6 {
        display: none;
    }
    
    /* Style the title */
    h1 {
        color: #1E88E5;
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("📄 Document Summarizer")

# File uploader with visible button
uploaded_file = st.file_uploader(
    "Upload PDF or TXT file",
    type=["pdf", "txt"],
    help="Upload a PDF or TXT file to summarize (max 200MB)"
)

# Information sections
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚙️ Configuration")
    st.markdown("- **Model:** Mistral 7B")
    st.markdown("- **Provider:** Mistral AI via OpenRouter")
    st.markdown("- **Max Summary Length:** 500 tokens")

with col2:
    st.markdown("### 📊 Token Limits")
    st.markdown("- **Max Context:** 32,768 tokens")
    st.markdown("- **Output Limit:** 500 tokens")
    st.markdown("- **Input Available:** 32,268 tokens")

st.markdown("---")

# Footer
st.markdown(
    """
    <div style="text-align: center; color: #666; margin-top: 50px;">
        <p>Built with Streamlit • Powered by Mistral 7B via OpenRouter</p>
    </div>
    """,
    unsafe_allow_html=True
)
