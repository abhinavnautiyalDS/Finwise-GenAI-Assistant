import streamlit as st

# --- Page Configuration ---
# Sets the page title, icon, wide layout, and collapses the sidebar by default.
st.set_page_config(
    page_title="Finwise Capital | AI-Driven Wealth Management",
    page_icon="💰", # A money bag emoji for the browser tab icon
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Styling ---
# This block defines the visual style of the website using CSS, focusing on
# clean typography, subtle shadows, and a modern color palette to match the image.
primary_text_color = "#212529" # Very dark grey, almost black, for main text/titles
secondary_accent_color = "#007BFF" # A standard blue for interactive elements like buttons
light_background_color = "#ffffff" # White for solution block backgrounds
app_background_color = "#f8f9fa" # Off-white for the overall app background
border_line_color = "#e9ecef" # Light grey for subtle borders and separators

st.markdown(f"""
<style>
/* General body and Streamlit app styling */
html, body, .stApp {{
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; /* Added Inter for a modern look */
    color: {primary_text_color};
    background-color: {app_background_color};
    -webkit-font-smoothing: antialiased; /* Smoother font rendering */
    -moz-osx-font-smoothing: grayscale;
}}

/* Main Title Styling */
h1 {{
    color: {primary_text_color};
    text-align: center;
    font-size: 3.2em; /* Slightly larger and bolder title */
    margin-bottom: 25px;
    padding-top: 30px;
    font-weight: 700;
    line-height: 1.2;
}}

/* Section Header Styling - specifically for "Explore Our AI-Powered Solutions" */
.stMarkdown h2 {{ /* Targeting Streamlit's h2 elements rendered via st.markdown */
    color: {primary_text_color};
    text-align: center;
    font-size: 2.2em; /* Larger section header */
    margin-top: 50px;
    margin-bottom: 40px;
    font-weight: 600;
}}

/* Main Description Styling */
.stMarkdown p {{
    font-size: 1.15em; /* Slightly larger description text for readability */
    line-height: 1.7;
    text-align: center;
    max-width: 900px; /* Optimal width for readability */
    margin: auto; /* Centers the description block */
    padding-bottom: 40px;
    color: #495057; /* Slightly softer dark grey for body text */
}}

/* Horizontal Rule Styling */
hr {{
    border-top: 1px solid {border_line_color};
    margin-top: 40px;
    margin-bottom: 40px;
    opacity: 0.7; /* Make separator less prominent */
}}

/* Individual Block Container Styling (for each AI solution card) */
.block-container {{
    background-color: {light_background_color};
    border-radius: 12px;
    padding: 30px; /* Generous internal padding */
    margin-bottom: 25px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05); /* Soft, subtle shadow for depth */
    transition: all 0.3s ease-in-out; /* Smooth transitions for hover effects */
    text-align: center;
    min-height: 400px; /* Ensures all blocks have a consistent, appealing height */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* Distributes space between title, image, description, button */
    align-items: center; /* Centers content horizontally within the block */
    border: 1px solid {border_line_color}; /* Very light border */
}}

.block-container:hover {{
    box-shadow: 0 8px 20px rgba(0,0,0,0.1); /* Enhanced shadow on hover */
    transform: translateY(-5px); /* Lifts the block slightly on hover */
    border-color: {secondary_accent_color}; /* Changes border color on hover */
}}

/* Block Title Styling */
.block-title {{
    font-size: 1.7em;
    font-weight: 600;
    color: {primary_text_color};
    margin-bottom: 18px;
    line-height: 1.3;
}}

/* Block Description Styling */
.block-description {{
    font-size: 1.0em;
    color: #555555;
    flex-grow: 1; /* Allows description to take up available space, pushing button down */
    line-height: 1.6;
    margin-bottom: 25px; /* Space above the button */
}}

/* Block Image Styling (for the iconic images) */
.block-image {{
    width: 80px; /* Smaller, iconic size for images */
    height: 80px;
    object-fit: contain; /* Ensures the image fits without cropping */
    margin-bottom: 20px;
    border-radius: 8px; /* Slightly rounded corners for consistency */
    /* No border on images to make them blend better as icons */
}}

/* Redirect Button Styling */
.redirect-button {{
    display: inline-block;
    padding: 13px 30px; /* Slightly larger button for better clickability */
    background-color: {secondary_accent_color};
    color: white !important; /* Ensures text is white, overriding default link color */
    text-align: center;
    text-decoration: none !important; /* Removes underline from link */
    font-size: 1.05em;
    font-weight: 500;
    border-radius: 8px;
    transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    cursor: pointer;
    border: none;
    box-shadow: 0 3px 6px rgba(0, 123, 255, 0.2); /* Subtle shadow for the button */
}}

.redirect-button:hover {{
    background-color: #0056b3; /* Darker blue on hover */
    transform: translateY(-2px); /* Slight lift on hover */
    box-shadow: 0 5px 10px rgba(0, 123, 255, 0.3); /* Enhanced shadow on hover */
}}

/* Footer Styling */
.footer {{
    text-align: center;
    margin-top: 60px; /* More space above footer */
    padding: 30px;
    color: #888888;
    font-size: 0.9em;
    border-top: 1px solid {border_line_color};
}}
</style>
""", unsafe_allow_html=True)


# --- Website Content ---

# Main Title
st.title("Finwise IQ | Working AI-Powered Wealth Intelligence Platform")

# Main Description
st.markdown("""
    <p>
    Finwise IQ is a working AI-powered wealth management platform that helps users analyze portfolios, assess risk, compare mutual funds, and generate compliance summaries. 
    It includes intelligent chatbots with memory, tool-using AI agents, document-based Q&A, SQL-powered financial queries, and smart summarization engines. 
    Finwise IQ also integrates graph-based analytics and automated workflows, delivering real-time, data-driven portfolio insights for investors and advisors.
    </p>
""", unsafe_allow_html=True)

st.markdown("---") # Horizontal separator for visual division

# Section Header for AI Solutions - Using markdown for flexible centering
st.markdown("<h2>Explore Our AI-Powered Solutions</h2>", unsafe_allow_html=True)

# --- Data for the Blocks ---
# Each dictionary represents a block with its title, enhanced description,
# the link to redirect to, and the local filename for its image.
blocks_data = [
    {
        "title": "💰 Financial Chatbot with Memory",
        "description": "Engage in intelligent conversations about a wide range of financial topics. Our Financial Chatbot remembers your previous interactions, providing personalized and context-aware insights to help you navigate complex financial concepts and make informed decisions.",
        "link": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/",
        "image_filename": "image (6).jpg" # Path to your chatbot image (e.g., a speech bubble or money bag icon)
    },
    {
        "title": "💰 Agentic Financial Assistant",
        "description": "Meet your dedicated Autonomous AI Agent, designed to streamline your financial tasks. This intelligent assistant excels at performing complex financial calculations, fetching real-time market data, and providing instant, accurate information to support your investment strategies.",
        "link": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/",
        "image_filename": "images/agent.png" # Path to your agent image (e.g., a robot or assistant icon)
    },
    {
        "title": "🚀 AI-Powered PDF Insight Agent",
        "description": "Unlock the hidden insights within your financial documents. Our AI-Powered PDF Insight Agent enables you to upload various PDF files – from annual reports to compliance documents – and ask intelligent questions, instantly extracting key information and generating summaries to save you time and effort.",
        "link": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/",
        "image_filename": "images/pdf_insight.png" # Path to your PDF insight image (e.g., a rocket with a document)
    },
    {
        "title": "💰 Financial Data Question Answering System",
        "description": "Transform raw data into actionable intelligence. Our Financial Data Question Answering System allows you to interact with structured financial datasets using natural language queries, providing instant answers and insights without the need for complex database skills.",
        "link": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/",
        "image_filename": "images/data_qa.png" # Path to your data QA image (e.g., a database or question icon)
    },
    {
        "title": "💼 Financial Document Summarizer",
        "description": "Cut through the noise with our Financial Document Summarizer. Quickly condense lengthy financial reports, market analyses, or meeting transcripts into concise, digestible summaries, highlighting critical information and key takeaways for efficient decision-making.",
        "link": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/",
        "image_filename": "images/summarizer.png" # Path to your summarizer image (e.g., a document with a magnifying glass)
    }
]

# --- Display Blocks in a Grid Layout ---
# Uses Streamlit columns to arrange blocks, showing 3 blocks per row,
# ensuring a responsive and visually appealing grid.
cols = st.columns(3) # Create 3 columns for a clean grid layout

for i, block in enumerate(blocks_data):
    with cols[i % 3]: # Cycle through the columns (0, 1, 2, then back to 0 for the next row)
        # Each block is rendered as a custom HTML `div` using st.markdown.
        # This allows for rich styling and direct integration of the redirect link.
        st.markdown(f"""
        <div class="block-container">
            <h3 class="block-title">{block["title"]}</h3>
            <img src="{block["image_filename"]}" alt="{block["title"]} Image" class="block-image">
            <p class="block-description">{block["description"]}</p>
            <a href="{block["link"]}" target="_blank" class="redirect-button">Launch Application</a>
        </div>
        """, unsafe_allow_html=True) # `unsafe_allow_html` is necessary to render custom HTML/CSS

# --- Footer ---
st.markdown("""
    <div class="footer">
        <p>Finwise Capital - Empowering your financial future with AI.</p>
        <p>© 2025 Finwise Capital. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
