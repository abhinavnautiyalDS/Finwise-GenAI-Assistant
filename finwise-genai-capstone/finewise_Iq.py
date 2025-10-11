import streamlit as st

# --- Page Configuration ---
# Sets the page title, icon, wide layout, and collapses the sidebar by default.
st.set_page_config(
    page_title="Finwise IQ | AI-Powered Wealth Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Styling ---
# Defines a clean, modern, and professional financial aesthetic.
primary_text_color = "#1a202c" # Soft black
secondary_accent_color = "#2563eb" # Professional blue for buttons/highlights
block_background_color = "#ffffff"
app_background_color = "#f7fafc" # Very light cool gray
border_color = "#e2e8f0"

st.markdown(f"""
<style>
/* Import Google Font for a more polished look */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="st-"] {{
    font-family: 'Inter', sans-serif;
    color: {primary_text_color};
    background-color: {app_background_color};
}}

/* Remove top padding from Streamlit main container */
.block-container.st-emotion-cache-1y4p8pa {{
    padding-top: 2rem;
}}

/* Main Title Styling */
h1 {{
    color: #0f172a; /* Darker shade for title */
    text-align: center;
    font-weight: 800;
    letter-spacing: -0.025em;
    font-size: 3rem;
    margin-bottom: 1.5rem;
}}

/* Main Description Styling */
.main-description p {{
    font-size: 1.125rem;
    line-height: 1.75;
    text-align: center;
    color: #4a5568; /* Softer gray for body text */
    max-width: 800px;
    margin: 0 auto 3rem auto;
}}

/* Section Header Styling */
h2 {{
    color: #0f172a;
    text-align: center;
    font-weight: 700;
    font-size: 2.25rem;
    margin-top: 1rem;
    margin-bottom: 3rem;
    letter-spacing: -0.025em;
}}

/* Custom separator */
.separator {{
    height: 1px;
    background: linear-gradient(to right, transparent, {border_color}, transparent);
    margin: 3rem 0;
}}

/* Card/Block Styling */
.solution-card {{
    background-color: {block_background_color};
    border: 1px solid {border_color};
    border-radius: 1rem;
    padding: 2rem;
    text-align: center;
    height: 100%;
    min-height: 420px; /* Fixed minimum height for alignment */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out, border-color 0.2s ease;
}}

.solution-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
    border-color: {secondary_accent_color};
}}

/* Card Image/Icon */
.card-icon {{
    width: 70px;
    height: 70px;
    margin-bottom: 1.5rem;
    object-fit: contain;
    padding: 10px;
    background-color: #eff6ff; /* Very light blue background for icon */
    border-radius: 50%; /* Circular icon background */
}}

/* Card Title */
.card-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1rem;
    min-height: 3rem; /* Ensure titles align even if some are longer */
    display: flex;
    align-items: center;
    justify-content: center;
}}

/* Card Description */
.card-description {{
    font-size: 0.95rem;
    line-height: 1.6;
    color: #64748b;
    margin-bottom: 2rem;
    flex-grow: 1;
}}

/* Launch Button */
.launch-button {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff !important;
    background-color: {secondary_accent_color};
    border-radius: 0.5rem;
    text-decoration: none !important;
    transition: background-color 0.2s;
    width: 100%; /* Full width button */
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}}

.launch-button:hover {{
    background-color: #1d4ed8; /* Darker blue */
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    color: #ffffff !important;
}}

/* Footer */
.footer {{
    text-align: center;
    margin-top: 5rem;
    padding: 2rem 0;
    border-top: 1px solid {border_color};
    color: #94a3b8;
    font-size: 0.875rem;
}}
</style>
""", unsafe_allow_html=True)

# --- Main Content ---

st.title("Finwise IQ | Working AI-Powered Wealth Intelligence Platform")

st.markdown("""
    <div class="main-description">
        <p>
        Finwise IQ is a working AI-powered wealth management platform that helps users analyze portfolios, assess risk, compare mutual funds, and generate compliance summaries. 
        It includes intelligent chatbots with memory, tool-using AI agents, document-based Q&A, SQL-powered financial queries, and smart summarization engines. 
        Finwise IQ also integrates graph-based analytics and automated workflows, delivering real-time, data-driven portfolio insights for investors and advisors.
        </p>
    </div>
""", unsafe_allow_html=True)

# Custom Separator
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

st.markdown("<h2>Explore Our AI-Powered Solutions</h2>", unsafe_allow_html=True)

# --- Data for the Blocks with Assigned Images ---
# Used reliable, clean, flat-style icons hosted publicly.
blocks_data = [
    {
        "title": "Financial Chatbot with Memory",
        "emoji": "🤖",
        "description": "Engage in intelligent conversations. Our Chatbot remembers previous interactions, providing personalized, context-aware insights to help navigate complex financial concepts.",
        "link": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/",
        # Image: A clean robot/chat icon
        "image_url": "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"
    },
    {
        "title": "Agentic Financial Assistant",
        "emoji": "⚙️",
        "description": "Your dedicated Autonomous AI Agent. It excels at performing complex financial calculations, fetching real-time market data, and support your investment strategies.",
        "link": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/",
        # Image: Cogs/Brain representing active processing/agent
        "image_url": "https://cdn-icons-png.flaticon.com/512/10473/10473667.png"
    },
    {
        "title": "AI-Powered PDF Insight Agent",
        "emoji": "📄",
        "description": "Unlock insights within financial documents. Upload annual reports or compliance docs and ask intelligent questions to instantly extract key information.",
        "link": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/",
        # Image: Document with a search loop
        "image_url": "https://cdn-icons-png.flaticon.com/512/3143/3143460.png"
    },
    {
        "title": "Financial Data Q&A System",
        "emoji": "📊",
        "description": "Interact with structured financial datasets using natural language. Get instant answers and insights from raw data without needing complex database skills.",
        "link": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/",
        # Image: Database/Chart icon
        "image_url": "https://cdn-icons-png.flaticon.com/512/2867/2867364.png"
    },
    {
        "title": "Financial Document Summarizer",
        "emoji": "📝",
        "description": "Cut through the noise. Quickly condense lengthy financial reports, market analyses, or meeting transcripts into concise, digestible summaries for efficient decisions.",
        "link": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/",
        # Image: Summarization/Notes icon
        "image_url": "https://cdn-icons-png.flaticon.com/512/4021/4021693.png"
    }
]

# --- Grid Layout ---
# Using a 3-column layout that wraps automatically based on the number of items.
num_cols = 3
cols = st.columns(num_cols)

for i, block in enumerate(blocks_data):
    col_index = i % num_cols
    with cols[col_index]:
        st.markdown(f"""
        <div class="solution-card">
            <div>
                <img src="{block['image_url']}" alt="{block['title']}" class="card-icon">
                <div class="card-title">{block['emoji']} {block['title']}</div>
                <p class="card-description">{block['description']}</p>
            </div>
            <a href="{block['link']}" target="_blank" class="launch-button">
                Launch Application &nbsp; 🚀
            </a>
        </div>
        """, unsafe_allow_html=True)

# Handle the empty slot if the number of blocks isn't perfectly divisible by columns
# to keep the layout neat (Optional, but good for visual balance).
if len(blocks_data) % num_cols != 0:
    remaining = num_cols - (len(blocks_data) % num_cols)
    for j in range(remaining):
        with cols[-(j+1)]:
            st.empty()

# --- Footer ---
st.markdown("""
    <div class="footer">
        <p><b>Finwise Capital</b> &mdash; Empowering your financial future with next-generation AI.</p>
        <p style="margin-top: 0.5rem;">&copy; 2025 Finwise Capital. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
