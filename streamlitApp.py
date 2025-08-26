import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from langchain_community.callbacks.manager import get_openai_callback
from scr.mcqgenrator.MCQ import generate_evaluate_chain
from scr.mcqgenrator.utils import read_file, get_table_data
from scr.mcqgenrator.logger import logging
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="MCQ Creator Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# Custom CSS
# ========================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        color: #333333 !important;
    }
    
    .metric-card h4 { color: #2c3e50 !important; margin-bottom: 0.5rem; }
    .metric-card p { color: #555555 !important; margin-bottom: 0.3rem; }
    .metric-card strong { color: #2c3e50 !important; }
    
    .success-message {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9ff 0%, #e8eeff 100%);
    }

    .quiz-container {
        background: #f8f9ff;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        color: #2c3e50 !important;
    }

    /* --- MCQ Table (Dark theme: black bg + white text) --- */
    .stDataFrame {
        background: #000000 !important;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    .stDataFrame table { background: #000000 !important; }

    .stDataFrame th {
        background-color: #111111 !important;
        color: #ffffff !important;
        font-weight: bold;
        padding: 12px 8px;
        text-align: center;
    }

    .stDataFrame td {
        background-color: #000000 !important;
        color: #ffffff !important;
        padding: 10px 8px;
        border-bottom: 1px solid #333333;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-width: 300px;
    }

    /* Force ALL rows same style */
    .stDataFrame tr:nth-child(odd) td,
    .stDataFrame tr:nth-child(even) td {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Index column */
    .stDataFrame td:first-child {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: bold;
        text-align: center;
    }

    .stDataFrame tr:hover td {
        background-color: #222222 !important;
        color: #ffffff !important;
    }

    /* --- Sidebar Quick Tips (white text) --- */
    .sidebar .stInfo, 
    .sidebar .stInfo > div,
    .sidebar .stMarkdown,
    .sidebar .stMarkdown h3 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# Load Response.json
# ========================
@st.cache_data
def load_response_json():
    try:
        with open('Response.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Response.json file not found!")
        return {}

RESPONSE_JSON = load_response_json()

# ========================
# Sidebar
# ========================
with st.sidebar:
    st.markdown("### 🎯 Quick Tips")
    st.info("📄 **Supported Files**: PDF, TXT")
    st.info("📊 **Optimal Range**: 5-20 MCQs")
    st.info("🎨 **Tone Examples**: Simple, Medium, Complex, Academic")

    st.markdown("### 📈 Usage Statistics")
    if 'total_mcqs_generated' not in st.session_state:
        st.session_state.total_mcqs_generated = 0
    if 'total_files_processed' not in st.session_state:
        st.session_state.total_files_processed = 0

    st.metric("Total MCQs Generated", st.session_state.total_mcqs_generated)
    st.metric("Files Processed", st.session_state.total_files_processed)

# ========================
# Main Header
# ========================
st.markdown("""
<div class="main-header">
    <h1>🧠 MCQ Creator Pro</h1>
    <h3>Generate Smart Multiple Choice Questions with AI</h3>
    <p>Powered by LangChain & OpenAI 🦜⛓️</p>
</div>
""", unsafe_allow_html=True)

# ========================
# Main Container
# ========================
col1, col2 = st.columns([2, 1])

with col1:
    with st.form("user_inputs", clear_on_submit=False):
        st.markdown("### 📋 Configure Your MCQ Generation")
        uploaded_file = st.file_uploader("📁 Upload Your Document", type=['pdf', 'txt'])
        
        if uploaded_file:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size/1024:.2f} KB)")

        col_a, col_b = st.columns(2)
        with col_a:
            mcq_count = st.selectbox("🔢 Number of MCQs", options=[3,5,10,15,20,25,30,35,40,45,50], index=2)
            subject = st.text_input("📚 Subject Area", placeholder="e.g., Biology, Physics, History...")
        with col_b:
            tone = st.select_slider("🎯 Complexity Level", options=["Beginner","Simple","Medium","Advanced","Expert"], value="Medium")
            question_type = st.multiselect("❓ Question Types", ["Factual","Conceptual","Application","Analysis"], default=["Factual","Conceptual"])
        
        with st.expander("⚙️ Advanced Options"):
            include_explanations = st.checkbox("Include detailed explanations", value=True)
            randomize_options = st.checkbox("Randomize answer options", value=True)
            focus_keywords = st.text_input("🔍 Focus Keywords (optional)")

        button = st.form_submit_button("🚀 Generate MCQs", type="primary", use_container_width=True)

with col2:
    st.markdown("### 📊 Preview")
    if uploaded_file and mcq_count and subject:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📝 Generation Preview</h4>
            <p><strong>File:</strong> {uploaded_file.name}</p>
            <p><strong>Questions:</strong> {mcq_count} MCQs</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Level:</strong> {tone}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👆 Fill in the form to see preview")

# ========================
# Processing Logic
# ========================
if button and uploaded_file is not None and mcq_count and subject and tone:
    progress_bar = st.progress(0)
    status_text = st.empty()
    result_col1, result_col2 = st.columns([3, 1])

    with result_col1:
        try:
            status_text.text("📖 Reading file...")
            progress_bar.progress(20)
            text = read_file(uploaded_file)

            status_text.text("🔍 Processing content...")
            progress_bar.progress(40)

            with get_openai_callback() as cb:
                status_text.text("🤖 Generating MCQs with AI...")
                progress_bar.progress(70)
                response = generate_evaluate_chain({
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                })

            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)
            st.session_state.total_mcqs_generated += mcq_count
            st.session_state.total_files_processed += 1

        except Exception as e:
            st.error(f"❌ **Error occurred:** {str(e)}")
            st.code(traceback.format_exc())

        else:
            st.markdown("""
            <div class="success-message">
                <h3>🎉 MCQs Generated Successfully!</h3>
            </div>
            """, unsafe_allow_html=True)

            with result_col2:
                st.markdown("### 📈 API Usage")
                st.metric("Total Tokens", f"{cb.total_tokens:,}")
                st.metric("Cost (USD)", f"${cb.total_cost:.4f}")
                st.metric("Time", f"{datetime.now().strftime('%H:%M:%S')}")

            if isinstance(response, dict):
                quiz = response.get("quiz", None)
                if quiz is not None:
                    st.markdown("### 📋 Generated MCQs")
                    table_data = get_table_data(quiz)
                    if table_data is not None:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        
                        # no alternating style
                        st.dataframe(df, use_container_width=True, height=400)

                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download MCQs as CSV",
                            data=csv,
                            file_name=f"mcqs_{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            type="secondary"
                        )

                        if "review" in response:
                            st.markdown("### 🔍 AI Review & Feedback")
                            st.markdown(f"""
                            <div class="quiz-container">
                                <p>{response["review"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Error processing the generated questions")
                else:
                    st.error("❌ No quiz data found in response")
            else:
                st.code(str(response), language="json")

            progress_bar.empty()
            status_text.empty()

# ========================
# Footer
# ========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Made with ❤️ using Streamlit & LangChain</p>
</div>
""", unsafe_allow_html=True)
