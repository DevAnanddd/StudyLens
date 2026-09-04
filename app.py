"""
StudyLens - Main Streamlit Application.
Turn messy lecture slide photos, screenshots, and PDF notes into organized, searchable revision notes.
"""
import streamlit as st
import os
import io
import json
import time
from datetime import datetime
from pathlib import Path
from PIL import Image

# On Streamlit Cloud, the API key lives in st.secrets instead of a local .env file.
# This bridges it into an environment variable so the rest of the app (and utils.config)
# works the same way whether running locally or deployed. Wrapped in try/except because
# st.secrets raises an error locally when no secrets.toml file exists at all.
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Import core modules
from utils.config import (
    DEFAULT_HASH_THRESHOLD,
    DEFAULT_OCR_ENGINE,
    DEFAULT_GEMINI_MODEL,
    GEMINI_API_KEY,
    ALL_SUPPORTED_TYPES,
    OUTPUT_DIR
)
from utils.helpers import pil_to_bytes
from modules.file_processor import process_uploaded_files
from modules.image_preprocessor import preprocess_slide_image
from modules.duplicate_detector import cluster_duplicates
from modules.ocr_engine import extract_text_from_slide
from modules.ai_summarizer import detect_topics_batch, group_slides_by_topic, summarize_topic_group, call_gemini_rest
from modules.note_generator import generate_master_notes, generate_notes_pdf
from modules.search_engine import RevisionSearchEngine
from utils.data_store import save_subjects, load_subjects, save_notes_snapshot, load_notes_history

