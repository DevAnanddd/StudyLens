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

    :root {
        --sl-bg0: #07070d;
        --sl-bg1: #0b0b16;
        --sl-card: rgba(15, 15, 29, 0.88);
        --sl-pink: #ec4899;
        --sl-blue: #3b82f6;
        --sl-purple: #a855f7;
        --sl-magenta: #d946ef;
        --sl-cyan: #22d3ee;
        --sl-emerald: #10b981;
        --sl-text: #f1f5f9;
        --sl-text-soft: #94a3b8;
        --sl-primary-grad: linear-gradient(135deg, #ec4899 0%, #a855f7 55%, #d946ef 100%);
        --sl-border: rgba(255, 255, 255, 0.08);
    }

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
        0%, 100% { box-shadow: 0 0 8px rgba(236, 72, 153, 0.3); }
        50% { box-shadow: 0 0 20px rgba(236, 72, 153, 0.6); }
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
    @keyframes shimmer {
        0% { transform: translateX(-120%) skewX(-20deg); }
        100% { transform: translateX(220%) skewX(-20deg); }
    }
    @keyframes spinSlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes orbPulse {
        0%, 100% { opacity: 0.35; transform: scale(1) translateY(0); }
        50% { opacity: 0.7; transform: scale(1.12) translateY(-14px); }
    }
    @keyframes nodePulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    @keyframes dashFlow {
        to { stroke-dashoffset: -1000; }
    }

    .stApp {
        background:
            radial-gradient(65% 55% at 12% 6%, rgba(236, 72, 153, 0.30) 0%, transparent 60%),
            radial-gradient(55% 48% at 90% 10%, rgba(217, 70, 239, 0.20) 0%, transparent 60%),
            radial-gradient(60% 45% at 50% 97%, rgba(59, 130, 246, 0.16) 0%, transparent 60%),
            radial-gradient(40% 30% at 78% 78%, rgba(236, 72, 153, 0.10) 0%, transparent 55%),
            linear-gradient(180deg, #050508 0%, var(--sl-bg1) 45%, #050508 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--sl-text);
        letter-spacing: -0.01em;
    }
    /* Animated neural-constellation backdrop overlay */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(34, 211, 238, 0.12) 0px, transparent 1.5px),
            radial-gradient(circle at 25% 40%, rgba(217, 70, 239, 0.12) 0px, transparent 1.5px),
            radial-gradient(circle at 40% 15%, rgba(59, 130, 246, 0.12) 0px, transparent 1.5px),
            radial-gradient(circle at 65% 55%, rgba(34, 211, 238, 0.10) 0px, transparent 1.5px),
            radial-gradient(circle at 80% 30%, rgba(217, 70, 239, 0.10) 0px, transparent 1.5px),
            radial-gradient(circle at 90% 70%, rgba(236, 72, 153, 0.10) 0px, transparent 1.5px),
            radial-gradient(circle at 15% 80%, rgba(34, 211, 238, 0.08) 0px, transparent 1.5px),
            radial-gradient(circle at 55% 85%, rgba(59, 130, 246, 0.08) 0px, transparent 1.5px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-repeat: no-repeat;
        animation: nodePulse 4s ease-in-out infinite;
    }
    /* Floating glow orbs */
    .stApp::after {
        content: '';
        position: fixed;
        pointer-events: none;
        z-index: 0;
        inset: 0;
        margin: auto;
        width: 520px;
        height: 520px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(217, 70, 239, 0.16) 0%, transparent 70%);
        filter: blur(60px);
        animation: orbPulse 9s ease-in-out infinite;
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
        background-color: #0a0a14 !important;
        background-image: linear-gradient(180deg, rgba(236, 72, 153, 0.08), rgba(7, 7, 14, 0) 42%), linear-gradient(0deg, rgba(217, 70, 239, 0.05), rgba(7, 7, 14, 0) 32%) !important;
        border-right: 1px solid rgba(34, 211, 238, 0.14) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.2rem 0 !important;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 0 16px 0;
        animation: fadeInDown 0.4s ease-out;
        position: relative;
    }
    .sidebar-brand-icon {
        font-size: 1.4rem;
        color: #e879f9;
        animation: float 3s ease-in-out infinite;
        position: relative;
    }
    .sidebar-brand-icon::after {
        content: '';
        position: absolute;
        inset: -7px;
        border: 1.5px dashed rgba(34, 211, 238, 0.5);
        border-radius: 50%;
        animation: spinSlow 12s linear infinite;
    }
    .sidebar-brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #ffffff 0%, #a5f3fc 45%, #f0abfc 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 5s ease infinite;
        position: relative;
    }
    .sidebar-brand-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .nav-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8b9cc0;
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
    .subject-chip {
        display: inline-block;
        padding: 2px 11px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.92rem;
        color: #f0abfc;
        background: rgba(217, 70, 239, 0.10);
        border: 1px solid rgba(217, 70, 239, 0.32);
        box-shadow: 0 2px 12px rgba(217, 70, 239, 0.18);
        vertical-align: middle;
    }
    .gradient-headline {
        background: linear-gradient(90deg, #22d3ee 0%, #a855f7 35%, #3b82f6 55%, #d946ef 80%, #22d3ee 100%);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline;
        animation: gradientShift 4s ease infinite;
        position: relative;
    }
    .gradient-headline::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
        width: 60%;
        animation: shimmer 3s ease-in-out infinite;
        pointer-events: none;
    }
    .stButton > button {
        background: var(--sl-primary-grad) !important;
        background-size: 180% auto !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.15rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 14px rgba(236, 72, 153, 0.30), inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button[kind="secondary"], .stButton > button[pkind="secondary"], .stFormSubmitButton > button[kind="secondary"] {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.14), rgba(217, 70, 239, 0.10)) !important;
        backdrop-filter: blur(10px);
        color: #e2e8f0 !important;
        border: 1px solid rgba(34, 211, 238, 0.30) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.15rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button[kind="secondary"]:hover, .stButton > button[pkind="secondary"]:hover {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.26), rgba(217, 70, 239, 0.18)) !important;
        border-color: rgba(236, 72, 153, 0.55) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(236, 72, 153, 0.28) !important;
    }
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 0;
        left: -10%;
        width: 40%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
        transform: skewX(-20deg);
        animation: shimmer 3.5s ease-in-out infinite;
        pointer-events: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        background-position: right center !important;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.45) !important;
        border-color: rgba(255, 255, 255, 0.32) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) scale(0.98) !important;
    }
    .stDownloadButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.12), rgba(217, 70, 239, 0.08)) !important;
        backdrop-filter: blur(8px);
        color: #f8fafc !important;
        border: 1px solid rgba(34, 211, 238, 0.28) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.24), rgba(217, 70, 239, 0.16)) !important;
        border-color: #a855f7 !important;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(150deg, rgba(20, 18, 38, 0.85), rgba(13, 12, 25, 0.9)) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 1.8rem !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
        position: relative;
        overflow: hidden;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(34, 211, 238, 0.35) !important;
        box-shadow: 0 14px 40px rgba(37, 99, 235, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]::after {
        content: '';
        position: absolute;
        top: 0; left: 12%; right: 12%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.6), transparent);
        pointer-events: none;
    }
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin: 1rem 0 1.8rem 0;
    }
    .stat-card {
        background: linear-gradient(160deg, rgba(21, 19, 40, 0.9), rgba(14, 13, 27, 0.92));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px 14px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 16px;
        background: radial-gradient(120% 120% at 50% 0%, rgba(34, 211, 238, 0.18) 0%, transparent 55%);
        opacity: 0;
        transition: opacity 0.25s ease;
        pointer-events: none;
    }
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(34, 211, 238, 0.55);
        box-shadow: 0 12px 34px rgba(236, 72, 153, 0.22);
    }
    .stat-card:hover::before { opacity: 1; }
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
        background: rgba(17, 16, 32, 0.6);
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
        color: #22d3ee;
        border-color: rgba(236, 72, 153, 0.4);
        font-weight: 600;
    }
    .pipeline-step.pending {
        color: #64748b;
    }
    .breadcrumb-tag {
        background-color: rgba(236, 72, 153, 0.15);
        color: #e879f9;
        border: 1px solid rgba(236, 72, 153, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .search-card {
        background: linear-gradient(145deg, rgba(19, 17, 36, 0.85), rgba(14, 13, 27, 0.9));
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #ec4899;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .search-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -10%;
        width: 50%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.06), transparent);
        transform: skewX(-20deg);
        animation: shimmer 5s ease-in-out infinite;
        pointer-events: none;
    }
    .search-card:hover {
        border-left-color: #e879f9;
        border-color: rgba(34, 211, 238, 0.35);
        box-shadow: 0 10px 32px rgba(236, 72, 153, 0.22);
        transform: translateY(-3px);
    }
    .quick-action-btn {
        background: rgba(17, 16, 32, 0.8);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .quick-action-btn:hover {
        border-color: #22d3ee;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.15);
    }
    .streamlit-expanderHeader {
        background-color: rgba(17, 16, 32, 0.7) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        color: #f8fafc !important;
        transition: all 0.25s ease !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: rgba(34, 211, 238, 0.35) !important;
        box-shadow: 0 4px 14px rgba(236, 72, 153, 0.12) !important;
    }
    ::selection {
        background: rgba(34, 211, 238, 0.45);
        color: #ffffff;
    }
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(10, 9, 20, 0.6);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ec4899, #d946ef);
        border-radius: 8px;
        border: 2px solid #05050a;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ec4899, #a855f7);
    }
    .gradient-divider {
        height: 1.5px;
        border: none;
        margin: 1.4rem 0;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.7), rgba(236, 72, 153, 0.7), transparent);
        position: relative;
    }
    .feature-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(145deg, rgba(24, 20, 44, 0.8), rgba(19, 17, 36, 0.9));
        border: 1px solid rgba(34, 211, 238, 0.3);
        border-radius: 9999px;
        padding: 8px 16px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #a5f3fc;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transition: all 0.25s ease;
    }
    .feature-chip:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.6);
        box-shadow: 0 8px 22px rgba(217, 70, 239, 0.28);
    }
    /* ── Landing feature grid & pipeline strip ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        margin: 1.6rem auto 0.4rem auto;
        max-width: 720px;
    }
    .feature-card {
        background: linear-gradient(150deg, rgba(21, 19, 40, 0.8), rgba(12, 11, 24, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 12px;
        text-align: left;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0; left: 20%; right: 20%;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.6), transparent);
    }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(168, 85, 247, 0.5);
        box-shadow: 0 12px 30px rgba(236, 72, 153, 0.22);
    }
    .feature-card-icon { font-size: 1.3rem; margin-bottom: 6px; }
    .feature-card-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 3px;
    }
    .feature-card-desc {
        font-size: 0.74rem;
        color: #94a3b8;
        line-height: 1.4;
    }
    .pipeline-strip {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        margin: 1rem auto 0 auto;
        font-size: 0.76rem;
        font-weight: 600;
        color: #e879f9;
    }
    .pipeline-strip span {
        background: rgba(236, 72, 153, 0.12);
        border: 1px solid rgba(34, 211, 238, 0.25);
        padding: 5px 12px;
        border-radius: 9999px;
        color: #a5f3fc;
        transition: all 0.2s ease;
    }
    .pipeline-strip span:hover {
        background: rgba(236, 72, 153, 0.24);
        transform: translateY(-2px);
    }
    .pipeline-strip i { color: #f0abfc; font-size: 0.85rem; }
    /* ── View title (gradient) ── */
    .view-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        background: linear-gradient(92deg, #a5f3fc 0%, #e879f9 30%, #a855f7 55%, #f0abfc 80%, #3b82f6 100%);
        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
        margin-bottom: 4px;
        animation: gradientShift 6s ease infinite;
    }
    .view-subtitle {
        font-size: 0.88rem;
        color: #94a3b8;
        margin-bottom: 1.4rem;
    }
    /* ── Stat card premium accents ── */
    .stat-card { border-top: 1px solid rgba(255, 255, 255, 0.08); }
    .stat-card:nth-child(1) .stat-icon { text-shadow: 0 0 18px rgba(236, 72, 153, 0.8); }
    .stat-card:nth-child(2) .stat-icon { text-shadow: 0 0 18px rgba(217, 70, 239, 0.8); }
    .stat-card:nth-child(3) .stat-icon { text-shadow: 0 0 18px rgba(59, 130, 246, 0.8); }
    .stat-card:nth-child(4) .stat-icon { text-shadow: 0 0 18px rgba(34, 211, 238, 0.8); }
    .stat-card:nth-child(1)::before { background: radial-gradient(120% 120% at 50% 0%, rgba(236, 72, 153, 0.22) 0%, transparent 55%); }
    .stat-card:nth-child(2)::before { background: radial-gradient(120% 120% at 50% 0%, rgba(217, 70, 239, 0.20) 0%, transparent 55%); }
    .stat-card:nth-child(3)::before { background: radial-gradient(120% 120% at 50% 0%, rgba(59, 130, 246, 0.18) 0%, transparent 55%); }
    .stat-card:nth-child(4)::before { background: radial-gradient(120% 120% at 50% 0%, rgba(34, 211, 238, 0.18) 0%, transparent 55%); }
    .stat-card:nth-child(1) { border-color: rgba(236, 72, 153, 0.35); }
    .stat-card:nth-child(2) { border-color: rgba(217, 70, 239, 0.30); }
    .stat-card:nth-child(3) { border-color: rgba(59, 130, 246, 0.30); }
    .stat-card:nth-child(4) { border-color: rgba(34, 211, 238, 0.30); }
    .stat-card:nth-child(1):hover { box-shadow: 0 12px 34px rgba(236, 72, 153, 0.25); }
    .stat-card:nth-child(2):hover { box-shadow: 0 12px 34px rgba(217, 70, 239, 0.22); }
    .stat-card:nth-child(3):hover { box-shadow: 0 12px 34px rgba(59, 130, 246, 0.20); }
    .stat-card:nth-child(4):hover { box-shadow: 0 12px 34px rgba(34, 211, 238, 0.20); }
    /* ── Subject avatar chip (sidebar) ── */
    .subject-avatar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 12px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.16), rgba(217, 70, 239, 0.10));
        border: 1px solid rgba(34, 211, 238, 0.35);
        margin: 4px 0 10px 0;
        animation: fadeInDown 0.4s ease-out;
    }
    .subject-avatar .avatar-letter {
        width: 30px;
        height: 30px;
        flex-shrink: 0;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 0.95rem;
        color: #ffffff;
        background: var(--sl-primary-grad);
        box-shadow: 0 3px 10px rgba(168, 85, 247, 0.4);
    }
    .subject-avatar .avatar-text {
        line-height: 1.25;
        min-width: 0;
    }
    .subject-avatar .avatar-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #f1f5f9;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .subject-avatar .avatar-status {
        font-size: 0.68rem;
        color: #22d3ee;
        font-weight: 600;
    }
    /* ── Chat polish ── */
    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #ec4899, #a855f7) !important;
        box-shadow: 0 2px 10px rgba(236, 72, 153, 0.4);
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #a855f7, #22d3ee) !important;
        box-shadow: 0 2px 10px rgba(168, 85, 247, 0.35);
    }
    [data-testid="stChatMessage"] {
        background: rgba(15, 15, 29, 0.75);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.6rem;
    }
    [data-testid="stChatInput"] textarea {
        background: rgba(15, 15, 29, 0.85) !important;
        border: 1px solid rgba(34, 211, 238, 0.3) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(168, 85, 247, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.18) !important;
    }
    [data-testid="stChatInput"] button {
        background: var(--sl-primary-grad) !important;
    }
    /* ── Uploader ── */
    [data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(145deg, rgba(20, 18, 38, 0.85), rgba(12, 11, 24, 0.9)) !important;
        border: 1.5px dashed rgba(34, 211, 238, 0.4) !important;
        border-radius: 14px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(168, 85, 247, 0.7) !important;
        box-shadow: 0 8px 26px rgba(236, 72, 153, 0.22) !important;
    }
    /* ── Captions & dividers ── */
    [data-testid="stCaptionContainer"] p { color: #8896ab; }
    .streamlit-expanderHeader {
        border: 1px solid rgba(34, 211, 238, 0.18) !important;
    }
    /* ── Native widgets (text input, select, radio, checkbox, slider, progress) ── */
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input {
        background: rgba(12, 11, 24, 0.85) !important;
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(168, 85, 247, 0.7) !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.16) !important;
    }
    [data-testid="stSelectbox"] > div > div, [data-testid="stPopover"] button {
        background: rgba(12, 11, 24, 0.85) !important;
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stCheckbox"] label span {
        color: #e2e8f0 !important;
    }
    [data-testid="stCheckbox"] svg { color: #a855f7 !important; }
    [data-testid="stSlider"] [data-testid="stThumbValue"], [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: #a855f7 !important;
        border-color: #a855f7 !important;
    }
    [data-testid="stSliderTickBar"] div { color: #64748b !important; }
    [data-baseweb="progress"] [role="progressbar"] {
        background: var(--sl-primary-grad) !important;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.45) !important;
    }
    [data-testid="stProgress"] > div > div > div > div {
        background: var(--sl-primary-grad) !important;
    }
    [data-testid="stRadio"] label { color: #e2e8f0 !important; }
    [data-testid="stRadio"] input:checked + div svg { color: #a855f7 !important; }
    [data-testid="stPopover"] button:hover {
        border-color: rgba(168, 85, 247, 0.6) !important;
    }
    .stApp > div:first-child { position: relative; z-index: 1; }
    [data-testid="stSidebar"] { z-index: 2; }
    /* ── Onboarding / First-run ── */
    .onboard-card {
        background: linear-gradient(150deg, rgba(236, 72, 153, 0.14), rgba(168, 85, 247, 0.10) 45%, rgba(34, 211, 238, 0.10));
        border: 1px solid rgba(168, 85, 247, 0.30);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.6rem;
        animation: fadeInUp 0.5s ease-out;
    }
    .onboard-badge {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
        color: #f0abfc;
        background: rgba(236, 72, 153, 0.16);
        border: 1px solid rgba(236, 72, 153, 0.35);
        padding: 4px 12px; border-radius: 9999px; margin-bottom: 0.9rem;
    }
    .onboard-steps { display: flex; gap: 0; margin: 1rem 0 0.4rem 0; }
    .onboard-step {
        flex: 1; position: relative; padding: 0 0.9rem; text-align: left;
    }
    .onboard-step:not(:last-child)::after {
        content: ''; position: absolute; top: 15px; left: calc(100% - 6px); width: 12px; height: 2px;
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.6), rgba(34, 211, 238, 0.6));
    }
    .onboard-step-num {
        width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 0.85rem; color: #ffffff;
        background: var(--sl-primary-grad); box-shadow: 0 3px 12px rgba(168, 85, 247, 0.45);
        margin-bottom: 0.5rem;
    }
    .onboard-step-title { font-size: 0.78rem; font-weight: 700; color: #f1f5f9; margin-bottom: 2px; }
    .onboard-step-desc { font-size: 0.72rem; color: #94a3b8; line-height: 1.5; }
    .onboard-demo-flow {
        display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;
        margin: 1rem 0 0.2rem 0; font-size: 0.82rem;
    }
    .onboard-milestone {
        display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 10px;
        background: rgba(12, 11, 24, 0.85); border: 1px solid rgba(34, 211, 238, 0.28);
        color: #a5f3fc; font-weight: 600;
    }
    .onboard-milestone.done { border-color: rgba(52, 211, 153, 0.4); color: #34d399; }
    .onboard-arrow { color: #d946ef; font-weight: 800; }
    /* Onboarding tour callout (inside workspace) */
    .tour-callout {
        background: linear-gradient(120deg, rgba(34, 211, 238, 0.12), rgba(168, 85, 247, 0.12));
        border: 1px solid rgba(34, 211, 238, 0.35);
        border-left: 3px solid #22d3ee;
        border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;
        animation: fadeInDown 0.4s ease-out;
    }
    .tour-callout h4 { color: #ffffff; margin: 0 0 6px 0; font-size: 1rem; display: flex; align-items: center; gap: 8px; }
    .tour-callout p { color: #a5f3fc; font-size: 0.85rem; margin: 0 0 10px 0; line-height: 1.55; }
    .tour-pills { display: flex; flex-wrap: wrap; gap: 8px; }
    .tour-pill {
        font-size: 0.75rem; padding: 5px 11px; border-radius: 9999px; font-weight: 600;
        background: rgba(236, 72, 153, 0.14); color: #f0abfc; border: 1px solid rgba(236, 72, 153, 0.35);
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
# First-run onboarding flags
if "onboard_welcome_seen" not in st.session_state:
    st.session_state.onboard_welcome_seen = False
if "onboard_tour_dismissed" not in st.session_state:
    st.session_state.onboard_tour_dismissed = False

# --- SIDEBAR: APP NAVIGATION (Linear / Notion Style) ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">◈</div>
        <div>
            <div class="sidebar-brand-title">StudyLens</div>
            <div class="sidebar-brand-sub">AI Study Workspace</div>
            <div style="height: 2px; width: 100%; margin-top: 6px; border-radius: 2px; background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.7), rgba(236, 72, 153, 0.7), transparent);"></div>
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

        _active_sub = st.session_state.subjects.get(st.session_state.current_subject, {})
        _has_notes = bool(_active_sub.get("master_notes_md"))
        st.markdown(f"""
        <div class="subject-avatar">
            <div class="avatar-letter">{st.session_state.current_subject[:1].upper()}</div>
            <div class="avatar-text">
                <div class="avatar-name">{st.session_state.current_subject}</div>
                <div class="avatar-status">{"✅ Notes ready" if _has_notes else "⏳ Pending setup"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
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

    # ── Onboarding progress tracker (sidebar footer) ──
    if st.session_state.current_subject and subject_names:
        _sub_now = st.session_state.subjects.get(st.session_state.current_subject, {})
        _mk = lambda done, txt: f'<span class="onboard-milestone {"done" if done else ""}">{"✅" if done else "○"} {txt}</span>'
        st.markdown("""
        <style>
            .pipeline-mini { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px; }
            .pipeline-mini .onboard-milestone { padding: 3px 7px; font-size: 0.62rem; gap: 3px; border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)
        _m1 = bool(_sub_now.get("raw_slides"))
        _m2 = bool(_sub_now.get("master_notes_md"))
        _m3 = bool(_sub_now.get("quiz_score", {}).get("total", 0))
        st.markdown(
            '<div class="nav-section-label">Your Progress</div>'
            + '<div class="pipeline-mini">'
            + _mk(True, "Created")
            + _mk(_m1, "Uploaded")
            + _mk(_m2, "Noted")
            + _mk(_m3, "Quizzed")
            + "</div>",
            unsafe_allow_html=True
        )
        if not _m1:
            st.caption("Hint: open 📄 Materials to add your first slides.")
        elif not _m2:
            st.caption("Hint: upload slides to generate your notes.")
        elif not _m3:
            st.caption("Hint: try a 🎯 Quiz to test yourself.")

    api_key_input = GEMINI_API_KEY


# ==============================================================================
# VIEW: CLEAN EMPTY / LANDING STATE (When no subject is active)
# ==============================================================================
if not st.session_state.subjects or not st.session_state.current_subject:
    # ── First-run welcome card ──
    if not st.session_state.onboard_welcome_seen:
        c_w, c_d = st.columns([5, 1])
        with c_w:
            st.markdown("""
            <div class="onboard-card">
                <div class="onboard-badge">👋 Welcome to StudyLens</div>
                <h3 style="color: #ffffff; margin: 0 0 0.3rem 0; font-size: 1.35rem; letter-spacing: -0.01em;">
                    Your study workspace is ready — here's how it works.
                </h3>
                <p style="color: #a5f3fc; font-size: 0.92rem; line-height: 1.6; margin: 0 0 0.4rem 0; max-width: 620px;">
                    StudyLens turns messy lecture slide photos, screenshots, and PDFs into organized, searchable
                    revision notes and quizzes — automatically. You're 4 quick steps from studying smarter.
                </p>
                <div class="onboard-steps">
                    <div class="onboard-step">
                        <div class="onboard-step-num">1</div>
                        <div class="onboard-step-title">Create a Subject</div>
                        <div class="onboard-step-desc">Name a course or exam below — this becomes your study workspace.</div>
                    </div>
                    <div class="onboard-step">
                        <div class="onboard-step-num">2</div>
                        <div class="onboard-step-title">Upload Slides</div>
                        <div class="onboard-step-desc">Drop in lecture photos, screenshots or PDFs on the Materials page.</div>
                    </div>
                    <div class="onboard-step">
                        <div class="onboard-step-num">3</div>
                        <div class="onboard-step-title">Get Notes & Quizzes</div>
                        <div class="onboard-step-desc">AI cleans, dedupes and summarizes into topic-grouped notes.</div>
                    </div>
                    <div class="onboard-step">
                        <div class="onboard-step-num">4</div>
                        <div class="onboard-step-title">Quiz & Chat</div>
                        <div class="onboard-step-desc">Test yourself and ask questions grounded in your own notes.</div>
                    </div>
                </div>
                <div class="onboard-demo-flow">
                    <span class="onboard-milestone">📤 Upload</span><span class="onboard-arrow">→</span>
                    <span class="onboard-milestone">🧹 Clean</span><span class="onboard-arrow">→</span>
                    <span class="onboard-milestone">🧠 Summarize</span><span class="onboard-arrow">→</span>
                    <span class="onboard-milestone">🎯 Quiz</span><span class="onboard-arrow">→</span>
                    <span class="onboard-milestone">💬 Chat</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_d:
            st.write("")
            if st.button("✕", key="btn_dismiss_welcome", help="Dismiss this welcome card"):
                st.session_state.onboard_welcome_seen = True
                st.rerun()

    st.markdown("""
    <div style="text-align: center; max-width: 720px; margin: 2.5rem auto 1rem auto;">
        <div style="display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg, rgba(236, 72, 153, 0.18), rgba(236, 72, 153, 0.18)); color: #a5f3fc; border: 1px solid rgba(34, 211, 238, 0.35); padding: 5px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1.4rem; box-shadow: 0 2px 12px rgba(236, 72, 153, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08);">
            ⚡ Powered by Gemini AI & OpenCV
        </div>
        <h1 style="font-size: 2.8rem; font-weight: 800; color: #ffffff; line-height: 1.18; margin-bottom: 1rem; text-shadow: 0 2px 24px rgba(37, 99, 235, 0.25);">
            Turn messy lecture slides into <span class="gradient-headline">structured revision notes.</span>
        </h1>
        <p style="font-size: 1.05rem; color: #e879f9; line-height: 1.6; margin-bottom: 2rem;">
            StudyLens cleans whiteboard photos, removes duplicate slides, and synthesizes crisp, topic-grouped revision notes and quizzes.
        </p>
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 1rem;">
            <span class="feature-chip">🧠 AI Summarization</span>
            <span class="feature-chip">🖼️ OCR Forensics</span>
            <span class="feature-chip">🎯 Auto Quizzes</span>
            <span class="feature-chip">💬 Chat with Notes</span>
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-card-icon">🧠</div>
                <div class="feature-card-title">AI Summarization</div>
                <div class="feature-card-desc">Topic-grouped, exam-ready notes synthesized from every slide.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">🖼️</div>
                <div class="feature-card-title">Smart Image Cleanup</div>
                <div class="feature-card-desc">OpenCV enhances dark whiteboard photos & auto-drops duplicates.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">🎯</div>
                <div class="feature-card-title">Auto Quizzes</div>
                <div class="feature-card-desc">Instant self-test questions grounded strictly in your material.</div>
            </div>
            <div class="feature-card">
                <div class="feature-card-icon">💬</div>
                <div class="feature-card-title">Chat with Notes</div>
                <div class="feature-card-desc">Ask anything — answers come only from your own revision notes.</div>
            </div>
        </div>
        <div class="pipeline-strip">
            <span>1 · Upload Slides</span><i>→</i><span>2 · Clean & Dedupe</span><i>→</i><span>3 · Summarize</span><i>→</i><span>4 · Quiz & Chat</span>
        </div>
        <hr class="gradient-divider">
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

    # ── Interactive "How it works" guide ──
    with st.expander("📚 Not sure where to start? — Open the guided walkthrough", expanded=False):
        st.markdown(
            "<p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.6rem;'>"
            "Your notes pipeline happens automatically. Here's what each step does and where it lives in the app.</p>",
            unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("""
            <div class="feature-card" style="margin-bottom: 8px;">
                <div class="feature-card-icon">📥</div>
                <div class="feature-card-title">1 · Create a Subject</div>
                <div class="feature-card-desc">Type a name in the box above (or tap <b>Try Sample Demo</b> to explore instantly). This creates your dedicated workspace.</div>
            </div>
            <div class="feature-card" style="margin-bottom: 8px;">
                <div class="feature-card-icon">📤</div>
                <div class="feature-card-title">2 · Upload Slides</div>
                <div class="feature-card-desc">From the <b>📄 Materials</b> page, upload lecture photo slides, screenshots, or PDFs. Drag-and-drop up to 20 files.</div>
            </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown("""
            <div class="feature-card" style="margin-bottom: 8px;">
                <div class="feature-card-icon">🧠</div>
                <div class="feature-card-title">3 · Get AI Notes</div>
                <div class="feature-card-desc">StudyLens cleans the images, removes duplicates, and summarizes everything into topic-grouped notes on the <b>📝 Revision Notes</b> page.</div>
            </div>
            <div class="feature-card" style="margin-bottom: 8px;">
                <div class="feature-card-icon">🎯</div>
                <div class="feature-card-title">4 · Quiz & Chat</div>
                <div class="feature-card-desc">Test yourself on <b>🎯 Quizzes</b> and ask questions on <b>💬 Chat with Notes</b> — answers come only from your own material.</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(
            "<p style='color: #22d3ee; font-size: 0.82rem; margin-top: 0.6rem;'>"
            "💡 Tip: Tap <b>✨ Try Sample Demo</b> above — it loads a pre-made lecture with notes & quiz so you can explore every feature without uploading anything.</p>",
            unsafe_allow_html=True)

    st.markdown("""
    <hr class="gradient-divider" style="margin-top: 2.5rem;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 10px; padding: 0.4rem 0 1.2rem 0; font-size: 0.8rem; color: #64748b;">
        <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px rgba(52, 211, 153, 0.9); animation: nodePulse 2s ease-in-out infinite;"></span>
        StudyLens AI Study Workspace · Powered by Gemini AI · OpenCV · EasyOCR
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# Current Subject State
sub = st.session_state.subjects[st.session_state.current_subject]


# ==============================================================================
# WORKSPACE VIEWS (Active Subject Workspace)
# ==============================================================================

top_nav_col1, top_nav_col2 = st.columns([1.5, 3.5])
with top_nav_col1:
    if st.button("← Home", key="btn_top_back_home", use_container_width=True, help="Return to subjects overview & landing page"):
        st.session_state.current_subject = None
        st.session_state.current_view = "Overview"
        st.rerun()
with top_nav_col2:
    if st.button("📤 Upload New Material", key="btn_top_upload", use_container_width=True, type="primary", help="Jump to the Materials uploader"):
        st.session_state.current_view = "Materials"
        st.rerun()

hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 0.4rem; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 10px;">
    <div>
        <div class="greeting-title">{greeting} 👋</div>
        <div class="greeting-subtitle">Ready to continue learning in <span class="subject-chip">{st.session_state.current_subject}</span>?</div>
    </div>
</div>
<hr class="gradient-divider">
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

    # ── First-run workspace tour callout ──
    if not st.session_state.onboard_tour_dismissed:
        tc1, tc2 = st.columns([5, 1])
        with tc1:
            st.markdown("""
            <div class="tour-callout">
                <h4>🎓 Welcome to your workspace!</h4>
                <p>The sidebar on the left is your command center. Green means ready, so start with <b>📄 Materials</b>
                to upload your lecture slides, then watch StudyLens clean, dedupe, and summarize them for you.</p>
                <div class="tour-pills">
                    <span class="tour-pill">📄 Materials — add slides</span>
                    <span class="tour-pill">📝 Revision Notes — your AI notes</span>
                    <span class="tour-pill">🎯 Quizzes — self-test</span>
                    <span class="tour-pill">💬 Chat — ask notes questions</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with tc2:
            st.write("")
            if st.button("✕ Got it", key="btn_dismiss_tour", help="Dismiss this tour guide"):
                st.session_state.onboard_tour_dismissed = True
                st.rerun()

    # ── Empty-workspace quick-start guide ──
    if total_materials == 0:
        es1, es2 = st.columns([3, 1])
        with es1:
            st.markdown("""
            <div class="onboard-card" style="margin-bottom: 1rem;">
                <div class="onboard-badge">🚀 Let's get you started</div>
                <h3 style="color: #ffffff; margin: 0 0 0.4rem 0; font-size: 1.15rem;">Your workspace is empty — here's the fastest way to fill it:</h3>
                <div class="onboard-steps">
                    <div class="onboard-step">
                        <div class="onboard-step-num">1</div>
                        <div class="onboard-step-title">Upload slides</div>
                        <div class="onboard-step-desc">Photos, screenshots, or PDFs on the Materials page.</div>
                    </div>
                    <div class="onboard-step">
                        <div class="onboard-step-num">2</div>
                        <div class="onboard-step-title">Watch the pipeline</div>
                        <div class="onboard-step-desc">Clean → dedupe → summarize runs automatically.</div>
                    </div>
                    <div class="onboard-step">
                        <div class="onboard-step-num">3</div>
                        <div class="onboard-step-title">Study smarter</div>
                        <div class="onboard-step-desc">Quiz, chat and review your notes from here.</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with es2:
            st.write("")
            if st.button("📤 Upload Slides", type="primary", key="btn_empty_upload", use_container_width=True, help="Jump to the Materials uploader"):
                st.session_state.current_view = "Materials"
                st.rerun()

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
    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
    with qa_col1:
        if st.button("📄 Upload", use_container_width=True, help="Upload lecture slides & PDFs"):
            st.session_state.current_view = "Materials"
            st.rerun()
    with qa_col2:
        if st.button("📝 Notes", use_container_width=True, help="View your revision notes"):
            st.session_state.current_view = "Revision Notes"
            st.rerun()
    with qa_col3:
        if st.button("🎯 Quiz", use_container_width=True, help="Test your knowledge"):
            st.session_state.current_view = "Quizzes"
            st.rerun()
    with qa_col4:
        if st.button("💬 Chat", use_container_width=True, type="primary", help="Ask AI about your notes"):
            st.session_state.current_view = "Chat"
            st.rerun()
                                
# ------------------------------------------------------------------------------
# 2. MATERIALS VIEW (Upload & Processing)
# ------------------------------------------------------------------------------
elif st.session_state.current_view == "Materials":
    st.markdown('<span class="view-title">📄 Course Materials &amp; Lecture Slides</span>', unsafe_allow_html=True)
    st.markdown('<div class="view-subtitle">Upload lecture slides (PNG, JPG, WEBP) or multi-page PDFs. OpenCV will enhance clarity and filter duplicates.</div>', unsafe_allow_html=True)

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
    st.markdown('<span class="view-title">📝 Structured Revision Notes</span>', unsafe_allow_html=True)
    st.markdown('<div class="view-subtitle">AI-synthesized, factually grounded notes extracted from your lecture materials.</div>', unsafe_allow_html=True)

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
    st.markdown('<span class="view-title">📜 Notes History — <span style="color:#ffffff;-webkit-text-fill-color:#ffffff;">{}</span></span>'.format(st.session_state.current_subject), unsafe_allow_html=True)
    st.markdown('<div class="view-subtitle">Browse past versions of your generated revision notes.</div>', unsafe_allow_html=True)

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
    st.markdown('<span class="view-title">💬 Chat with Your Revision Notes</span>', unsafe_allow_html=True)
    st.markdown('<div class="view-subtitle">Ask a question and the AI answers using only the content from your generated notes for this subject.</div>', unsafe_allow_html=True)

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
    st.markdown('<span class="view-title">🎯 AI Knowledge Check &amp; Quizzes</span>', unsafe_allow_html=True)
    st.markdown('<div class="view-subtitle">3-question targeted multiple choice assessment based on your generated notes.</div>', unsafe_allow_html=True)

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


# ==============================================================================
# FOOTER (Workspace views)
# ==============================================================================
st.markdown("""
<hr class="gradient-divider" style="margin-top: 2.5rem;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; padding: 0.4rem 0 1.2rem 0;">
    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #94a3b8;">
        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px rgba(52, 211, 153, 0.9); animation: nodePulse 2s ease-in-out infinite;"></span>
        <span>StudyLens <span class="gradient-headline">AI Study Workspace</span></span>
    </div>
    <div style="font-size: 0.78rem; color: #64748b;">
        Powered by Gemini AI · OpenCV · EasyOCR
    </div>
</div>
""", unsafe_allow_html=True)
