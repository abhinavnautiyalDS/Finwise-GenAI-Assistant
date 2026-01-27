import os
import tempfile
import streamlit as st
import google.generativeai as genai
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide"
)

# ============================
# Custom CSS
# ============================
st.markdown("""
<style>
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 8px;
    }
    .summary-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Function to Initialize Gemini
# ============================
def initialize_gemini():
    """Initialize Gemini API with proper error handling"""
    try:
        # Get API key from secrets
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True, "Gemini API configured successfully"
    except KeyError:
        return False, "GOOGLE_API_KEY not found in Streamlit secrets"
    except Exception as e:
        return False, f"API configuration error: {str(e)}"

# ============================
# Function to List Available Models
# ============================
@st.cache_data
def get_available_models():
    """Get list of available Gemini models"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if "generateContent" in model.supported_generation_methods:
                available_models.append(model.name)
        return available_models
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

# ============================
# Function to Initialize Model
# ============================
def get_gemini_model(model_name="gemini-1.5-flash-latest"):
    """Get Gemini model instance"""
    try:
        model = genai.GenerativeModel(model_name)
        return model, None
    except Exception as e:
        return None, str(e)

# ============================
# Initialize API
# ============================
st.sidebar.title("🔧 Configuration")

# Check API status
api_status, api_message = initialize_gemini()
if api_status:
    st.sidebar.success(api_message)
else:
    st.sidebar.error(api_message)
    st.error(f"API Error: {api_message}")
    st.info("""
    **To get a FREE Gemini API key:**
    1. Visit https://makersuite.google.com/app/apikey
    2. Sign in with Google account
    3. Create a new API key
    4. Add to Streamlit secrets as `GOOGLE_API_KEY`
    """)
    st.stop()

# ============================
# Get Available Models
# ============================
available_models = get_available_models()

# Filter for free Gemini models (commonly available in free tier)
free_models = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest", 
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.0-pro"
]

# Show only models that are actually available
valid_models = [model for model in free_models if any(m for m in available_models if model in m)]

if not valid_models:
    st.error("No Gemini models available. Check your API key and permissions.")
    st.stop()

# ============================
# Model Selection
# ============================
st.sidebar.subheader("Model Selection")
selected_model = st.sidebar.selectbox(
    "Choose Gemini Model",
    options=valid_models,
    index=0,
    help="gemini-1.5-flash-latest is fastest and free"
)

# ============================
# Model Info
# ============================
st.sidebar.markdown("""
<div class="info-box">
<strong>Free Tier Limits:</strong><br>
• 60 requests per minute<br>
• 1M tokens per month<br>
• More than enough for regular use
</div>
""", unsafe_allow_html=True)

# ============================
# Summarization Settings
# ============================
st.sidebar.subheader("Summarization Settings")

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Lower = more factual, Higher = more creative"
)

max_tokens = st.sidebar.slider(
    "Max Summary Length",
    min_value=100,
    max_value=2000,
    value=500,
    step=100,
    help="Maximum tokens in summary"
)

# ============================
# Initialize Model
# ============================
model, model_error = get_gemini_model(selected_model)
if model_error:
    st.error(f"Model initialization failed: {model_error}")
    # Try fallback model
    fallback_model = "gemini-1.0-pro" if "gemini-1.0-pro" in valid_models else valid_models[-1]
    st.info(f"Trying fallback model: {fallback_model}")
    model, model_error = get_gemini_model(fallback_model)
    if model_error:
        st.error(f"Fallback also failed: {model_error}")
        st.stop()

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except ImportError:
        return "ERROR: Please install pypdf"
    except Exception as e:
        return f"ERROR: {str(e)}"

def process_files(uploaded_files):
    """Process uploaded files"""
    all_text = ""
    file_details = []
    
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(temp_path)
                file_type = "PDF"
            elif uploaded_file.type == "text/plain":
                with open(temp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                file_type = "TXT"
            else:
                st.warning(f"Unsupported file: {uploaded_file.name}")
                continue
            
            if text and not text.startswith("ERROR"):
                all_text += f"\n\n{'='*50}\nFile: {uploaded_file.name}\n{'='*50}\n\n{text}"
                file_details.append({
                    "name": uploaded_file.name,
                    "type": file_type,
                    "size": len(text)
                })
                st.success(f"✅ Processed: {uploaded_file.name}")
            else:
                st.error(f"Failed: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text, file_details

# ============================
# Summarization Function
# ============================
def generate_summary(text, model_instance):
    """Generate summary using Gemini"""
    
    # Truncate if too long
    if len(text) > 20000:
        text = text[:20000]
        st.warning("Text truncated to 20,000 characters")
    
    try:
        prompt = f"""You are an expert document summarizer. Please provide a concise and accurate summary of the following document(s).

Focus on:
1. Key points and main ideas
2. Important facts and figures
3. Conclusions and recommendations
4. Critical insights

Document Content:
{text}

Please provide a well-structured summary that captures the essence of the document(s):"""
        
        response = model_instance.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        return response.text
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# ============================
# Main App
# ============================
st.title("📄 Document Summarizer")
st.markdown("Upload documents for AI-powered summarization using **Google Gemini (Free Tier)**")

# File upload
uploaded_files = st.file_uploader(
    "Choose PDF or TXT files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Multiple files will be combined"
)

if uploaded_files:
    # Process files
    with st.spinner("Processing files..."):
        text, file_details = process_files(uploaded_files)
    
    if text and len(text) > 100:
        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files", len(file_details))
        with col2:
            st.metric("Characters", f"{len(text):,}")
        with col3:
            st.metric("Words", f"{len(text.split()):,}")
        
        # Preview
        with st.expander("📋 Preview Text"):
            st.text(text[:1500] + "..." if len(text) > 1500 else text)
        
        # Generate summary
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            with st.spinner("Generating summary with Gemini..."):
                summary = generate_summary(text, model)
            
            if summary and not summary.startswith("Error"):
                st.subheader("📋 Summary")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Download
                st.download_button(
                    "💾 Download Summary",
                    summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.error(summary)
    else:
        st.error("Could not extract text")
else:
    st.info("👆 Upload files to begin")

# ============================
# Footer
# ============================
st.markdown("---")
with st.expander("ℹ️ Setup Instructions"):
    st.markdown("""
    ### **Requirements.txt:**
    ```txt
    streamlit==1.53.1
    google-generativeai>=0.3.0
    pypdf>=3.0.0
    ```
    
    ### **Streamlit Secrets (.streamlit/secrets.toml):**
    ```toml
    GOOGLE_API_KEY = "your-gemini-api-key-here"
    ```
    
    ### **Get FREE API Key:**
    1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Sign in with Google account
    3. Create API key
    4. Copy and add to secrets.toml
    
    ### **Available Free Models:**
    - `gemini-1.5-flash-latest`: Fastest, recommended
    - `gemini-1.5-pro-latest`: Higher quality
    - `gemini-1.0-pro`: Legacy but reliable
    """)

st.caption("Powered by Google Gemini AI • Free Tier")
