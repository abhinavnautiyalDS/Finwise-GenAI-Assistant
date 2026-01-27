import os
import tempfile
import streamlit as st
import requests
import json
from pathlib import Path

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Fixed Custom CSS (Dark Text on Light Background)
# ============================
st.markdown("""
<style>
    /* Main container */
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    
    /* Summary box - Dark text on light background */
    .summary-box {
        background-color: #ffffff;
        color: #1f2937 !important;  /* Dark text */
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        line-height: 1.7;
        font-size: 1.05rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Text elements - Ensure dark text */
    .stText, .stMarkdown, .stExpander, p, div, span {
        color: #ffffff !important;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8fafc;
        color: #1f2937 !important;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-size: 1rem;
    }
    
    /* File info cards */
    .file-card {
        background-color: #f1f5f9;
        color: #1f2937 !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    /* Info/warning boxes */
    .info-box {
        background-color: #dbeafe;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fef3c7;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    
    /* Streamlit text elements override */
    .st-bb, .st-bc, .st-bd, .st-be, .st-bf, .st-bg, .st-bh, .st-bi, .st-bj, .st-bk, .st-bl, .st-bm, .st-bn, .st-bo, .st-bp, .st-bq, .st-br, .st-bs, .st-bt, .st-bu, .st-bv, .st-bw, .st-bx, .st-by, .st-bz, .st-c0, .st-c1, .st-c2, .st-c3, .st-c4, .st-c5, .st-c6, .st-c7, .st-c8, .st-c9, .st-ca, .st-cb, .st-cc, .st-cd, .st-ce, .st-cf, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz, .st-d0, .st-d1, .st-d2, .st-d3, .st-d4, .st-d5, .st-d6, .st-d7, .st-d8, .st-d9, .st-da, .st-db, .st-dc, .st-dd, .st-de, .st-df, .st-dg, .st-dh, .st-di, .st-dj, .st-dk, .st-dl, .st-dm, .st-dn, .st-do, .st-dp, .st-dq, .st-dr, .st-ds, .st-dt, .st-du, .st-dv, .st-dw, .st-dx, .st-dy, .st-dz, .st-e0, .st-e1, .st-e2, .st-e3, .st-e4, .st-e5, .st-e6, .st-e7, .st-e8, .st-e9, .st-ea, .st-eb, .st-ec, .st-ed, .st-ee, .st-ef, .st-eg, .st-eh, .st-ei, .st-ej, .st-ek, .st-el, .st-em, .st-en, .st-eo, .st-ep, .st-eq, .st-er, .st-es, .st-et, .st-eu, .st-ev, .st-ew, .st-ex, .st-ey, .st-ez, .st-f0, .st-f1, .st-f2, .st-f3, .st-f4, .st-f5, .st-f6, .st-f7, .st-f8, .st-f9, .st-fa, .st-fb, .st-fc, .st-fd, .st-fe, .st-ff, .st-fg, .st-fh, .st-fi, .st-fj, .st-fk, .st-fl, .st-fm, .st-fn, .st-fo, .st-fp, .st-fq, .st-fr, .st-fs, .st-ft, .st-fu, .st-fv, .st-fw, .st-fx, .st-fy, .st-fz, .st-g0, .st-g1, .st-g2, .st-g3, .st-g4, .st-g5, .st-g6, .st-g7, .st-g8, .st-g9, .st-ga, .st-gb, .st-gc, .st-gd, .st-ge, .st-gf, .st-gg, .st-gh, .st-gi, .st-gj, .st-gk, .st-gl, .st-gm, .st-gn, .st-go, .st-gp, .st-gq, .st-gr, .st-gs, .st-gt, .st-gu, .st-gv, .st-gw, .st-gx, .st-gy, .st-gz, .st-h0, .st-h1, .st-h2, .st-h3, .st-h4, .st-h5, .st-h6, .st-h7, .st-h8, .st-h9, .st-ha, .st-hb, .st-hc, .st-hd, .st-he, .st-hf, .st-hg, .st-hh, .st-hi, .st-hj, .st-hk, .st-hl, .st-hm, .st-hn, .st-ho, .st-hp, .st-hq, .st-hr, .st-hs, .st-ht, .st-hu, .st-hv, .st-hw, .st-hx, .st-hy, .st-hz, .st-i0, .st-i1, .st-i2, .st-i3, .st-i4, .st-i5, .st-i6, .st-i7, .st-i8, .st-i9, .st-ia, .st-ib, .st-ic, .st-id, .st-ie, .st-if, .st-ig, .st-ih, .st-ii, .st-ij, .st-ik, .st-il, .st-im, .st-in, .st-io, .st-ip, .st-iq, .st-ir, .st-is, .st-it, .st-iu, .st-iv, .st-iw, .st-ix, .st-iy, .st-iz, .st-j0, .st-j1, .st-j2, .st-j3, .st-j4, .st-j5, .st-j6, .st-j7, .st-j8, .st-j9, .st-ja, .st-jb, .st-jc, .st-jd, .st-je, .st-jf, .st-jg, .st-jh, .st-ji, .st-jj, .st-jk, .st-jl, .st-jm, .st-jn, .st-jo, .st-jp, .st-jq, .st-jr, .st-js, .st-jt, .st-ju, .st-jv, .st-jw, .st-jx, .st-jy, .st-jz, .st-k0, .st-k1, .st-k2, .st-k3, .st-k4, .st-k5, .st-k6, .st-k7, .st-k8, .st-k9, .st-ka, .st-kb, .st-kc, .st-kd, .st-ke, .st-kf, .st-kg, .st-kh, .st-ki, .st-kj, .st-kk, .st-kl, .st-km, .st-kn, .st-ko, .st-kp, .st-kq, .st-kr, .st-ks, .st-kt, .st-ku, .st-kv, .st-kw, .st-kx, .st-ky, .st-kz, .st-l0, .st-l1, .st-l2, .st-l3, .st-l4, .st-l5, .st-l6, .st-l7, .st-l8, .st-l9, .st-la, .st-lb, .st-lc, .st-ld, .st-le, .st-lf, .st-lg, .st-lh, .st-li, .st-lj, .st-lk, .st-ll, .st-lm, .st-ln, .st-lo, .st-lp, .st-lq, .st-lr, .st-ls, .st-lt, .st-lu, .st-lv, .st-lw, .st-lx, .st-ly, .st-lz {
        color: #1f2937 !important;
    }
    
    /* Text in expanders */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        color: #1f2937 !important;
    }
    
    /* All text in the app */
    * {
        color: #1f2937 !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        color: #1f2937 !important;
        background-color: white !important;
    }
    
    /* Sliders */
    .stSlider>div>div>div>div {
        color: #1f2937 !important;
    }
    
    /* Metric values */
    .stMetric {
        color: #1f2937 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# OpenRouter Configuration - ONLY Mistral 7B
# ============================
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "mistralai/mistral-7b-instruct"
MODEL_CONTEXT = 32768  # Max context length in tokens
MODEL_NAME = "Mistral 7B"

# ============================
# Sidebar Configuration
# ============================
st.sidebar.title("⚙️ Configuration")

# Get API Key
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    st.sidebar.success("✓ API key loaded")
except KeyError:
    OPENROUTER_API_KEY = st.sidebar.text_input(
        "Enter OpenRouter API Key:",
        type="password",
        help="Get free key from https://openrouter.ai"
    )
    if OPENROUTER_API_KEY:
        st.sidebar.success("✓ API key entered")
    else:
        st.sidebar.warning("⚠️ API key required")

# Show model info
st.sidebar.markdown(f"""
<div style="background-color: #e0f2fe; padding: 1rem; border-radius: 8px; border-left: 4px solid #0ea5e9;">
    <b>🤖 Using: {MODEL_NAME}</b><br>
    <small>Max context: {MODEL_CONTEXT:,} tokens</small><br>
    <small>Provider: Mistral AI</small>
</div>
""", unsafe_allow_html=True)

# Summarization Settings
st.sidebar.subheader("📝 Settings")

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1,
    help="Lower = more factual, Higher = more creative"
)

max_tokens = st.sidebar.slider(
    "Max Summary Tokens",
    min_value=100,
    max_value=1000,
    value=500,
    step=50,
    help="Maximum tokens in summary (output)"
)

# Token usage info
st.sidebar.markdown(f"""
<div style="background-color: #fef3c7; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
    <b>📊 Token Limits:</b><br>
    • Max context: {MODEL_CONTEXT:,} tokens<br>
    • Your output: {max_tokens} tokens<br>
    • Available for input: {MODEL_CONTEXT - max_tokens:,} tokens
</div>
""", unsafe_allow_html=True)

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
        
        return text.strip() if text else "No text could be extracted"
        
    except ImportError:
        return "ERROR: Please install pypdf"
    except Exception as e:
        return f"ERROR: {str(e)}"

def process_uploaded_files(uploaded_files):
    """Process uploaded files and extract text"""
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
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_text = f.read()
                file_type = "📝 TXT"
            else:
                st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
                continue
            
            if file_text and not file_text.startswith("ERROR"):
                # Add to combined text
                all_text += f"\n\n{'='*60}\n📁 File: {uploaded_file.name}\n{'='*60}\n\n{file_text}"
                
                # Store file details
                file_details.append({
                    "name": uploaded_file.name,
                    "type": file_type,
                    "size": len(uploaded_file.getvalue()),
                    "text_length": len(file_text),
                    "pages": file_text.count("--- Page") if uploaded_file.type == "application/pdf" else 1
                })
                
                st.success(f"✅ Processed: {uploaded_file.name}")
            else:
                st.error(f"❌ Failed to process: {uploaded_file.name}")
                
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return all_text.strip(), file_details

# ============================
# Token Estimation Function
# ============================
def estimate_tokens(text):
    """Estimate number of tokens in text (rough estimate: 1 token ≈ 4 chars)"""
    # Rough estimate for English text
    return len(text) // 4

def truncate_text_by_tokens(text, max_tokens_needed):
    """Truncate text to fit within token limit"""
    # Estimate tokens
    estimated_tokens = estimate_tokens(text)
    
    if estimated_tokens <= max_tokens_needed:
        return text, estimated_tokens
    
    # Calculate how many characters to keep
    # Average chars per token ≈ 4, but be conservative
    chars_per_token = 3.5  # Conservative estimate
    max_chars = int(max_tokens_needed * chars_per_token)
    
    # Truncate text
    truncated_text = text[:max_chars]
    
    # Try to cut at a sentence boundary
    last_period = truncated_text.rfind('. ')
    last_newline = truncated_text.rfind('\n\n')
    
    cut_point = max(last_period, last_newline)
    if cut_point > max_chars * 0.8:  # Only if we don't lose too much
        truncated_text = truncated_text[:cut_point + 1]
    
    new_estimate = estimate_tokens(truncated_text)
    return truncated_text, new_estimate

# ============================
# OpenRouter API Function with Token Limit Handling
# ============================
def summarize_with_mistral(text, temperature=0.3, max_output_tokens=500):
    """Summarize text using Mistral 7B via OpenRouter"""
    
    if not OPENROUTER_API_KEY:
        return "❌ Please provide OpenRouter API key", 0, 0
    
    # Calculate max input tokens (leave room for output + prompt overhead)
    max_input_tokens = MODEL_CONTEXT - max_output_tokens - 100  # Reserve 100 tokens for prompt overhead
    
    # Truncate text to fit within token limit
    truncated_text, input_tokens_used = truncate_text_by_tokens(text, max_input_tokens)
    
    if input_tokens_used < estimate_tokens(text):
        st.warning(f"⚠️ Document too large! Using first {input_tokens_used:,} estimated tokens (out of {estimate_tokens(text):,})")
    
    # Prepare the prompt for Mistral
    prompt = f"""<s>[INST] You are an expert document summarizer. Please provide a concise and accurate summary of the following document(s).

Focus on:
1. Main points and key ideas
2. Important facts and figures  
3. Conclusions and recommendations
4. Critical insights

Document Content:
{truncated_text}

Please provide a well-structured summary that captures the essence of the document(s). [/INST]</s>
"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://document-summarizer.streamlit.app",
        "X-Title": "Document Summarizer"
    }
    
    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_output_tokens,
    }
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                summary = result["choices"][0]["message"]["content"].strip()
                
                # Clean up any leftover prompt fragments
                summary = summary.split("</s>")[0].strip()
                summary = summary.split("[INST]")[0].strip()
                summary = summary.split("[/INST]")[0].strip()
                
                # Estimate output tokens
                output_tokens = estimate_tokens(summary)
                
                return summary, input_tokens_used, output_tokens
            else:
                return f"❌ No summary in response: {result}", 0, 0
                
        elif response.status_code == 400:
            error_data = response.json()
            if "maximum context length" in str(error_data).lower():
                # Try with more aggressive truncation
                st.error("⚠️ Context length exceeded. Trying with more aggressive truncation...")
                more_truncated_text, new_input_tokens = truncate_text_by_tokens(text, max_input_tokens - 1000)
                return summarize_with_mistral(more_truncated_text, temperature, max_output_tokens)
            return f"❌ API Error 400: {error_data}", 0, 0
            
        elif response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please wait a moment and try again.", 0, 0
            
        elif response.status_code == 401:
            return "❌ Invalid API key. Please check your OpenRouter API key.", 0, 0
            
        else:
            error_msg = response.text[:200] if response.text else "Unknown error"
            return f"❌ API Error {response.status_code}: {error_msg}", 0, 0
            
    except requests.exceptions.Timeout:
        return "⏱️ Request timeout. Please try again.", 0, 0
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please check your internet.", 0, 0
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}", 0, 0