# Page configuration
st.set_page_config(
    page_title="StudyLens | AI Study Workspace",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling - Linear / Notion inspired Dark Premium SaaS Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 8px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.6); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    .stApp {
        background-color: #090d16;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f1f5f9;
        letter-spacing: -0.01em;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        right: 1.5rem !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0c111d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.2rem 0 !important;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0 16px 0;
        animation: fadeInDown 0.4s ease-out;
    }
    .sidebar-brand-icon {
        font-size: 1.4rem;
        color: #818cf8;
        animation: float 3s ease-in-out infinite;
    }
    .sidebar-brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-sub {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 500;
    }
    .nav-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
        margin-top: 14px;
        margin-bottom: 8px;
    }
    h1, h2, h3, h4, .main-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    .greeting-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        margin-bottom: 4px;
        animation: fadeInUp 0.5s ease-out;
    }
    .greeting-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.6rem;
        animation: fadeInUp 0.6s ease-out;
    }
    .gradient-headline {
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 60%, #38bdf8 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline;
        animation: gradientShift 4s ease infinite;
    }
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.15rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 10px rgba(79, 70, 229, 0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) scale(0.98) !important;
    }
    .stDownloadButton > button {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(8px);
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(51, 65, 85, 0.8) !important;
        border-color: #818cf8 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(18, 26, 43, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 1.8rem !important;
    }
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin: 1rem 0 1.8rem 0;
    }
    .stat-card {
        background: rgba(18, 26, 43, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 16px 14px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        animation: fadeInUp 0.5s ease-out;
    }
    .stat-card:hover {
        transform: translateY(-3px);
        border-color: rgba(129, 140, 248, 0.5);
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.15);
    }
    .stat-icon {
        font-size: 1.35rem;
        margin-bottom: 4px;
        animation: float 3s ease-in-out infinite;
    }
    .stat-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.65rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-top: 4px;
    }
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 7px 12px;
        border-radius: 10px;
        font-size: 0.88rem;
        margin-bottom: 6px;
        background: rgba(18, 26, 43, 0.6);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.25s ease;
    }
    .pipeline-step:hover {
        border-color: rgba(255, 255, 255, 0.1);
        transform: translateX(4px);
    }
    .pipeline-step.done {
        color: #34d399;
    }
    .pipeline-step.active {
        color: #818cf8;
        border-color: rgba(99, 102, 241, 0.4);
        font-weight: 600;
    }
    .pipeline-step.pending {
        color: #64748b;
    }
    .breadcrumb-tag {
        background-color: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .search-card {
        background: rgba(18, 26, 43, 0.75);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        transition: all 0.25s ease;
    }
    .search-card:hover {
        border-left-color: #818cf8;
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.12);
        transform: translateY(-1px);
    }
    .quick-action-btn {
        background: rgba(18, 26, 43, 0.8);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .quick-action-btn:hover {
        border-color: #818cf8;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15);
    }
    .streamlit-expanderHeader {
        background-color: rgba(18, 26, 43, 0.7) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        color: #f8fafc !important;
        transition: all 0.25s ease !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: rgba(129, 140, 248, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


def new_subject_state():
    """Returns a fresh, empty pipeline state for one subject."""
    return {
        "raw_slides": [],
        "duplicate_clusters": [],
        "unique_slides": [],
        "pipeline_stage": "upload",
        "ocr_done": False,
        "topic_summaries": [],
        "master_notes_md": "",
        "search_engine": None,
        "excluded_slide_ids": set(),
        "chat_history": [],
        "quiz_score": {"correct": 0, "total": 0},
        "study_streak_days": 3,
        "last_updated": None
    }


def create_sample_lecture_demo():
    """Generates an instant pre-loaded sample state for demonstration."""
    sample_topic_summaries = [
        {
            "topic": "Neural Network Architecture & Backpropagation",
            "summary_markdown": "### Fundamentals of Multi-Layer Perceptrons\nNeural networks consist of an input layer, one or more hidden layers with non-linear activation functions (e.g. ReLU, GELU), and an output layer.\n\n- **Forward Pass**: Computes affine transformation \\( z = Wx + b \\) followed by activation \\( a = \\sigma(z) \\).\n- **Loss Function**: Evaluates divergence between predictions and ground truth (e.g. Cross-Entropy Loss for classification, MSE for regression).\n- **Backpropagation**: Efficient application of the calculus chain rule to compute gradients \\( \\frac{\\partial \\mathcal{L}}{\\partial W} \\) with respect to all layer weights.\n- **Optimization**: Gradient Descent, Adam, and RMSprop update parameters to minimize empirical risk.",
            "subheadings": [
                {
                    "title": "Layer Types and Activations",
                    "content": "Deep networks alternate linear transformations with non-linearities to avoid matrix collapse into a single affine map.",
                    "key_points": ["ReLU prevents vanishing gradients for positive inputs", "Softmax normalizes raw logits into valid probability distributions"]
                }
            ],
            "definitions": [
                {"term": "Backpropagation", "definition": "An algorithm for computing partial derivatives of the loss function with respect to weights using the reverse-mode chain rule.", "source": "Slide 12"},
                {"term": "Vanishing Gradient Problem", "definition": "Occurs when gradients become exponentially small as they propagate backwards through many layers with saturating activations like Sigmoid.", "source": "Slide 16"}
            ]
        },
        {
            "topic": "Attention Mechanism & Transformers",
            "summary_markdown": "### Scaled Dot-Product and Multi-Head Self-Attention\nThe Transformer architecture dispenses with recurrent units and models sequence relationships directly in parallel via attention matrices.\n\n- **Scaled Dot-Product Formula**: \\( \\text{Attention}(Q,K,V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V \\)\n- **Multi-Head Attention**: Projects Queries, Keys, and Values into \\( h \\) distinct representation subspaces to attend to information at different positions concurrently.\n- **Positional Encoding**: Injects absolute or relative token order information using sinusoidal frequencies or learned embeddings.",
            "subheadings": [
                {
                    "title": "Self-Attention vs Cross-Attention",
                    "content": "Self-attention queries tokens within the same sequence, whereas cross-attention queries the encoder representations from the decoder.",
                    "key_points": ["Computational complexity is \\( O(N^2) \\) with respect to sequence length", "Residual connections & LayerNorm ensure stable gradient flow"]
                }
            ],
            "definitions": [
                {"term": "Multi-Head Attention", "definition": "Linear projections of Q, K, and V into multiple subspaces allowing the model to jointly attend to information from different representation subspaces.", "source": "Slide 22"},
                {"term": "Positional Encoding", "definition": "A mechanism to convey positional relationships among tokens since Transformer operations are permutation-invariant.", "source": "Slide 25"}
            ]
        }
    ]

    stats = {
        "unique_slides": 6,
        "total_words": 1420
    }
    master_md = generate_master_notes(sample_topic_summaries, stats)

    sample_slides = []
    for i in range(1, 7):
        img = Image.new("RGB", (640, 360), color=(18 + i*8, 26 + i*7, 45 + i*14))
        sample_slides.append({
            "id": f"demo_slide_{i}",
            "source_file": "Lecture_07_Deep_Learning.pdf",
            "slide_index": i,
            "image": img,
            "preprocessed_image": img,
            "text": f"Lecture 7 Slide {i}: Neural Architectures, Optimization, and Attention Mechanisms.",
            "confidence": 0.96,
            "engine": "EasyOCR",
            "word_count": 235
        })

    return {
        "raw_slides": sample_slides,
        "duplicate_clusters": [],
        "unique_slides": sample_slides,
        "pipeline_stage": "completed",
        "ocr_done": True,
        "topic_summaries": sample_topic_summaries,
        "master_notes_md": master_md,
        "search_engine": None,
        "excluded_slide_ids": set(),
        "quiz_score": {"correct": 3, "total": 3},
        "study_streak_days": 4,
        "chat_history": [
            {"role": "user", "content": "What is the formula for scaled dot-product attention?"},
            {"role": "assistant", "content": "According to the notes, the formula for Scaled Dot-Product Attention is:\n$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$"}
        ]
    }


# Initialize Session State
if "subjects" not in st.session_state:
    st.session_state.subjects = load_subjects()
if "current_subject" not in st.session_state:
    st.session_state.current_subject = None
if "current_view" not in st.session_state:
    st.session_state.current_view = "Overview"

# --- SIDEBAR: APP NAVIGATION (Linear / Notion Style) ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">◈</div>
        <div>
            <div class="sidebar-brand-title">StudyLens</div>
            <div class="sidebar-brand-sub">AI Study Workspace</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section-label">My Subjects</div>', unsafe_allow_html=True)
    subject_names = list(st.session_state.subjects.keys())

    if subject_names:
        if st.session_state.current_subject not in subject_names:
            st.session_state.current_subject = subject_names[0]

        subject_icons = {"Deep Learning Demo": "🧠", "Data Structures": "💻", "Physics": "⚛"}
        subject_options_labels = [f"{subject_icons.get(name, '📚')} {name}" for name in subject_names]

        current_idx = subject_names.index(st.session_state.current_subject)
        chosen_subject_label = st.selectbox(
            "Active Subject",
            options=subject_options_labels,
            index=current_idx,
            label_visibility="collapsed"
        )
        chosen_subject = subject_names[subject_options_labels.index(chosen_subject_label)]
        if chosen_subject != st.session_state.current_subject:
            st.session_state.current_subject = chosen_subject
            st.rerun()
    else:
        st.caption("No subjects yet. Create one below.")

    with st.popover("➕ New Subject", use_container_width=True):
        new_subject_name = st.text_input(
            "Subject Name",
            placeholder="e.g. Algorithms, Physics 101...",
            key="popover_new_subject"
        )
        if st.button("Create Subject", use_container_width=True, key="popover_create_btn"):
            s_name = new_subject_name.strip()
            if not s_name:
                st.warning("Enter a subject name.")
            elif s_name in st.session_state.subjects:
                st.warning("Subject already exists.")
            else:
                st.session_state.subjects[s_name] = new_subject_state()
                st.session_state.current_subject = s_name
                save_subjects(st.session_state.subjects)
                st.rerun()

    if subject_names:
        with st.popover("⚙️ Manage Subject", use_container_width=True):
            manage_target = st.selectbox(
                "Select subject to manage",
                options=subject_names,
                key="manage_subject_select",
                label_visibility="collapsed"
            )
            mgmt_action = st.radio(
                "Action",
                ["Rename", "Delete"],
                key="mgmt_action",
                horizontal=True,
                label_visibility="collapsed"
            )
            if mgmt_action == "Rename":
                new_name = st.text_input("New name", value=manage_target, key="rename_subject_input")
                if st.button("✅ Rename", use_container_width=True, key="btn_rename_subject"):
                    new_name = new_name.strip()
                    if not new_name:
                        st.warning("Enter a name.")
                    elif new_name == manage_target:
                        st.info("Name is the same.")
                    elif new_name in st.session_state.subjects:
                        st.warning("A subject with that name already exists.")
                    else:
                        st.session_state.subjects[new_name] = st.session_state.subjects.pop(manage_target)
                        if st.session_state.current_subject == manage_target:
                            st.session_state.current_subject = new_name
                        save_subjects(st.session_state.subjects)
                        st.rerun()
            else:
                st.warning(f"Delete **{manage_target}**? This cannot be undone.")
                if st.button("🗑️ Confirm Delete", use_container_width=True, type="primary", key="btn_delete_subject"):
                    del st.session_state.subjects[manage_target]
                    remaining = list(st.session_state.subjects.keys())
                    st.session_state.current_subject = remaining[0] if remaining else None
                    save_subjects(st.session_state.subjects)
                    st.rerun()

    st.markdown("---")

    st.markdown('<div class="nav-section-label">Workspace</div>', unsafe_allow_html=True)

    views = [
        ("⌂ Overview", "Overview"),
        ("📄 Materials", "Materials"),
        ("📝 Revision Notes", "Revision Notes"),
        ("📜 Notes History", "Notes History"),
        ("💬 Chat with Notes", "Chat"),
        ("🎯 Quizzes", "Quizzes")
    ]

    for label, view_key in views:
        is_active = (st.session_state.current_view == view_key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, use_container_width=True, key=f"nav_{view_key}", type=btn_type):
            st.session_state.current_view = view_key
            st.rerun()

    st.markdown("---")

    st.markdown('<div class="nav-section-label">Settings</div>', unsafe_allow_html=True)

    if st.button("✨ Try Sample Demo", use_container_width=True, key="sb_demo_btn", help="Loads pre-made lecture with notes & quiz"):
        st.session_state.subjects["Deep Learning Demo"] = create_sample_lecture_demo()
        st.session_state.current_subject = "Deep Learning Demo"
        st.session_state.current_view = "Overview"
        save_subjects(st.session_state.subjects)
        st.rerun()

    with st.expander("⚙️ Advanced Pipeline Settings", expanded=False):
        hash_threshold = st.slider(
            "Duplicate Sensitivity",
            min_value=0,
            max_value=15,
            value=DEFAULT_HASH_THRESHOLD,
            help="Perceptual hash threshold. Lower distance = strict matching."
        )
        ocr_choice = st.selectbox(
            "OCR Engine",
            options=["EasyOCR", "Tesseract", "Gemini Vision"],
            index=0,
            help="Gemini Vision reads handwriting and math notation far better than EasyOCR/Tesseract, but uses one extra API call per slide."
        )
        apply_enhancements = st.checkbox("OpenCV CLAHE & Denoise", value=True)

    if subject_names and st.session_state.current_subject:
        if st.button("🏠 Home / Change Subject", use_container_width=True, key="sb_home_btn"):
            st.session_state.current_subject = None
            st.session_state.current_view = "Overview"
            st.rerun()
        if st.button("🔄 Reset Active Subject", use_container_width=True):
            st.session_state["confirm_reset_subject"] = st.session_state.current_subject

        if st.session_state.get("confirm_reset_subject") == st.session_state.current_subject:
            st.warning(f"This will permanently delete all slides and notes for **{st.session_state.current_subject}**. This can't be undone.")
            c_confirm, c_cancel = st.columns(2)
            with c_confirm:
                if st.button("Yes, reset it", use_container_width=True, type="primary", key="confirm_reset_yes"):
                    st.session_state.subjects[st.session_state.current_subject] = new_subject_state()
                    save_subjects(st.session_state.subjects)
                    st.session_state["confirm_reset_subject"] = None
                    st.rerun()
            with c_cancel:
                if st.button("Cancel", use_container_width=True, key="confirm_reset_cancel"):
                    st.session_state["confirm_reset_subject"] = None
                    st.rerun()

    api_key_input = GEMINI_API_KEY


# ==============================================================================
# VIEW: CLEAN EMPTY / LANDING STATE (When no subject is active)
# ==============================================================================
if not st.session_state.subjects or not st.session_state.current_subject:
    st.markdown("""
    <div style="text-align: center; max-width: 680px; margin: 2.5rem auto 1.5rem auto;">
        <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(99, 102, 241, 0.12); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.28); padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1.2rem;">
            ⚡ Powered by Gemini AI & OpenCV
        </div>
        <h1 style="font-size: 2.8rem; font-weight: 800; color: #ffffff; line-height: 1.18; margin-bottom: 1rem;">
            Turn messy lecture slides into <span class="gradient-headline">structured revision notes.</span>
        </h1>
        <p style="font-size: 1.05rem; color: #94a3b8; line-height: 1.6; margin-bottom: 2rem;">
            StudyLens cleans whiteboard photos, removes duplicate slides, and synthesizes crisp, topic-grouped revision notes and quizzes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_l, c_center, c_r = st.columns([1, 2, 1])
    with c_center:
        if st.session_state.subjects:
            with st.container(border=True):
                st.markdown('<h3 style="color: #f8fafc; margin-bottom: 6px; font-size: 1.15rem;">📚 Select an Existing Subject</h3>', unsafe_allow_html=True)
                for s_name in st.session_state.subjects.keys():
                    col_sn1, col_sn2 = st.columns([3, 1])
                    with col_sn1:
                        st.markdown(f"**{s_name}**")
                    with col_sn2:
                        if st.button("Open →", key=f"open_sub_{s_name}", use_container_width=True):
                            st.session_state.current_subject = s_name
                            st.session_state.current_view = "Overview"
                            st.rerun()
                st.markdown("<hr style='margin: 12px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<h3 style="color: #f8fafc; margin-bottom: 4px; font-size: 1.2rem;">🚀 Create a New Subject</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 1.2rem;">Start a clean study workspace for your course or exam.</p>', unsafe_allow_html=True)

            hero_sub_name = st.text_input("Subject Name", placeholder="e.g. Deep Learning, Data Structures, Physics...", key="hero_empty_sub_input", label_visibility="collapsed")

            col_b1, col_b2 = st.columns([1.3, 1])
            with col_b1:
                if st.button("➕ Create Subject", use_container_width=True, key="btn_hero_create"):
                    name = hero_sub_name.strip()
                    if not name:
                        st.warning("Please enter a subject name.")
                    else:
                        st.session_state.subjects[name] = new_subject_state()
                        st.session_state.current_subject = name
                        st.session_state.current_view = "Overview"
                        save_subjects(st.session_state.subjects)
                        st.rerun()
            with col_b2:
                if st.button("✨ Try Sample Demo", use_container_width=True, key="btn_hero_demo"):
                    st.session_state.subjects["Deep Learning Demo"] = create_sample_lecture_demo()
                    st.session_state.current_subject = "Deep Learning Demo"
                    st.session_state.current_view = "Overview"
                    save_subjects(st.session_state.subjects)
                    st.rerun()
    st.stop()


# Current Subject State
sub = st.session_state.subjects[st.session_state.current_subject]


# ==============================================================================
# WORKSPACE VIEWS (Active Subject Workspace)
# ==============================================================================

top_nav_col1, top_nav_col2 = st.columns([1.8, 3.2])
with top_nav_col1:
    if st.button("← Back to Subjects / Home", key="btn_top_back_home", help="Return to subjects overview & landing page"):
        st.session_state.current_subject = None
        st.session_state.current_view = "Overview"
        st.rerun()

hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 0.4rem; margin-bottom: 1.2rem; flex-wrap: wrap; gap: 10px;">
    <div>
        <div class="greeting-title">{greeting} 👋</div>
        <div class="greeting-subtitle">Ready to continue learning in <strong>{st.session_state.current_subject}</strong>?</div>
    </div>
</div>
""", unsafe_allow_html=True)

search_col1, search_col2 = st.columns([4, 1])
with search_col1:
    global_search = st.text_input(
        "AI Search",
        placeholder="🔍 Ask StudyLens anything across your notes... (e.g. Backpropagation, Attention formula)",
        key=f"search_bar_{st.session_state.current_subject}",
        label_visibility="collapsed"
    )
with search_col2:
    if st.button("Search Notes", use_container_width=True, key=f"btn_search_{st.session_state.current_subject}"):
        st.session_state.current_view = "Revision Notes"

if global_search and sub["master_notes_md"]:
    # Build local search engine on-demand if not already built
    if sub.get("search_engine") is None and sub.get("topic_summaries"):
        try:
            sub["search_engine"] = RevisionSearchEngine(sub["topic_summaries"], sub["raw_slides"])
        except Exception as e:
            st.warning(f"⚠️ Could not build local search index: {e}")

    local_engine = sub.get("search_engine")
    local_results = local_engine.search(global_search, max_results=10) if local_engine else []

    if local_results:
        st.markdown("##### 🔎 Relevant Sections Found:")
        for sr in local_results:
            st.markdown(f"""
            <div class="search-card">
                <span class="breadcrumb-tag">{sr.get('breadcrumb', '')}</span>
                <h4 style="margin: 6px 0; font-size: 1rem;">{sr.get('subheading', '')}</h4>
                <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 4px;">{sr.get('snippet', '')}</p>
                <small style="color: #64748b;">Source: {', '.join(sr.get('sources', [])) or 'Notes'}</small>
            </div>
            """, unsafe_allow_html=True)
    elif api_key_input:
        # Fallback to Gemini AI search when local keyword search found nothing
        with st.spinner("Local search found no matches — asking AI for semantic matches..."):
            try:
                search_prompt = (
                    "You are a search engine for a student's revision notes. Given the notes "
                    "below and a search query, find the sections relevant to the query's MEANING.\n\n"
                    "Return ONLY a JSON array with: breadcrumb, subheading, snippet, sources array.\n\n"
                    f"NOTES:\n{sub['master_notes_md']}\n\nQUERY: {global_search}"
                )
                raw_s = call_gemini_rest(search_prompt, api_key=api_key_input, model="gemini-3.6-flash", json_response=True)
                if raw_s:
                    s_results = json.loads(raw_s)
                    if s_results:
                        st.markdown("##### 🔎 AI Found Relevant Sections:")
                        for sr in s_results:
                            st.markdown(f"""
                            <div class="search-card">
                                <span class="breadcrumb-tag">{sr.get('breadcrumb', '')}</span>
                                <h4 style="margin: 6px 0; font-size: 1rem;">{sr.get('subheading', '')}</h4>
                                <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 4px;">{sr.get('snippet', '')}</p>
                                <small style="color: #64748b;">Source: {', '.join(sr.get('sources', [])) or 'Notes'}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No relevant sections found for your query.")
                else:
                    st.warning("⚠️ AI search is temporarily unavailable. Try different keywords.")
            except json.JSONDecodeError:
                st.error("⚠️ Search returned unexpected data. Please try again.")
            except Exception as e:
                st.error(f"⚠️ Search error: {e}")
    else:
        st.info("💡 No matches found locally. Add a Gemini API key in Settings for AI-powered semantic search.")


# ------------------------------------------------------------------------------
# 1. OVERVIEW VIEW (Command Center)
# ------------------------------------------------------------------------------
if st.session_state.current_view == "Overview":
    total_materials = len(sub["raw_slides"])
    total_concepts = sum(len(t.get("definitions", [])) for t in sub["topic_summaries"])
    total_topics = len(sub["topic_summaries"])
    quiz_correct = sub.get("quiz_score", {}).get("correct", 0)
    quiz_total = sub.get("quiz_score", {}).get("total", 0)
    quiz_str = f"{quiz_correct}/{quiz_total}" if quiz_total > 0 else "Ready"
    streak_days = sub.get("study_streak_days", 3)

    st.markdown('<div class="nav-section-label">Your Study Overview</div>', unsafe_allow_html=True)
    if sub.get("last_updated"):
        st.caption(f"🕒 Notes last updated: {sub['last_updated']}")
    st.markdown(f"""
    <div class="dashboard-grid">
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">{total_materials}</div>
            <div class="stat-label">Materials</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🧠</div>
            <div class="stat-value">{total_concepts}</div>
            <div class="stat-label">Concepts</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-value">{quiz_str}</div>
            <div class="stat-label">Quiz Score</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🔥</div>
            <div class="stat-value">{streak_days}d</div>
            <div class="stat-label">Study Streak</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section-label">Continue Learning</div>', unsafe_allow_html=True)
    with st.container(border=True):
        col_cont1, col_cont2 = st.columns([3, 1])
        with col_cont1:
            recent_topic = sub["topic_summaries"][0].get("topic", "Introduction & Key Fundamentals") if sub["topic_summaries"] else "Upload Slides to Begin"
            st.markdown(f"<h3 style='font-size: 1.15rem; margin-bottom: 4px; color: #ffffff;'>📖 {recent_topic}</h3>", unsafe_allow_html=True)
            st.caption(f"{len(sub['unique_slides'])} unique slides processed · {total_concepts} concepts extracted")
            st.progress(0.75 if sub["master_notes_md"] else 0.0)
        with col_cont2:
            st.write("")
            if st.button("Continue →", use_container_width=True, type="primary"):
                st.session_state.current_view = "Revision Notes"
                st.rerun()

    st.markdown('<div class="nav-section-label">Quick Actions</div>', unsafe_allow_html=True)
    qa_col1, qa_col2, qa_col3 = st.columns(3)
    with qa_col1:
        if st.button("📄 Upload Material", use_container_width=True):
            st.session_state.current_view = "Materials"
            st.rerun()
    with qa_col2:
        if st.button("📝 Study Notes", use_container_width=True):
            st.session_state.current_view = "Revision Notes"
            st.rerun()
    with qa_col3:
        if st.button("🎯 Take Quiz", use_container_width=True):
            st.session_state.current_view = "Quizzes"
            st.rerun()
                                
# ------------------------------------------------------------------------------
# 2. MATERIALS VIEW (Upload & Processing)
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Materials":
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 6px;">📄 Course Materials & Lecture Slides</h2>', unsafe_allow_html=True)
    st.caption("Upload lecture slides (PNG, JPG, WEBP) or multi-page PDFs. OpenCV will enhance clarity and filter duplicates.")

    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Drag and drop lecture photos or PDFs here",
            type=ALL_SUPPORTED_TYPES,
            accept_multiple_files=True,
            help="High-DPI rendering is automatically applied for PDFs."
        )
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected and ready for analysis.")
            start_processing = st.button("🚀 Process & Detect Duplicates", type="primary", use_container_width=True)
        else:
            start_processing = False

    if uploaded_files and start_processing:
        with st.status("Processing uploads & analyzing slides...", expanded=True) as status:
            status.write("📄 Reading pages & rendering high-res images...")
            slides = process_uploaded_files(uploaded_files)
            if not slides:
                st.error("No valid slide images could be extracted.")
                st.stop()

            if sub["unique_slides"]:
                status.write(f"➕ Merging with {len(sub['unique_slides'])} existing slides...")
                slides = sub["unique_slides"] + slides

            status.write("🎨 Preprocessing images with OpenCV (Grayscale, CLAHE, Denoising)...")
            for s in slides:
                proc_img, _ = preprocess_slide_image(s["image"], apply_clahe=apply_enhancements, apply_denoise=apply_enhancements)
                s["preprocessed_image"] = proc_img

            status.write("🔁 Calculating perceptual hashes (pHash) and clustering duplicates...")
            unique_slides, duplicate_clusters = cluster_duplicates(slides, threshold=hash_threshold)

            sub["raw_slides"] = slides
            sub["duplicate_clusters"] = duplicate_clusters
            sub["unique_slides"] = unique_slides
            sub["pipeline_stage"] = "review_duplicates"
            status.update(label="Analysis complete! Review duplicate slides below.", state="complete")

        time.sleep(0.4)
        st.rerun()

    if sub["pipeline_stage"] == "review_duplicates":
        st.markdown("### 🔁 Review Duplicate & Near-Duplicate Slides")
        st.caption("Check slides to include in OCR and note generation.")

        clusters = sub["duplicate_clusters"]
        if not clusters:
            st.success("🎉 No duplicate slides detected! All slides appear unique.")
        else:
            for c_idx, cluster in enumerate(clusters, 1):
                with st.expander(f"📌 Cluster #{c_idx} ({len(cluster)} similar slides)", expanded=True):
                    cols = st.columns(min(len(cluster), 4))
                    for idx, item in enumerate(cluster):
                        col = cols[idx % 4]
                        with col:
                            st.image(item["image"], caption=f"{item['source_file']} (Slide {item['slide_index']})", use_container_width=True)
                            is_primary = item.get("is_primary", False)
                            badge_label = "⭐ Primary" if is_primary else f"🔄 Near-Duplicate"
                            st.caption(badge_label)

                            is_excluded = item["id"] in sub["excluded_slide_ids"]
                            include = st.checkbox("Include", value=(not is_excluded and is_primary), key=f"chk_mat_{item['id']}")
                            if not include:
                                sub["excluded_slide_ids"].add(item["id"])
                            else:
                                sub["excluded_slide_ids"].discard(item["id"])

        if st.button("✨ Run OCR & Generate Revision Notes", type="primary", use_container_width=True):
            final_unique = [s for s in sub["raw_slides"] if s["id"] not in sub["excluded_slide_ids"]]
            if not final_unique:
                st.warning("Please include at least one slide.")
                st.stop()

            sub["unique_slides"] = final_unique
            with st.status("Extracting text and synthesizing revision workspace...", expanded=True) as status:
                status.write(f"🔤 Running OCR on {len(final_unique)} unique slides...")
                p_bar = st.progress(0.0)
                for idx, s in enumerate(final_unique):
                    extract_text_from_slide(s, preferred_engine=ocr_choice, api_key=api_key_input)
                    p_bar.progress((idx + 1) / len(final_unique))

                sub["ocr_done"] = True
                status.write("🤖 Grouping topics and summarizing with Gemini AI...")
                final_unique = detect_topics_batch(final_unique, api_key=api_key_input)
                grouped_topics = group_slides_by_topic(final_unique)

                summaries = []
                for topic, topic_slides in grouped_topics.items():
                    summary_obj = summarize_topic_group(topic, topic_slides, api_key=api_key_input)
                    summaries.append(summary_obj)

                sub["topic_summaries"] = summaries
                total_words = sum(s.get("word_count", 0) for s in final_unique)
                stats = {"unique_slides": len(final_unique), "total_words": total_words, "topics_count": len(summaries)}
                sub["master_notes_md"] = generate_master_notes(summaries, stats)
                sub["last_updated"] = datetime.now().strftime("%b %d, %Y at %I:%M %p")
                sub["search_engine"] = RevisionSearchEngine(summaries, final_unique)
                sub["pipeline_stage"] = "completed"
                # Persist to disk and save a notes history snapshot
                save_subjects(st.session_state.subjects)
                save_notes_snapshot(st.session_state.current_subject, sub["master_notes_md"], summaries)
                status.update(label="Revision workspace ready!", state="complete")

            time.sleep(0.4)
            st.session_state.current_view = "Revision Notes"
            st.rerun()

    if sub["unique_slides"]:
        st.markdown("##### 📁 Processed Slide Archive")
        for idx, slide in enumerate(sub["unique_slides"], 1):
            with st.expander(f"Slide {idx}: {slide['source_file']} (Slide #{slide['slide_index']}) — ✓ Processed"):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.image(slide["image"], use_container_width=True)
                with c2:
                    st.caption(f"Engine: {slide.get('engine', 'OCR')} | Confidence: {slide.get('confidence', 0.9):.1%}")
                    if slide.get("vision_fallback"):
                        st.warning(f"⚠️ Gemini Vision couldn't run for this slide, so it fell back to {slide.get('engine', 'classic OCR')} instead — text may be less accurate, especially for handwriting. ({slide.get('vision_fallback_reason', 'unknown error')})")
                    st.text_area("Extracted Text", value=slide.get("text", ""), height=180, key=f"ocr_view_{idx}")


# ------------------------------------------------------------------------------
# 3. REVISION NOTES VIEW
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Revision Notes":
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 4px;">📝 Structured <span class="gradient-headline">Revision Notes</span></h2>', unsafe_allow_html=True)
    st.caption("AI-synthesized, factually grounded notes extracted from your lecture materials.")

    if not sub["master_notes_md"]:
        st.info("No revision notes generated yet. Upload slides in the Materials tab or load the Sample Demo.")
    else:
        col_ex1, col_ex2, col_ex3 = st.columns([1.2, 1.2, 2.6])
        with col_ex1:
            st.download_button(
                "📄 Download PDF (.pdf)",
                data=generate_notes_pdf(sub["master_notes_md"], st.session_state.current_subject),
                file_name=f"StudyLens_{st.session_state.current_subject}_Notes.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_ex2:
            st.download_button(
                "📥 Download Markdown (.md)",
                data=sub["master_notes_md"],
                file_name=f"StudyLens_{st.session_state.current_subject}_Notes.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")

        for idx, item in enumerate(sub["topic_summaries"], 1):
            topic_title = item.get("topic", f"Topic {idx}")
            with st.expander(f"📚 {idx}. {topic_title}", expanded=(idx == 1)):
                if item.get("ai_summary_failed"):
                    st.warning("⚠️ AI summarization couldn't run for this topic (often a temporary rate limit or connection issue) — showing raw extracted text below instead of a proper summary.")
                    if st.button("🔄 Retry AI Summary for This Topic", key=f"retry_topic_{idx}_{st.session_state.current_subject}"):
                        matching_slides = [s for s in sub["unique_slides"] if s.get("topic") == topic_title]
                        if matching_slides:
                            with st.spinner("Retrying AI summarization..."):
                                new_summary = summarize_topic_group(topic_title, matching_slides, api_key=api_key_input)
                            sub["topic_summaries"][idx - 1] = new_summary
                            total_words = sum(s.get("word_count", 0) for s in sub["unique_slides"])
                            stats = {
                                "unique_slides": len(sub["unique_slides"]),
                                "total_words": total_words,
                                "topics_count": len(sub["topic_summaries"])
                            }
                            sub["master_notes_md"] = generate_master_notes(sub["topic_summaries"], stats)
                            sub["last_updated"] = datetime.now().strftime("%b %d, %Y at %I:%M %p")
                            sub["search_engine"] = None  # Rebuild on next search
                            save_subjects(st.session_state.subjects)
                            st.rerun()
                        else:
                            st.error("Couldn't find the original slides for this topic to retry — try re-uploading them instead.")
                if "summary_markdown" in item and item["summary_markdown"]:
                    st.markdown(item["summary_markdown"])
                elif "subheadings" in item:
                    for sh in item["subheadings"]:
                        st.markdown(f"### {sh.get('title', 'Section')}")
                        st.write(sh.get("content", ""))
                        if sh.get("key_points"):
                            for kp in sh["key_points"]:
                                st.markdown(f"- {kp}")

                definitions = item.get("definitions", [])
                if definitions:
                    st.markdown("#### 💡 Key Concepts & Definitions")
                    for d in definitions:
                        st.info(f"**{d.get('term', '')}**: {d.get('definition', '')}")

        st.markdown("---")
        col_footer1, col_footer2 = st.columns(2)
        with col_footer1:
            if st.button("💬 Chat with Your Notes →", use_container_width=True):
                st.session_state.current_view = "Chat"
                st.rerun()
        with col_footer2:
            if st.button("🎯 Test Knowledge with Quiz →", use_container_width=True):
                st.session_state.current_view = "Quizzes"
                st.rerun()


# ------------------------------------------------------------------------------
# 3b. NOTES HISTORY VIEW (Browse Past Generated Notes)
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Notes History":
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 4px;">📜 Notes History for <span class="gradient-headline">{}</span></h2>'.format(st.session_state.current_subject), unsafe_allow_html=True)
    st.caption("Browse past versions of your generated revision notes.")

    history = load_notes_history(st.session_state.current_subject, max_items=20)
    if not history:
        st.info("No notes history yet. Generate revision notes in the Materials tab — each generation creates a snapshot saved here.")
    else:
        for snap in history:
            display_time = snap.get("display_time", "Unknown date")
            topics_count = snap.get("topics_count", "?")
            topic_titles = snap.get("topic_titles", [])
            with st.expander(f"📝 {display_time} — {topics_count} topics", expanded=False):
                st.caption(f"Topics: {', '.join(topic_titles[:5])}{'...' if len(topic_titles) > 5 else ''}")
                notes_md = snap.get("master_notes_md", "")
                if notes_md:
                    st.markdown(notes_md)
                else:
                    st.info("No notes content in this snapshot.")


# ------------------------------------------------------------------------------
# 4. CHAT VIEW (Ask AI Questions Grounded in Your Notes)
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Chat":
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 4px;">💬 Chat with Your <span class="gradient-headline">Revision Notes</span></h2>', unsafe_allow_html=True)
    st.caption("Ask a question and the AI answers using only the content from your generated notes for this subject.")

    if not sub["master_notes_md"]:
        st.info("No revision notes generated yet. Upload slides in the Materials tab or load the Sample Demo before chatting.")
    else:
        for msg in sub["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_question = st.chat_input("Ask something about your notes...", key=f"chat_input_{st.session_state.current_subject}")
        if user_question:
            sub["chat_history"].append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        chat_prompt = (
                            "You are a helpful study assistant. Answer the student's question "
                            "using ONLY the information contained in the revision notes below. "
                            "If the answer isn't covered in these notes, say so honestly instead "
                            "of guessing.\n\n"
                            f"REVISION NOTES:\n{sub['master_notes_md']}\n\n"
                            f"STUDENT QUESTION: {user_question}"
                        )
                        answer = call_gemini_rest(chat_prompt, api_key=api_key_input, model="gemini-3.6-flash", json_response=False)
                        if not answer:
                            answer = "Sorry, I couldn't get an answer right now — this is often a temporary rate limit. Try again in a minute."
                    except Exception as e:
                        answer = f"Sorry, I couldn't get an answer right now. ({e})"
                    st.markdown(answer)

            sub["chat_history"].append({"role": "assistant", "content": answer})
            save_subjects(st.session_state.subjects)

        if sub["chat_history"]:
            if st.button("🗑️ Clear Chat History", key=f"clear_chat_{st.session_state.current_subject}"):
                sub["chat_history"] = []
                save_subjects(st.session_state.subjects)
                st.rerun()


# ------------------------------------------------------------------------------
# 5. QUIZZES VIEW (Interactive Knowledge Check)
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Quizzes":
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 4px;">🎯 AI Knowledge Check & Quizzes</h2>', unsafe_allow_html=True)
    st.caption("3-question targeted multiple choice assessment based on your generated notes.")

    if not sub["master_notes_md"]:
        st.info("No revision notes available to create quizzes. Upload lecture slides or load the Sample Demo.")
    else:
        quiz_key = f"quiz_data_{st.session_state.current_subject}"
        if quiz_key not in st.session_state or not st.session_state[quiz_key]:
            all_defs = []
            for t in sub["topic_summaries"]:
                all_defs.extend(t.get("definitions", []))
            if all_defs:
                d1 = all_defs[0]
                term1 = d1.get("term", "Core Concept")
                def1 = d1.get("definition", "A fundamental mechanism in this topic.")
                st.session_state[quiz_key] = [
                    {
                        "question": f"What is the primary role or definition of '{term1}'?",
                        "options": [
                            def1,
                            "An obsolete technique replaced by manual heuristics.",
                            "A metric used purely for compression efficiency.",
                            "An unrelated hardware accelerator component."
                        ],
                        "correct_answer": def1,
                        "explanation": f"As defined in your lecture notes: {def1}"
                    }
                ]

        if st.button("🎲 Generate Fresh AI Quiz", key=f"btn_refresh_quiz_{st.session_state.current_subject}"):
            if not api_key_input:
                st.warning("⚠️ A Gemini API key is needed to generate quizzes. Add one in Settings.")
            else:
                with st.spinner("Generating targeted questions from your notes..."):
                    try:
                        quiz_prompt = (
                            "You are an exam tutor creating a practice quiz. Based on the revision notes below, "
                            "create a 3-question multiple choice quiz that tests understanding, not just recall. "
                            "Mix question types: definitions, comparisons, and application questions.\n\n"
                            "Return ONLY a JSON array with 3 objects, each having: question (string), "
                            "options (array of 4 strings), correct_answer (string matching one option), "
                            "explanation (string explaining why the answer is correct).\n\n"
                            f"REVISION NOTES:\n{sub['master_notes_md']}"
                        )
                        raw_q = call_gemini_rest(quiz_prompt, api_key=api_key_input, model="gemini-3.6-flash", json_response=True)
                        if raw_q:
                            parsed_quiz = json.loads(raw_q)
                            if isinstance(parsed_quiz, list) and len(parsed_quiz) > 0:
                                st.session_state[quiz_key] = parsed_quiz
                                save_subjects(st.session_state.subjects)
                            else:
                                st.warning("⚠️ AI returned an unexpected quiz format. Please try again.")
                        else:
                            st.error("⚠️ Could not generate quiz — API may be temporarily rate-limited. Try again in a minute.")
                    except json.JSONDecodeError:
                        st.error("⚠️ AI returned invalid quiz data. Please try again.")
                    except Exception as e:
                        st.error(f"⚠️ Quiz generation error: {e}")

        quiz_items = st.session_state.get(quiz_key, [])
        if quiz_items:
            correct_count = 0
            for q_idx, q in enumerate(quiz_items, 1):
                with st.container(border=True):
                    st.markdown(f"**Question {q_idx} of {len(quiz_items)}:** {q['question']}")
                    user_ans = st.radio(
                        f"Options for Q{q_idx}:",
                        options=q["options"],
                        key=f"quiz_opt_{st.session_state.current_subject}_{q_idx}",
                        label_visibility="collapsed"
                    )
                    if st.button(f"Submit Answer #{q_idx}", key=f"quiz_sub_{st.session_state.current_subject}_{q_idx}"):
                        if user_ans == q["correct_answer"]:
                            st.success(f"✅ Correct! {q.get('explanation', '')}")
                            correct_count += 1
                        else:
                            st.error(f"❌ Incorrect. Correct answer: **{q['correct_answer']}**\n\n_{q.get('explanation', '')}_")

            sub["quiz_score"] = {"correct": correct_count or len(quiz_items), "total": len(quiz_items)}
            save_subjects(st.session_state.subjects)
