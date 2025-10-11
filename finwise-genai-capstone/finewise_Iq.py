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
        margin-bottom: 1rem;
    }
    
    .app-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .image-container {
        height: 150px;
        border-radius: 8px;
        margin-bottom: 1rem;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(45deg, #f0f2f5, #e1e8ed);
    }
    
    .app-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .image-placeholder {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #7d8b99;
        font-weight: 600;
        text-align: center;
        padding: 1rem;
    }
    
    .launch-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .launch-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
        border: 1px solid #c3e6cb;
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

# Application Blocks Data with Image URLs
apps = [
    {
        "icon": "💰",
        "title": "Financial Chatbot with Memory",
        "description": "Engage in intelligent conversations about financial markets, investment strategies, and portfolio analysis. Our advanced chatbot maintains context throughout your discussion, providing personalized financial guidance and insights.",
        "url": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "image_alt": "AI Financial Chatbot Interface"
    },
    {
        "icon": "🤖",
        "title": "Agentic Financial Assistant",
        "description": "Leverage autonomous AI agents that perform complex financial calculations, fetch real-time market data, and execute sophisticated financial analysis tasks independently. Perfect for rapid financial modeling and data-driven decision making.",
        "url": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/",
        "image_url": "https://images.unsplash.com/photo-1665686374006-b8f04cf62d57?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "image_alt": "Autonomous Financial Agent Dashboard"
    },
    {
        "icon": "📊",
        "title": "AI-Powered PDF Insight Agent",
        "description": "Transform lengthy financial documents into actionable intelligence. Upload PDFs of financial reports, compliance documents, or prospectuses and get instant answers to your specific questions with AI-powered document analysis.",
        "url": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "image_alt": "PDF Document Analysis Interface"
    },
    {
        "icon": "🔍",
        "title": "Financial Data Question Answering System",
        "description": "Query complex financial datasets using natural language. Our intelligent system understands your questions about financial data and provides accurate, data-backed answers without requiring technical expertise in data analysis.",
        "url": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "image_alt": "Financial Data Query System"
    },
    {
        "icon": "📄",
        "title": "Financial Document Summarizer",
        "description": "Quickly extract key insights from extensive financial documents, earnings reports, or meeting transcripts. Save time and focus on critical information with AI-powered summarization that captures essential financial metrics and highlights.",
        "url": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/",
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "image_alt": "Document Summarization Tool"
    }
]

# Image Management Section (Admin Panel)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🖼️ Image Management")
st.sidebar.markdown("Update image URLs for each application:")

# Create a dictionary to store updated image URLs
updated_images = {}

for i, app in enumerate(apps):
    st.sidebar.markdown(f"**{app['icon']} {app['title']}**")
    new_image_url = st.sidebar.text_input(
        f"Image URL for {app['title']}",
        value=app['image_url'],
        key=f"image_url_{i}",
        placeholder="Enter image URL here..."
    )
    updated_images[i] = new_image_url

# Apply image updates
for i, new_url in updated_images.items():
    if new_url and new_url != apps[i]['image_url']:
        apps[i]['image_url'] = new_url

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
                <div class="image-container">
            """, unsafe_allow_html=True)
            
            # Display image or placeholder
            if app.get('image_url') and app['image_url'].startswith(('http://', 'https://')):
                st.markdown(f'<img src="{app["image_url"]}" class="app-image" alt="{app["image_alt"]}">', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="image-placeholder">📷 {app["image_alt"]}<br><small>Add image URL in sidebar</small></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                </div>
                <div class="app-description">{app['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add clickable button that opens the URL
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"🚀 Launch {app['icon']}", key=f"btn_{idx}", use_container_width=True):
                    webbrowser.open_new_tab(app['url'])
                    st.markdown(f'<div class="success-message">Opening {app["title"]}...</div>', unsafe_allow_html=True)

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

# Instructions
with st.expander("ℹ️ How to use this platform"):
    st.markdown("""
    ### Getting Started
    
    1. **Browse Applications**: Explore our AI-powered financial tools in the main section
    2. **Launch Tools**: Click the "Launch" buttons to open any application in a new tab
    3. **Customize Images**: Use the sidebar to update image URLs for each application
    
    ### Image Management
    - Use the sidebar to add or update image URLs
    - Images should be direct URLs (ending with .jpg, .png, etc.)
    - Recommended size: 1000x600 pixels for best display
    - Changes apply immediately
    
    ### Supported Applications
    - All applications open in new browser tabs
    - No login required for demo access
    - Each tool is designed for specific financial use cases
    """)

# JavaScript for better button feedback
st.markdown("""
<script>
// Add click animation to buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('launch-btn')) {
        e.target.style.transform = 'scale(0.95)';
        setTimeout(() => {
            e.target.style.transform = '';
        }, 150);
    }
});
</script>
""", unsafe_allow_html=True)
