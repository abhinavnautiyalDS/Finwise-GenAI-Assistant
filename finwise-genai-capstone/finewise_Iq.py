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
# This block defines the visual style of the website using CSS.
# It ensures a cohesive and modern look, including responsive design elements.
primary_color = "#004d40" # A dark teal, often associated with finance/trust
secondary_color = "#007BFF" # A standard blue for interactive elements like buttons

st.markdown(f"""
<style>
/* General body and Streamlit app styling */
html, body, .stApp {{
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #333333;
    background-color: #f8f9fa; /* Lighter background for the entire app */
}}

/* Main Title Styling */
h1 {{
    color: {primary_color};
    text-align: center;
    font-size: 2.8em; /* Larger title font size */
    margin-bottom: 20px;
    padding-top: 20px;
}}

/* Section Header Styling */
h2 {{
    color: {primary_color};
    text-align: center;
    font-size: 2em;
    margin-top: 40px;
    margin-bottom: 30px;
}}

/* Main Description Styling */
.stMarkdown p {{
    font-size: 1.1em;
    line-height: 1.6;
    text-align: center; /* Center-aligns the main description */
    max-width: 850px; /* Limits width for better readability */
    margin: auto; /* Centers the description block */
    padding-bottom: 30px;
    color: #444444;
}}

/* Horizontal Rule Styling */
hr {{
    border-top: 1px solid #e0e0e0;
    margin-top: 40px;
    margin-bottom: 40px;
}}

/* Individual Block Container Styling */
.block-container {{
    background-color: #ffffff; /* White background for each solution block */
    border-radius: 12px; /* Rounded corners */
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1); /* Soft shadow for depth */
    transition: all 0.3s ease-in-out; /* Smooth transition for hover effects */
    text-align: center;
    min-height: 380px; /* Ensures all blocks have a consistent height */
    display: flex;
    flex-direction: column;
    justify-content: space-between; /* Distributes space between items */
    align-items: center; /* Centers items horizontally */
    border: 1px solid #e0e0e0; /* Subtle border */
}}

.block-container:hover {{
    box-shadow: 0 10px 25px rgba(0,0,0,0.15); /* Enhanced shadow on hover */
    transform: translateY(-8px); /* Lifts the block slightly on hover */
    border-color: {secondary_color}; /* Changes border color on hover */
}}

/* Block Title Styling */
.block-title {{
    font-size: 1.6em;
    font-weight: 600; /* Semi-bold */
    color: {primary_color};
    margin-bottom: 15px;
}}

/* Block Description Styling */
.block-description {{
    font-size: 0.98em;
    color: #555555;
    flex-grow: 1; /* Allows description to take up available space */
    line-height: 1.5;
    margin-bottom: 20px;
}}

/* Block Image Styling */
.block-image {{
    width: 120px; /* Fixed width for images */
    height: 120px; /* Fixed height for images */
    object-fit: contain; /* Ensures the image fits without cropping */
    margin-bottom: 20px;
    border-radius: 8px; /* Slightly rounded corners for images */
    border: 1px solid #f0f0f0; /* Light border around image */
}}

/* Redirect Button Styling */
.redirect-button {{
    display: inline-block;
    padding: 12px 25px;
    background-color: {secondary_color}; /* Blue button background */
    color: white !important; /* Ensures text is white, overriding default link color */
    text-align: center;
    text-decoration: none !important; /* Removes underline from link */
    font-size: 1.05em;
    font-weight: 500;
    border-radius: 8px;
    transition: background-color 0.3s ease, transform 0.2s ease;
    cursor: pointer;
    border: none;
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2); /* Soft shadow for button */
}}

.redirect-button:hover {{
    background-color: #0056b3; /* Darker blue on hover */
    transform: translateY(-2px); /* Slight lift on hover */
    box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3); /* Enhanced shadow on hover */
}}

/* Footer Styling */
.footer {{
    text-align: center;
    margin-top: 50px;
    padding: 20px;
    color: #888888;
    font-size: 0.9em;
    border-top: 1px solid #eeeeee;
}}
</style>
""", unsafe_allow_html=True)


# --- Website Content ---

# Main Title
st.title("Finwise Capital | AI-Driven Wealth Management & Portfolio Intelligence Platform")

