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
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #e0e0e0;
        height: 100%;
        cursor: pointer;
    }
    
    .app-block:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .app-title {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    .app-description {
        color: #5d6d7e;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .app-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .image-placeholder {
        background: linear-gradient(45deg, #f0f2f5, #e1e8ed);
        height: 120px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        color: #7d8b99;
        font-weight: 600;
    }
    
    .click-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    
    .click-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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
        "url": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/",
        "image_alt": "AI Financial Chatbot Interface"
    },
    {
        "icon": "🤖",
        "title": "Agentic Financial Assistant",
        "description": "Leverage autonomous AI agents that perform complex financial calculations, fetch real-time market data, and execute sophisticated financial analysis tasks independently. Perfect for rapid financial modeling and data-driven decision making.",
        "url": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/",
        "image_alt": "Autonomous Financial Agent Dashboard"
    },
    {
        "icon": "📊",
        "title": "AI-Powered PDF Insight Agent",
        "description": "Transform lengthy financial documents into actionable intelligence. Upload PDFs of financial reports, compliance documents, or prospectuses and get instant answers to your specific questions with AI-powered document analysis.",
        "url": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/",
        "image_alt": "PDF Document Analysis Interface"
    },
    {
        "icon": "🔍",
        "title": "Financial Data Q&A System",
        "description": "Query complex financial datasets using natural language. Our intelligent system understands your questions about financial data and provides accurate, data-backed answers without requiring technical expertise in data analysis.",
        "url": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/",
        "image_alt": "Financial Data Query System"
    },
    {
        "icon": "📄",
        "title": "Financial Document Summarizer",
        "description": "Quickly extract key insights from extensive financial documents, earnings reports, or meeting transcripts. Save time and focus on critical information with AI-powered summarization that captures essential financial metrics and highlights.",
        "url": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/",
        "image_alt": "Document Summarization Tool"
    }
]

# Create columns for the app blocks
cols = st.columns(3)

for idx, app in enumerate(apps):
    with cols[idx % 3]:
        # Create container for the app block
        with st.container():
            st.markdown(f"""
            <div class="app-block">
                <div class="app-icon">{app['icon']}</div>
                <div class="app-title">{app['title']}</div>
                <div class="image-placeholder">
                    {app['image_alt']}
                </div>
                <div class="app-description">{app['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add clickable button that opens the URL
            if st.button(f"Launch {app['icon']} {app['title']}", key=f"btn_{idx}", use_container_width=True):
                webbrowser.open_new_tab(app['url'])

# Spacing
st.markdown("<br><br>", unsafe_allow_html=True)

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

# Alternative method using markdown links (commented out)
st.markdown("""
<style>
    .app-link {
        text-decoration: none;
        color: inherit;
    }
    .app-link:hover {
        text-decoration: none;
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

# You can also use this alternative approach - uncomment to try:
"""
# Alternative approach using markdown links (for reference)
for idx, app in enumerate(apps):
    with cols[idx % 3]:
        st.markdown(f'''
        <a href="{app['url']}" target="_blank" class="app-link">
            <div class="app-block">
                <div class="app-icon">{app['icon']}</div>
                <div class="app-title">{app['title']}</div>
                <div class="image-placeholder">
                    {app['image_alt']}
                </div>
                <div class="app-description">{app['description']}</div>
                <div style="text-align: center; margin-top: 1rem;">
                    <button class="click-button">Launch Application</button>
                </div>
            </div>
        </a>
        ''', unsafe_allow_html=True)
"""