# ============================
# Main App Interface
# ============================
st.markdown('<h1 class="main-header">📄 Document Summarizer</h1>', unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align: center; color: #374151; margin-bottom: 2rem;">
Using: <b>{MODEL_NAME}</b> • Free Tier • Max {MODEL_CONTEXT:,} tokens
</div>
""", unsafe_allow_html=True)

# File upload section
uploaded_files = st.file_uploader(
    "📁 Drag and drop files here (PDF or TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    help="Multiple files will be combined"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    # Process files
    with st.spinner("🔍 Extracting text from documents..."):
        extracted_text, file_details = process_uploaded_files(uploaded_files)
    
    if extracted_text and len(extracted_text) > 100:
        # Display file statistics
        st.subheader("📊 Document Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        total_chars = sum(fd["text_length"] for fd in file_details)
        estimated_tokens = estimate_tokens(extracted_text)
        
        with col1:
            st.metric("Total Files", len(file_details))
        with col2:
            st.metric("Characters", f"{total_chars:,}")
        with col3:
            st.metric("Words", f"{len(extracted_text.split()):,}")
        with col4:
            st.metric("Estimated Tokens", f"{estimated_tokens:,}")
        
        # Check if document fits within context
        max_allowed_tokens = MODEL_CONTEXT - max_tokens - 100
        if estimated_tokens > max_allowed_tokens:
            st.warning(f"⚠️ Document is large ({estimated_tokens:,} tokens). Only first {max_allowed_tokens:,} tokens will be used for summarization.")
        
        # Preview extracted text
        with st.expander("📋 Preview Extracted Text", expanded=False):
            preview = extracted_text[:2000]
            if len(extracted_text) > 2000:
                preview += "\n\n[... document truncated for preview ...]"
            st.text(preview)
        
        # Generate summary button
        st.divider()
        
        if st.button("🚀 Generate AI Summary", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Summarizing with {MODEL_NAME}..."):
                summary, input_tokens_used, output_tokens = summarize_with_mistral(
                    extracted_text,
                    temperature,
                    max_tokens
                )
            
            # Display results
            if summary and not summary.startswith("❌") and not summary.startswith("⚠️"):
                st.subheader("📋 AI Summary")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                # Token usage statistics
                st.subheader("📈 Token Usage")
                
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Input Tokens", f"{input_tokens_used:,}")
                with cols[1]:
                    st.metric("Output Tokens", f"{output_tokens:,}")
                with cols[2]:
                    total_tokens = input_tokens_used + output_tokens
                    st.metric("Total Tokens", f"{total_tokens:,}")
                with cols[3]:
                    if total_tokens > 0:
                        efficiency = (output_tokens / total_tokens) * 100
                        st.metric("Efficiency", f"{efficiency:.1f}%")
                
                # Text statistics
                st.subheader("📊 Text Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Text", f"{total_chars:,} chars")
                with col2:
                    st.metric("Summary", f"{len(summary):,} chars")
                with col3:
                    if total_chars > 0:
                        compression = 100 - (len(summary) / total_chars * 100)
                        st.metric("Compression", f"{compression:.1f}%")
                
                # Download button
                st.download_button(
                    "💾 Download Summary",
                    summary,
                    file_name="document_summary.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.error(f"Summary generation failed: {summary}")
    else:
        st.error("❌ Could not extract sufficient text from files")
else:
    # Welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #f8fafc; border-radius: 15px; border: 2px solid #e2e8f0;">
        <div style="font-size: 4rem; color: #3b82f6;">📁</div>
        <h3 style="color: #1e3a8a;">Ready to Summarize</h3>
        <p style="color: #4b5563;">Upload documents to get AI-powered summaries</p>
        <p style="color: #6b7280; font-size: 0.9rem;">Free • Fast • Powered by Mistral 7B</p>
        </div>
        """, unsafe_allow_html=True)

