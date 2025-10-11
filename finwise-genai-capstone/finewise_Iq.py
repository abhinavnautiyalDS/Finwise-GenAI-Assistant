import streamlit as st
import requests
from PIL import Image
import io

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
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; font-weight: 700;">Finwise Capital</h1>
    <h2 style="font-size: 1.5rem; font-weight: 300; margin-bottom: 1rem;">AI-Driven Wealth Management & Portfolio Intelligence Platform</h2>
    <p style="font-size: 1.1rem; max-width: 800px; margin: 0 auto; opacity: 0.9;">
        Finwise IQ is a working AI-powered wealth management platform that helps users analyze portfolios, assess risk, compare mutual funds, and generate compliance summaries. 
        It includes intelligent chatbots with memory, tool-using AI agents, document-based Q&A, SQL-powered financial queries, and smart summarization engines. 
        Finwise IQ also integrates graph-based analytics and automated workflows, delivering real-time, data-driven portfolio insights for investors and advisors..
    </p>
</div>
""", unsafe_allow_html=True)

# Introduction
# st.markdown("""
# <div style="text-align: center; margin-bottom: 3rem;">
#     <h3 style="color: #2c3e50; font-weight: 600;">🚀 Next-Generation AI Financial Ecosystem</h3>
#     <p style="color: #5d6d7e; font-size: 1.1rem; max-width: 900px; margin: 0 auto;">
#         Finwise is pioneering the integration of Generative AI into wealth management. Explore our suite of intelligent 
#         assistants and AI-powered tools designed to empower you with smarter, data-driven portfolio insights and 
#         transform your advisory experience.
#     </p>
# </div>
# """, unsafe_allow_html=True)

# Application Blocks
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
        # Create clickable block
        if st.markdown(f"""
        <div class="app-block" onclick="window.open('{app['url']}', '_blank')">
            <div class="app-icon">{app['icon']}</div>
            <div class="app-title">{app['title']}</div>
            <div class="image-placeholder">
                {app['image_alt']}
            </div>
            <div class="app-description">{app['description']}</div>
        </div>
        """, unsafe_allow_html=True):
            pass

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

# JavaScript to make entire blocks clickable
st.markdown("""
<script>
    // Make all app blocks clickable
    document.querySelectorAll('.app-block').forEach(block => {
        block.style.cursor = 'pointer';
    });
</script>
""", unsafe_allow_html=True)
