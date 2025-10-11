import streamlit as st
import webbrowser

# Page configuration
st.set_page_config(
    page_title="Finwise Capital | AI-Driven Wealth Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .app-block {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #e0e0e0;
        height: 100%;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .app-block:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .app-title {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    
    .app-description {
        color: #5d6d7e;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .app-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; font-weight: 700;">Finwise Capital</h1>
    <h2 style="font-size: 1.5rem; font-weight: 300; margin-bottom: 1rem;">AI-Driven Wealth Management & Portfolio Intelligence Platform</h2>
    <p style="font-size: 1.1rem; max-width: 800px; margin: 0 auto; opacity: 0.9;">
        Bangalore-based wealth management firm serving High Net Worth Individuals, Family Offices, and Institutional Investors. 
        Through Finwise IQ, we deliver personalized portfolio management, fund recommendations, risk profiling, and compliance reporting.
    </p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h3 style="color: #2c3e50; font-weight: 600;">🚀 Next-Generation AI Financial Ecosystem</h3>
    <p style="color: #5d6d7e; font-size: 1.1rem; max-width: 900px; margin: 0 auto;">
        Finwise is pioneering the integration of Generative AI into wealth management. Explore our suite of intelligent 
        assistants and AI-powered tools designed to empower you with smarter, data-driven portfolio insights and 
        transform your advisory experience.
    </p>
</div>
""", unsafe_allow_html=True)

# Application Blocks Data
apps = [
    {
        "icon": "💰",
        "title": "Financial Chatbot with Memory",
        "description": "Engage in intelligent conversations about financial markets, investment strategies, and portfolio analysis. Our advanced chatbot maintains context throughout your discussion, providing personalized financial guidance and insights.",
        "url": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/"
    },
    {
        "icon": "🤖",
        "title": "Agentic Financial Assistant",
        "description": "Leverage autonomous AI agents that perform complex financial calculations, fetch real-time market data, and execute sophisticated financial analysis tasks independently. Perfect for rapid financial modeling and data-driven decision making.",
        "url": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/"
    },
    {
        "icon": "📊",
        "title": "AI-Powered PDF Insight Agent",
        "description": "Transform lengthy financial documents into actionable intelligence. Upload PDFs of financial reports, compliance documents, or prospectuses and get instant answers to your specific questions with AI-powered document analysis.",
        "url": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/"
    },
    {
        "icon": "🔍",
        "title": "Financial Data Question Answering System",
        "description": "Query complex financial datasets using natural language. Our intelligent system understands your questions about financial data and provides accurate, data-backed answers without requiring technical expertise in data analysis.",
        "url": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/"
    },
    {
        "icon": "📄",
        "title": "Financial Document Summarizer",
        "description": "Quickly extract key insights from extensive financial documents, earnings reports, or meeting transcripts. Save time and focus on critical information with AI-powered summarization that captures essential financial metrics and highlights.",
        "url": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/"
    }
]

# Create columns for the app blocks
cols = st.columns(3)

# Track which app was launched
if 'launched_app' not in st.session_state:
    st.session_state.launched_app = None

for idx, app in enumerate(apps):
    with cols[idx % 3]:
        # Create the app block
        st.markdown(f"""
        <div class="app-block">
            <div class="app-icon">{app['icon']}</div>
            <div class="app-title">{app['title']}</div>
            <div class="app-description">{app['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create launch button
        if st.button(f"🚀 Launch {app['title']}", key=f"btn_{idx}"):
            st.session_state.launched_app = app['title']
            webbrowser.open_new_tab(app['url'])

# Show success message if an app was launched
if st.session_state.launched_app:
    st.success(f"✅ Opening {st.session_state.launched_app} in a new tab...")
    # Reset after showing message
    st.session_state.launched_app = None

# Alternative method using markdown with JavaScript
st.markdown("---")
st.markdown("### 🔗 Quick Links (Alternative)")
st.markdown("You can also use these direct links:")

for app in apps:
    st.markdown(f"- [{app['icon']} {app['title']}]({app['url']})")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
    <h4 style="color: #2c3e50; margin-bottom: 1rem;">Ready to Transform Your Financial Advisory Experience?</h4>
    <p style="color: #5d6d7e; margin-bottom: 1.5rem;">
        Contact us to learn more about our AI-powered wealth management solutions and how Finwise IQ can elevate your investment strategy.
    </p>
    <div style="color: #667eea; font-weight: 600;">
        📍 Bangalore, India | 💼 Wealth Management & Financial Advisory
    </div>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("ℹ️ How to use this platform"):
    st.markdown("""
    ### Getting Started
    
    1. **Browse Applications**: Explore our AI-powered financial tools in the main section
    2. **Launch Tools**: Click the "Launch" buttons to open any application in a new tab
    3. **Allow Pop-ups**: Make sure your browser allows pop-ups for this site
    
    ### Troubleshooting
    - If buttons don't work, check if your browser is blocking pop-ups
    - Use the quick links section as an alternative
    - All applications open in new browser tabs
    
    ### Supported Applications
    - All applications are live Streamlit apps
    - No login required for demo access
    - Each tool is designed for specific financial use cases
    """)