# ============================
# Instructions
# ============================
with st.expander("ℹ️ Setup Instructions", expanded=False):
    st.markdown("""
    ### **⚙️ Requirements.txt:**
    ```txt
    streamlit==1.53.1
    requests==2.32.5
    pypdf>=3.0.0
    ```
    
    ### **🔑 Get FREE OpenRouter API Key:**
    1. Visit **[OpenRouter](https://openrouter.ai)**
    2. Sign up with email (no credit card)
    3. Get 500 free requests per day
    4. Copy your API key
    
    ### **🔧 Streamlit Secrets (.streamlit/secrets.toml):**
    ```toml
    OPENROUTER_API_KEY = "your-api-key-here"
    ```
    
    ### **🤖 About Mistral 7B:**
    - **Context Window**: 32,768 tokens
    - **Free Tier**: 500 requests/day
    - **Best For**: General document summarization
    - **Provider**: Mistral AI
    
    ### **💡 Tips for Best Results:**
    - Keep **temperature** at 0.3 for factual summaries
    - Use **500-700 tokens** for output length
    - Large documents are automatically truncated
    - First request may be slower (model loading)
    """)

st.markdown("---")
st.caption("""
<div style="text-align: center; color: #6b7280;">
Built with Streamlit • Powered by Mistral 7B via OpenRouter • 
<a href="https://openrouter.ai" target="_blank" style="color: #3b82f6;">Get free API key</a>
</div>
""", unsafe_allow_html=True)
