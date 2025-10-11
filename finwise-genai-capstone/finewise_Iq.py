import streamlit as st
import webbrowser

# --- Page Configuration ---
st.set_page_config(
    page_title="Finwise Capital | AI-Driven Wealth Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Styling ---
primary_color = "#004d40"
secondary_color = "#007BFF"
accent_color = "#FF6B35"

st.markdown(f"""
<style>
/* General body and Streamlit app styling */
html, body, .stApp {{
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}}

.main-container {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px;
    margin: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}}

/* Main Title Styling */
.main-title {{
    color: {primary_color};
    text-align: center;
    font-size: 3em;
    font-weight: 700;
    margin-bottom: 20px;
    background: linear-gradient(135deg, {primary_color}, {accent_color});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* Section Header Styling */
.section-header {{
    color: {primary_color};
    text-align: center;
    font-size: 2.2em;
    font-weight: 600;
    margin-top: 50px;
    margin-bottom: 40px;
}}

/* Main Description Styling */
.main-description {{
    font-size: 1.2em;
    line-height: 1.7;
    text-align: center;
    max-width: 900px;
    margin: auto;
    padding: 25px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    border-left: 4px solid {accent_color};
}}

/* Individual Block Container Styling */
.block-container {{
    background: linear-gradient(145deg, #ffffff, #f8f9fa);
    border-radius: 16px;
    padding: 30px 25px;
    margin-bottom: 30px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    text-align: center;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
}}

.block-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {primary_color}, {accent_color});
}}

.block-container:hover {{
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    border-color: {secondary_color};
}}

/* Block Title Styling */
.block-title {{
    font-size: 1.5em;
    font-weight: 700;
    color: {primary_color};
    margin-bottom: 15px;
    padding: 10px 20px;
    background: rgba(0, 77, 64, 0.05);
    border-radius: 25px;
    width: 100%;
}}

/* Block Description Styling */
.block-description {{
    font-size: 1em;
    color: #555555;
    flex-grow: 1;
    line-height: 1.6;
    margin-bottom: 25px;
    padding: 0 10px;
}}

/* Icon Styling */
.block-icon {{
    font-size: 3.5em;
    margin-bottom: 20px;
    background: linear-gradient(135deg, {primary_color}, {accent_color});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}}

/* Streamlit Button Styling */
.stButton > button {{
    background: linear-gradient(135deg, {secondary_color}, {accent_color}) !important;
    color: white !important;
    border: none !important;
    padding: 14px 35px !important;
    border-radius: 50px !important;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 15px rgba(0, 123, 255, 0.3) !important;
    width: 100% !important;
    margin-top: 10px !important;
}}

.stButton > button:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 25px rgba(0, 123, 255, 0.4) !important;
    background: linear-gradient(135deg, {accent_color}, {secondary_color}) !important;
}}

/* Footer Styling */
.footer {{
    text-align: center;
    margin-top: 60px;
    padding: 30px;
    color: #666666;
    font-size: 1em;
    border-top: 2px solid #eeeeee;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
}}

/* Success Message Styling */
.success-message {{
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    color: #155724;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #28a745;
    text-align: center;
    font-weight: 600;
}}

/* Grid Layout Improvements */
.row-container {{
    display: flex;
    flex-wrap: wrap;
    gap: 25px;
    justify-content: center;
}}

.col-container {{
    flex: 1;
    min-width: 300px;
    max-width: 400px;
}}
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'launched_app' not in st.session_state:
    st.session_state.launched_app = None

# --- Website Content ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Main Title
st.markdown('<h1 class="main-title">Finwise Capital</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666; font-size: 1.5em; margin-bottom: 40px;">AI-Driven Wealth Management & Portfolio Intelligence Platform</h2>', unsafe_allow_html=True)

# Main Description
st.markdown("""
    <div class="main-description">
    Finwise Capital is a Bangalore-based wealth management and financial advisory firm working with High Net Worth Individuals, 
    Family Offices, and Institutional Investors. Through its flagship platform Finwise IQ, the company delivers personalized 
    portfolio management, fund recommendations, risk profiling, and compliance reporting.
    <br><br>
    <strong>Finwise is now working on integrating Generative AI into its ecosystem</strong> — building intelligent assistants, 
    retrieval-based Q&A, and workflow automation to empower clients with smarter, data-driven portfolio insights 
    and a next-generation advisory experience.
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Section Header for AI Solutions
st.markdown('<h2 class="section-header">🚀 Explore Our AI-Powered Solutions</h2>', unsafe_allow_html=True)

# --- Data for the Blocks ---
blocks_data = [
    {
        "icon": "💬",
        "title": "Financial Chatbot with Memory",
        "description": "Engage in intelligent conversations about a wide range of financial topics. Our Financial Chatbot remembers your previous interactions, providing personalized and context-aware insights to help you navigate complex financial concepts and make informed decisions.",
        "link": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/"
    },
    {
        "icon": "🤖",
        "title": "Agentic Financial Assistant",
        "description": "Meet your dedicated Autonomous AI Agent, designed to streamline your financial tasks. This intelligent assistant excels at performing complex financial calculations, fetching real-time market data, and providing instant, accurate information to support your investment strategies.",
        "link": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/"
    },
    {
        "icon": "📊",
        "title": "AI-Powered PDF Insight Agent",
        "description": "Unlock the hidden insights within your financial documents. Our AI-Powered PDF Insight Agent enables you to upload various PDF files – from annual reports to compliance documents – and ask intelligent questions, instantly extracting key information and generating summaries to save you time and effort.",
        "link": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/"
    },
    {
        "icon": "🔍",
        "title": "Financial Data Question Answering System",
        "description": "Transform raw data into actionable intelligence. Our Financial Data Question Answering System allows you to interact with structured financial datasets using natural language queries, providing instant answers and insights without the need for complex database skills.",
        "link": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/"
    },
    {
        "icon": "📄",
        "title": "Financial Document Summarizer",
        "description": "Cut through the noise with our Financial Document Summarizer. Quickly condense lengthy financial reports, market analyses, or meeting transcripts into concise, digestible summaries, highlighting critical information and key takeaways for efficient decision-making.",
        "link": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/"
    }
]

# --- Display Blocks in a Grid Layout ---
st.markdown('<div class="row-container">', unsafe_allow_html=True)

for i, block in enumerate(blocks_data):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="col-container">
            <div class="block-container">
                <div class="block-icon">{block["icon"]}</div>
                <h3 class="block-title">{block["title"]}</h3>
                <p class="block-description">{block["description"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Working Launch Button
        if st.button(f"🚀 Launch {block['title']}", key=f"btn_{i}"):
            st.session_state.launched_app = block["title"]
            webbrowser.open_new_tab(block["link"])

# Show success message if an app was launched
if st.session_state.launched_app:
    st.markdown(f"""
    <div class="success-message">
        ✅ Opening {st.session_state.launched_app} in a new tab...
    </div>
    """, unsafe_allow_html=True)
    # Reset after showing message
    st.session_state.launched_app = None

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
    <div class="footer">
        <h3 style="color: #004d40; margin-bottom: 15px;">Finwise Capital</h3>
        <p style="margin-bottom: 10px;">Empowering your financial future with cutting-edge AI technology.</p>
        <p style="font-size: 0.9em; color: #888;">📍 Bangalore, India | 💼 Wealth Management & Financial Advisory</p>
        <p style="font-size: 0.9em; color: #888; margin-top: 15px;">© 2025 Finwise Capital. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
