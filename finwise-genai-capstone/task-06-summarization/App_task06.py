import os
import tempfile
import streamlit as st
import google.generativeai as genai
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Financial Document Summarizer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Custom CSS
# ============================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .summary-box {
        background-color: #f8fafc;
        color: #1e293b;
        padding: 2rem;
        border-radius: 12px;
        border-left: 6px solid #1f77b4;
        white-space: pre-wrap;
        line-height: 1.8;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
    }
    .file-card {
        background-color: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background: linear-gradient(135deg, #1f77b4 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.8rem 2.5rem;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(31, 119, 180, 0.2);
    }
    .success-msg {
        background-color: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    .warning-msg {
        background-color: #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Google Gemini API Setup (FREE TIER)
# ============================

# Display API key instructions prominently
st.sidebar.title("🔑 API Setup")

with st.sidebar.expander("📋 How to get FREE Gemini API Key", expanded=True):
    st.markdown("""
    1. **Go to**: [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. **Sign in** with Google account
    3. **Create API key** (it's free!)
    4. **Copy key** and paste below
    
    **Free Limits:**
    - 60 requests per minute
    - 15 million tokens per month
    - More than enough for regular use
    """)

# Get API key
try:
    # First try Streamlit secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.markdown('<div class="success-msg">✓ API key loaded from secrets</div>', unsafe_allow_html=True)
except KeyError:
    # Fallback to user input
    api_key = st.sidebar.text_input(
        "Enter your Gemini API Key:",
        type="password",
        placeholder="Paste your API key here...",
        help="Get free API key from https://makersuite.google.com/app/apikey"
    )
    
    if api_key:
        st.sidebar.markdown('<div class="success-msg">✓ API key entered</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="warning-msg">⚠️ API key required</div>', unsafe_allow_html=True)

# Configure Gemini
if api_key:
    try:
        genai.configure(api_key=api_key)
        st.sidebar.success("✅ Gemini API configured successfully")
    except Exception as e:
        st.sidebar.error(f"Configuration error: {str(e)}")
else:
    st.warning("Please enter your Gemini API key to continue")
    st.info("""
    **Getting your FREE Gemini API key:**
    
    1. Visit **[Google AI Studio](https://makersuite.google.com/app/apikey)**
    2. Click **"Create API Key"**
    3. Copy the key and paste in the sidebar
    4. The free tier is very generous (60 RPM, 15M tokens/month)
    """)
    st.stop()

# ============================
# Sidebar Configuration
# ============================
st.sidebar.title("⚙️ Summarization Settings")

# Correct Gemini model names - Updated!
model_name = st.sidebar.selectbox(
    "Gemini Model",
    options=[
        "gemini-1.5-flash-latest",  # Updated name
        "gemini-1.5-pro-latest",    # Updated name
        "gemini-pro",               # Legacy but still works
    ],
    index=0,
    help="gemini-1.5-flash-latest: Fast & free | gemini-1.5-pro-latest: Higher quality"
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Lower = more factual, Higher = more creative"
)

summary_length = st.sidebar.selectbox(
    "Summary Length",
    options=["Concise (1-2 paragraphs)", "Detailed (3-4 paragraphs)", "Comprehensive (5+ paragraphs)"],
    index=1,
    help="Control the length of the summary"
)

# Map selection to token limits
length_map = {
    "Concise (1-2 paragraphs)": 500,
    "Detailed (3-4 paragraphs)": 800,
    "Comprehensive (5+ paragraphs)": 1200
}
max_output_tokens = length_map[summary_length]

# ============================
# Initialize Gemini Model
# ============================
@st.cache_resource
def get_gemini_model(_model_name, _temperature, _max_output_tokens):
    """Initialize and cache Gemini model with correct configuration"""
    try:
        # Create generation configuration
        generation_config = {
            "temperature": _temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": _max_output_tokens,
        }
        
        # Safety settings (minimal blocking for financial docs)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Initialize the model
        model = genai.GenerativeModel(
            model_name=_model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Test the model with a simple prompt
        test_response = model.generate_content("Hello")
        if test_response.text:
            st.sidebar.success(f"✅ Model '{_model_name}' loaded successfully")
            return model
        else:
            st.sidebar.error(f"❌ Model test failed")
            return None
            
    except Exception as e:
        st.sidebar.error(f"❌ Error loading model: {str(e)}")
        # Try fallback model
        if _model_name != "gemini-pro":
            st.sidebar.info("Trying fallback model: gemini-pro")
            return get_gemini_model("gemini-pro", _temperature, _max_output_tokens)
        return None

# Initialize model
model = get_gemini_model(model_name, temperature, max_output_tokens)

if not model:
    st.error("""
    ❌ Could not initialize Gemini model. Possible issues:
    1. Invalid API key
    2. Model name not found
    3. API quota exceeded
    
    **Try these fixes:**
    - Use model name: `gemini-1.5-flash-latest`
    - Verify your API key is correct
    - Check your Google AI Studio dashboard
    """)
    st.stop()

# ============================
# File Processing Functions
# ============================
def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"--- Page {page_num} ---\n{page_text}\n\n"
        
        return text.strip() if text else "No text could be extracted from PDF"
        
    except ImportError:
        return "ERROR: Please install pypdf (pip install pypdf)"
    except Exception as e:
        return f"ERROR extracting PDF: {str(e)}"

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"ERROR reading text file: {str(e)}"

def process_uploaded_files(uploaded_files):
    """Process all uploaded files and extract text"""
    all_text = ""
    file_details = []
    
    for uploaded_file in uploaded_files:
        # Create temporary file
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        
        try:
            file_text = ""
            if uploaded_file.type == "application/pdf":
                file_text = extract_text_from_pdf(temp_path)
                file_type = "📄 PDF"
            elif uploaded_file.type == "text/plain":
                file_text = extract_text_from_txt(temp_path)
                file_type = "📝 TXT"
            else:
                st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                continue
            
            if file_text and not file_text.startswith("ERROR"):
                # Add to combined text
                all_text += f"\n\n{'='*60}\n📁 FILE: {uploaded_file.name}\n{'='*60}\n\n{file_text}"
                
                # Store file details
                file_details.append({
                    "name": uploaded_file.name,
                    "type": file_type,
                    "size": len(uploaded_file.getvalue()),
                    "text_length": len(file_text),
                    "pages": file_text.count("--- Page") if uploaded_file.type == "application/pdf" else 1
                })
                
                # Show success message
                st.markdown(f"""
                <div class="file-card">
                ✅ <b>{uploaded_file.name}</b><br>
                {file_type} • {len(file_text):,} characters • {file_details[-1]['pages']} pages
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ Failed to process: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    return all_text.strip(), file_details

# ============================
# Summarization Function
# ============================
def generate_summary(text, file_details):
    """Generate summary using Gemini"""
    
    # Truncate if too long (Gemini has token limits)
    original_length = len(text)
    if original_length > 30000:
        st.warning(f"⚠️ Document very large ({original_length:,} chars). Using first 30,000 characters.")
        text = text[:30000]
    
    # Create context about files
    files_context = ""
    if file_details:
        files_context = "Documents being summarized:\n"
        for i, detail in enumerate(file_details, 1):
            files_context += f"{i}. {detail['name']} ({detail['type']}, {detail['text_length']:,} chars)\n"
    
    # Create the prompt
    prompt = f"""You are an expert financial analyst. Please analyze the following financial document(s) and provide a comprehensive summary.

{files_context}

**INSTRUCTIONS:**
1. Focus on key financial metrics, performance indicators, and trends
2. Identify strategic initiatives, developments, and milestones
3. Note any risks, challenges, or concerns mentioned
4. Highlight future outlook, guidance, and projections
5. Mention important dates, deadlines, or events
6. Structure the summary with clear paragraphs and bullet points where appropriate
7. Use professional financial terminology

**DOCUMENT CONTENT:**
{text}

**FINANCIAL ANALYSIS SUMMARY:**
"""
    
    try:
        # Generate response
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            # Check for blocked content
            if response.prompt_feedback:
                return f"Content blocked: {response.prompt_feedback.block_reason}"
            return "No summary generated. The response was empty."
            
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# ============================
# Main App Interface
# ============================
st.markdown('<h1 class="main-header">💼 Financial Document Summarizer</h1>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem; color: #4b5563;">
Upload financial documents (PDF/TXT) for AI-powered analysis using <b>Google Gemini AI (Free Tier)</b>
</div>
""", unsafe_allow_html=True)

# File upload section
uploaded_files = st.file_uploader(
    "📁 Drag and drop files here",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Upload multiple PDF or text files. They will be combined for analysis."
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    # Process files
    with st.spinner("🔍 Extracting and processing documents..."):
        extracted_text, file_details = process_uploaded_files(uploaded_files)
    
    if extracted_text and len(extracted_text) > 100:
        # Display file statistics
        st.subheader("📊 Document Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        total_chars = sum(fd["text_length"] for fd in file_details)
        total_pages = sum(fd.get("pages", 1) for fd in file_details)
        
        with col1:
            st.markdown('<div class="metric-card"><b>Total Files</b><br><span style="font-size: 2rem;">📚</span><br><span style="font-size: 1.5rem;">{}</span></div>'.format(len(file_details)), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card"><b>Total Pages</b><br><span style="font-size: 2rem;">📄</span><br><span style="font-size: 1.5rem;">{}</span></div>'.format(total_pages), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card"><b>Characters</b><br><span style="font-size: 2rem;">🔢</span><br><span style="font-size: 1.5rem;">{:,}</span></div>'.format(total_chars), unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-card"><b>Words</b><br><span style="font-size: 2rem;">📝</span><br><span style="font-size: 1.5rem;">{:,}</span></div>'.format(len(extracted_text.split())), unsafe_allow_html=True)
        
        # Preview extracted text
        with st.expander("📋 Preview Extracted Text", expanded=False):
            preview = extracted_text[:3000]
            if len(extracted_text) > 3000:
                preview += "\n\n[... document truncated for preview ...]"
            st.text(preview)
        
        # Generate summary button
        st.divider()
        
        if st.button("🚀 Generate Financial Summary", type="primary", use_container_width=True):
            with st.spinner("🤖 Analyzing with Gemini AI. This may take a moment..."):
                summary = generate_summary(extracted_text, file_details)
            
            # Display summary
            st.subheader("📋 AI Financial Analysis Summary")
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
            
            # Summary statistics
            st.subheader("📈 Summary Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                compression = 100 - (len(summary) / total_chars * 100) if total_chars > 0 else 0
                st.metric("Compression Ratio", f"{compression:.1f}%")
            with col2:
                st.metric("Summary Length", f"{len(summary):,} chars")
            with col3:
                st.metric("Word Count", f"{len(summary.split()):,}")
            
            # Download button
            st.download_button(
                label="💾 Download Summary as Text File",
                data=summary,
                file_name="financial_analysis_summary.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # Show model info
            st.caption(f"⚡ Using {model_name} | Temperature: {temperature} | Max tokens: {max_output_tokens}")
    else:
        st.error("❌ Could not extract sufficient text from the uploaded files")
else:
    # Welcome message when no files uploaded
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #f8fafc; border-radius: 15px; margin: 2rem 0;">
        <div style="font-size: 4rem;">📁</div>
        <h3 style="color: #1f77b4;">Ready to Analyze</h3>
        <p style="color: #64748b;">Upload financial documents to get started</p>
        <p style="color: #94a3b8; font-size: 0.9rem;">Supported: PDF & TXT files</p>
        </div>
        """, unsafe_allow_html=True)

# ============================
# Footer & Information
# ============================
st.divider()

with st.expander("ℹ️ About This App & Setup Instructions", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **🎯 Features**
        
        - **Free Google Gemini API**: Generous free tier
        - **Multi-file support**: Combine PDFs & text files
        - **Financial focus**: Specialized for financial documents
        - **Customizable**: Adjust length & creativity
        - **Downloadable**: Save summaries as text files
        
        ### **📊 Supported Documents**
        
        - Annual reports
        - Financial statements
        - Earnings releases
        - SEC filings (10-K, 10-Q)
        - Investment memos
        - Market research
        """)
    
    with col2:
        st.markdown("""
        ### **⚙️ Setup Instructions**
        
        1. **Get FREE API Key**:
           - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
           - Sign in & create API key
        
        2. **Add to Streamlit**:
           ```toml
           # .streamlit/secrets.toml
           GOOGLE_API_KEY = "your-key-here"
           ```
        
        3. **requirements.txt**:
           ```txt
           streamlit>=1.28.0
           google-generativeai>=0.3.0
           pypdf>=3.0.0
           ```
        
        4. **Deploy** to Streamlit Cloud
        
        ### **💎 Free Tier Limits**
        - 60 requests per minute
        - 15 million tokens per month
        - More than enough for personal use
        """)

st.markdown("---")
st.caption("""
<div style="text-align: center; color: #94a3b8;">
Built with ❤️ using Streamlit • Powered by Google Gemini AI (Free Tier) • 
<a href="https://makersuite.google.com/app/apikey" target="_blank" style="color: #3b82f6;">Get your free API key</a>
</div>
""", unsafe_allow_html=True)

# ============================
# Debug Information (Hidden)
# ============================
if st.sidebar.checkbox("Show debug info", value=False):
    st.sidebar.write("**Debug Info:**")
    st.sidebar.write(f"API Key exists: {bool(api_key)}")
    st.sidebar.write(f"API Key length: {len(api_key) if api_key else 0}")
    st.sidebar.write(f"Selected model: {model_name}")
    
    # Test API connection
    if st.sidebar.button("Test API Connection"):
        try:
            # List available models
            available_models = genai.list_models()
            model_names = [m.name for m in available_models]
            st.sidebar.write("**Available models:**")
            for name in model_names:
                if "gemini" in name.lower():
                    st.sidebar.code(name)
        except Exception as e:
            st.sidebar.error(f"API test failed: {str(e)}")

# Test code to see available models
import google.generativeai as genai
genai.configure(api_key="your-api-key")

models = genai.list_models()
for model in models:
    if "gemini" in model.name.lower():
        print(f"Model: {model.name}")
        print(f"  Supported methods: {model.supported_generation_methods}")
        print()