# Main Description
st.markdown("""
    <p>
    Finwise Capital is a Bangalore-based wealth management and financial advisory firm working with High Net Worth Individuals, 
    Family Offices, and Institutional Investors. Through its flagship platform Finwise IQ, the company delivers personalized 
    portfolio management, fund recommendations, risk profiling, and compliance reporting. 
    <br><br>
    Finwise is now working on integrating Generative AI into its ecosystem — building intelligent assistants, 
    retrieval-based Q&A, and workflow automation to empower clients with smarter, data-driven portfolio insights 
    and a next-generation advisory experience.
    </p>
""", unsafe_allow_html=True)

st.markdown("---") # Horizontal separator

# Section Header for AI Solutions
st.header("Explore Our AI-Powered Solutions")

# --- Data for the Blocks ---
# Each dictionary represents a block with its title, enhanced description,
# the link to redirect to, and the local filename for its image.
blocks_data = [
    {
        "title": "💰 Financial Chatbot with Memory",
        "description": "Engage in intelligent conversations about a wide range of financial topics. Our Financial Chatbot remembers your previous interactions, providing personalized and context-aware insights to help you navigate complex financial concepts and make informed decisions.",
        "link": "https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/",
        "image_filename": "images/chatbot.png" # Placeholder filename
    },
    {
        "title": "💰 Agentic Financial Assistant",
        "description": "Meet your dedicated Autonomous AI Agent, designed to streamline your financial tasks. This intelligent assistant excels at performing complex financial calculations, fetching real-time market data, and providing instant, accurate information to support your investment strategies.",
        "link": "https://finwise-genai-assistant-em7uzkajvqedkpcyhctgq8.streamlit.app/",
        "image_filename": "images/agent.png" # Placeholder filename
    },
    {
        "title": "🚀 AI-Powered PDF Insight Agent",
        "description": "Unlock the hidden insights within your financial documents. Our AI-Powered PDF Insight Agent enables you to upload various PDF files – from annual reports to compliance documents – and ask intelligent questions, instantly extracting key information and generating summaries to save you time and effort.",
        "link": "https://finwise-genai-assistant-ntajccym3nyh469d8qkppq.streamlit.app/",
        "image_filename": "images/pdf_insight.png" # Placeholder filename
    },
    {
        "title": "💰 Financial Data Question Answering System",
        "description": "Transform raw data into actionable intelligence. Our Financial Data Question Answering System allows you to interact with structured financial datasets using natural language queries, providing instant answers and insights without the need for complex database skills.",
        "link": "https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/",
        "image_filename": "images/data_qa.png" # Placeholder filename
    },
    {
        "title": "💼 Financial Document Summarizer",
        "description": "Cut through the noise with our Financial Document Summarizer. Quickly condense lengthy financial reports, market analyses, or meeting transcripts into concise, digestible summaries, highlighting critical information and key takeaways for efficient decision-making.",
        "link": "https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/",
        "image_filename": "images/summarizer.png" # Placeholder filename
    }
]

# --- Display Blocks in a Grid Layout ---
# Uses Streamlit columns to arrange blocks, showing 3 blocks per row.
cols = st.columns(3) # Create 3 columns for a responsive grid

for i, block in enumerate(blocks_data):
    with cols[i % 3]: # Cycle through the columns (0, 1, 2, then back to 0 for the next row)
        # Each block is rendered as a custom HTML `div` using st.markdown.
        # This allows for rich styling and direct integration of the redirect link.
        st.markdown(f"""
        <div class="block-container">
            <h3 class="block-title">{block["title"]}</h3>
            <img src="{block["image_filename"]}" alt="{block["title"]} Image" class="block-image">
            <!-- 
            IMPORTANT: For images to display, ensure you have an 'images' folder 
            in the same directory as this Streamlit script. 
            Place your image files (e.g., chatbot.png, agent.png) inside it.
            Alternatively, replace 'images/filename.png' with a direct URL to your hosted images.
            -->
            <p class="block-description">{block["description"]}</p>
            <a href="{block["link"]}" target="_blank" class="redirect-button">Launch Application</a>
        </div>
        """, unsafe_allow_html=True) # unsafe_allow_html is necessary to render custom HTML/CSS

# --- Footer ---
st.markdown("""
    <div class="footer">
        <p>Finwise Capital - Empowering your financial future with AI.</p>
        <p>© 2025 Finwise Capital. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
