"""
StudyLens - Main Streamlit Application.
Turn messy lecture slide photos, screenshots, and PDF notes into organized, searchable revision notes.
"""
import streamlit as st
import os
import io
import time
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# On Streamlit Cloud, the API key lives in st.secrets instead of a local .env file.
# This bridges it into an environment variable so the rest of the app (and utils.config)
# works the same way whether running locally or deployed.
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

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
from modules.ai_summarizer import detect_topics_batch, group_slides_by_topic, summarize_topic_group
from modules.note_generator import generate_master_notes
from modules.search_engine import RevisionSearchEngine

# Page configuration
st.set_page_config(
    page_title="StudyLens | Smart Lecture Revision Notes",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=Kalam:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .main-title {
        font-family: 'Fraunces', serif;
        font-size: 2.7rem;
        font-weight: 700;
        color: #F3EFE4;
        margin-bottom: 0.1rem;
        letter-spacing: -0.01em;
    }
    .main-title .hl {
        background: linear-gradient(104deg, rgba(245,194,66,0) 0.5%, rgba(245,194,66,0.55) 3%, rgba(245,194,66,0.55) 92%, rgba(245,194,66,0) 96%);
        padding: 0 6px;
    }
    .sub-title {
        font-family: 'Kalam', cursive;
        font-size: 1.15rem;
        color: #B7C9BE;
        margin-bottom: 1.8rem;
    }
    .metric-card {
        background: #1E332B;
        border: 1px solid #3E5347;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .breadcrumb-tag {
        font-family: 'Kalam', cursive;
        background-color: rgba(245, 194, 66, 0.15);
        color: #F5C242;
        border: 1px dashed rgba(245, 194, 66, 0.5);
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .search-card {
        background: #1E332B;
        border: 1px solid #3E5347;
        border-left: 4px solid #F5C242;
        border-radius: 4px 10px 10px 4px;
        padding: 14px 18px;
        margin-bottom: 12px;
        position: relative;
        box-shadow: 2px 3px 10px rgba(0,0,0,0.25);
    }
    .search-card::after {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 0 16px 16px 0;
        border-color: transparent #0E1A15 transparent transparent;
    }
</style>
""", unsafe_allow_html=True)


def new_subject_state():
    """Returns a fresh, empty pipeline state for one subject."""
    return {
        "raw_slides": [],
        "duplicate_clusters": [],
        "unique_slides": [],
        "pipeline_stage": "upload",  # upload, review_duplicates, completed
        "ocr_done": False,
        "topic_summaries": [],
        "master_notes_md": "",
        "search_engine": None,
        "excluded_slide_ids": set(),
        "chat_history": [],
    }


# Initialize Session State (now keyed by subject)
if "subjects" not in st.session_state:
    st.session_state.subjects = {}
if "current_subject" not in st.session_state:
    st.session_state.current_subject = None

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/book-open.svg", width=48)
    st.title("StudyLens Settings")
    st.markdown("---")

    # --- Subject Management ---
    st.subheader("📚 Subject")
    subject_names = list(st.session_state.subjects.keys())

    if subject_names:
        if st.session_state.current_subject not in subject_names:
            st.session_state.current_subject = subject_names[0]
        selected_subject = st.selectbox(
            "Active Subject",
            options=subject_names,
            index=subject_names.index(st.session_state.current_subject),
            help="Each subject keeps its own separate slides, notes, and chat."
        )
        st.session_state.current_subject = selected_subject
    else:
        st.caption("No subjects yet — create one below to get started.")

    new_subject_name = st.text_input(
        "New subject name",
        placeholder="e.g. Data Structures, Physics...",
        key="new_subject_input"
    )
    if st.button("➕ Create Subject", use_container_width=True):
        name = new_subject_name.strip()
        if not name:
            st.warning("Enter a subject name first.")
        elif name in st.session_state.subjects:
            st.warning("That subject already exists.")
        else:
            st.session_state.subjects[name] = new_subject_state()
            st.session_state.current_subject = name
            st.rerun()

    st.markdown("---")

    api_key_input = GEMINI_API_KEY

    st.subheader("Pipeline Settings")
    hash_threshold = st.slider(
        "Duplicate Sensitivity (Hamming Distance)",
        min_value=0,
        max_value=15,
        value=DEFAULT_HASH_THRESHOLD,
        help="Lower distance = only exact duplicates. Higher distance = flags similar/slightly altered slides."
    )

    ocr_choice = st.selectbox(
        "Preferred OCR Engine",
        options=["EasyOCR", "Tesseract"],
        index=0
    )

    apply_enhancements = st.checkbox(
        "OpenCV Image Enhancements (CLAHE & Denoise)",
        value=True,
        help="Improves OCR accuracy for noisy photos & low-contrast slides."
    )

    st.markdown("---")
    if subject_names:
        if st.button("🔄 Reset Current Subject", use_container_width=True):
            st.session_state.subjects[st.session_state.current_subject] = new_subject_state()
            st.rerun()

# --- HEADER ---
if not st.session_state.subjects:
    st.markdown('<div class="main-title">🔍 <span class="hl">StudyLens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Turn messy lecture slide photos, screenshots, and PDF notes into organized, searchable revision notes.</div>', unsafe_allow_html=True)
    st.info("👈 Create your first subject in the sidebar to get started (e.g. \"DSA\", \"Physics\", \"History\").")
    st.stop()

sub = st.session_state.subjects[st.session_state.current_subject]

st.markdown(f'<div class="main-title">🔍 <span class="hl">StudyLens</span> — {st.session_state.current_subject}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Turn messy lecture slide photos, screenshots, and PDF notes into organized, searchable revision notes.</div>', unsafe_allow_html=True)

# --- STAGE 1: UPLOAD & EXTRACTION ---
if sub["pipeline_stage"] == "upload":
    st.subheader("📤 Step 1: Upload Lecture Slides or PDFs")
    uploaded_files = st.file_uploader(
        "Choose image files (PNG, JPG, WEBP) or PDFs",
        type=ALL_SUPPORTED_TYPES,
        accept_multiple_files=True,
        help="Upload individual photos, screenshots, or multi-page lecture PDFs."
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected.")
        if st.button("🚀 Process & Detect Duplicates", type="primary", use_container_width=True):
            with st.status("Processing uploads & analyzing slides...", expanded=True) as status:
                # 1. File extraction
                status.write("📄 Extracting pages and reading images...")
                slides = process_uploaded_files(uploaded_files)
                if not slides:
                    st.error("No valid slide images could be extracted from the uploaded files.")
                    st.stop()

                status.write(f"✅ Extracted {len(slides)} total slide/page images.")

                # 2. Image Preprocessing (OpenCV)
                status.write("🎨 Preprocessing images with OpenCV (Grayscale, CLAHE, Denoising)...")
                for s in slides:
                    proc_img, _ = preprocess_slide_image(
                        s["image"],
                        apply_clahe=apply_enhancements,
                        apply_denoise=apply_enhancements
                    )
                    s["preprocessed_image"] = proc_img

                # 3. Duplicate Detection
                status.write("🔁 Calculating perceptual hashes (pHash) and detecting duplicates...")
                unique_slides, duplicate_clusters = cluster_duplicates(slides, threshold=hash_threshold)

                sub["raw_slides"] = slides
                sub["duplicate_clusters"] = duplicate_clusters
                sub["unique_slides"] = unique_slides
                sub["pipeline_stage"] = "review_duplicates"
                status.update(label="Initial processing complete! Ready for duplicate review.", state="complete")

            time.sleep(0.5)
            st.rerun()

# --- STAGE 2: DUPLICATE REVIEW SCREEN ---
elif sub["pipeline_stage"] == "review_duplicates":
    st.subheader("🔁 Step 2: Review Duplicate & Near-Duplicate Slides")
    st.caption("We found potential duplicates. Review below and choose which slides to include before running OCR.")

    total_extracted = len(sub["raw_slides"])
    clusters = sub["duplicate_clusters"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Slides Uploaded", total_extracted)
    col2.metric("Duplicate Clusters Found", len(clusters))
    col3.metric("Estimated Unique Slides", len(sub["unique_slides"]))

    st.markdown("---")

    if not clusters:
        st.success("🎉 No duplicate slides detected! All slides appear unique.")
    else:
        st.markdown("### 🔍 Duplicate Clusters Found (Never auto-deleted)")
        for c_idx, cluster in enumerate(clusters, 1):
            with st.expander(f"📌 Cluster #{c_idx} ({len(cluster)} similar slides)", expanded=True):
                cols = st.columns(min(len(cluster), 4))
                for idx, item in enumerate(cluster):
                    col = cols[idx % 4]
                    with col:
                        st.image(item["image"], caption=f"{item['source_file']} (Slide {item['slide_index']})", use_container_width=True)
                        is_primary = item.get("is_primary", False)
                        dist = item.get("hamming_dist", 0)

                        badge_label = "⭐ Primary Slide" if is_primary else f"🔄 Near-Duplicate (Dist: {dist})"
                        st.caption(badge_label)

                        is_excluded = item["id"] in sub["excluded_slide_ids"]
                        include = st.checkbox(
                            "Include in OCR",
                            value=(not is_excluded and is_primary),
                            key=f"chk_{st.session_state.current_subject}_{item['id']}"
                        )
                        if not include:
                            sub["excluded_slide_ids"].add(item["id"])
                        else:
                            sub["excluded_slide_ids"].discard(item["id"])

        st.markdown("---")
    c_back, c_run = st.columns([1, 3])
    with c_back:
        if st.button("⬅️ Back to Upload"):
            sub["pipeline_stage"] = "upload"
            st.rerun()
    with c_run:
        if st.button("✨ Run OCR & Generate Revision Notes", type="primary", use_container_width=True):
            # Filter final slides to OCR
            final_unique = [
                s for s in sub["raw_slides"]
                if s["id"] not in sub["excluded_slide_ids"]
            ]

            if not final_unique:
                st.warning("All slides were excluded! Please select at least one slide to proceed.")
                st.stop()

            sub["unique_slides"] = final_unique

            # Run OCR
            with st.status("Extracting text and generating revision notes...", expanded=True) as status:
                status.write(f"🔤 Running {ocr_choice} on {len(final_unique)} unique slides...")
                progress_bar = st.progress(0.0)

                for idx, s in enumerate(final_unique):
                    extract_text_from_slide(s, preferred_engine=ocr_choice)
                    progress_bar.progress((idx + 1) / len(final_unique))

                sub["ocr_done"] = True

                # Gemini Topic Grouping & Summaries
                status.write("🤖 Detecting topics and clustering concepts with Gemini AI...")
                final_unique = detect_topics_batch(final_unique, api_key=api_key_input)
                grouped_topics = group_slides_by_topic(final_unique)

                status.write(f"📝 Summarizing {len(grouped_topics)} distinct topic sections...")
                summaries = []
                for topic, topic_slides in grouped_topics.items():
                    summary_obj = summarize_topic_group(topic, topic_slides, api_key=api_key_input)
                    summaries.append(summary_obj)

                sub["topic_summaries"] = summaries

                # Master Note Generation
                total_words = sum(s.get("word_count", 0) for s in final_unique)
                stats = {
                    "unique_slides": len(final_unique),
                    "total_words": total_words,
                    "topics_count": len(summaries)
                }
                master_md = generate_master_notes(summaries, stats)
                sub["master_notes_md"] = master_md

                # Build Search Index
                sub["search_engine"] = RevisionSearchEngine(summaries, final_unique)
                sub["pipeline_stage"] = "completed"
                status.update(label="Revision notes successfully generated!", state="complete")

            time.sleep(0.5)
            st.rerun()

# --- STAGE 3: RESULTS, DASHBOARD, SEARCH, NOTES & CHAT ---
elif sub["pipeline_stage"] == "completed":
    # 1. Stats Dashboard
    total_raw = len(sub["raw_slides"])
    total_unique = len(sub["unique_slides"])
    total_dups_removed = total_raw - total_unique
    total_words = sum(s.get("word_count", 0) for s in sub["unique_slides"])
    total_topics = len(sub["topic_summaries"])

    st.markdown("### 📊 Processing Statistics")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Uploaded", total_raw)
    m2.metric("Duplicates Removed", total_dups_removed)
    m3.metric("Unique Slides", total_unique)
    m4.metric("Extracted Words", total_words)
    m5.metric("Topics Created", total_topics)

    st.markdown("---")

    # 2. Main Navigation Tabs
    tab_search, tab_notes, tab_slides, tab_chat = st.tabs([
        "🔎 Smart Search & Breadcrumbs",
        "📖 Revision Notes",
        "🖼️ Unique Slides & OCR Text",
        "💬 Chat with Notes"
    ])

    with tab_search:
        st.subheader("🔎 Search Across Topics, Headings & Definitions")
        search_query = st.text_input("Enter search keywords, concept, or term:", placeholder="e.g. Backpropagation, Neural Network, Theorem 2...")

        if search_query:
            if sub["search_engine"]:
                results = sub["search_engine"].search(search_query)
                if results:
                    st.success(f"Found {len(results)} matching sections/concepts:")
                    for r in results:
                        st.markdown(f"""
                        <div class="search-card">
                        <span class="breadcrumb-tag">{r['breadcrumb']}</span>
                        <h4 style="margin: 6px 0;">{r['subheading']}</h4>
                        <p style="color: #374151; font-size: 0.95rem;">{r['snippet']}</p>
                        <small style="color: #6B7280;">Sources: {', '.join(r['sources']) if r['sources'] else 'N/A'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No matching topics or concepts found for this query.")
            else:
                st.caption("Type any term above to view exact breadcrumb navigation links across your notes.")

    with tab_notes:
        st.subheader("📑 Structured Revision Notes")

        # Download & Copy Row
        col_d1, col_d2, _ = st.columns([1, 1, 2])
        with col_d1:
            st.download_button(
                label="📥 Download Markdown (.md)",
                data=sub["master_notes_md"],
                file_name=f"StudyLens_{st.session_state.current_subject}_Revision_Notes.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="📥 Download Plain Text (.txt)",
                data=sub["master_notes_md"],
                file_name=f"StudyLens_{st.session_state.current_subject}_Revision_Notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("---")

        # Collapsible Topic Accordions
        for idx, item in enumerate(sub["topic_summaries"], 1):
            topic_title = item.get("topic", f"Topic {idx}")
            with st.expander(f"📚 Topic {idx}: {topic_title}", expanded=(idx == 1)):
                if "summary_markdown" in item and item["summary_markdown"]:
                    st.markdown(item["summary_markdown"])
                elif "subheadings" in item:
                    for sh in item["subheadings"]:
                        st.markdown(f"### {sh.get('title', 'Section')}")
                        st.write(sh.get("content", ""))
                        if sh.get("key_points"):
                            for kp in sh["key_points"]:
                                st.markdown(f"- {kp}")

                # Definitions
                definitions = item.get("definitions", [])
                if definitions:
                    st.markdown("#### 💡 Key Definitions")
                    for d in definitions:
                        st.info(f"**{d.get('term', '')}**: {d.get('definition', '')}")

    with tab_slides:
        st.subheader("🖼️ Extracted Unique Slides & Raw OCR Output")
        for idx, slide in enumerate(sub["unique_slides"], 1):
            with st.expander(f"Slide {idx}: {slide['source_file']} (Slide #{slide['slide_index']}) - Confidence: {slide.get('confidence', 0):.1%}"):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.image(slide["image"], use_container_width=True, caption="Original Slide")
                with c2:
                    st.markdown(f"**OCR Engine:** {slide.get('engine', 'N/A')} | **Word Count:** {slide.get('word_count', 0)}")
                    st.text_area(
                        "Extracted OCR Text",
                        value=slide.get("text", ""),
                        height=220,
                        key=f"ocr_text_{st.session_state.current_subject}_{slide['id']}"
                    )

    with tab_chat:
        st.subheader(f"💬 Chat with Your {st.session_state.current_subject} Notes")
        st.caption("Ask a question and the AI will answer using only the content from your generated revision notes.")

        if not sub["master_notes_md"]:
            st.info("Generate your revision notes first — this tab needs notes to chat about.")
        else:
            for msg in sub["chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_question = st.chat_input("Ask something about your notes...")
            if user_question:
                sub["chat_history"].append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            genai.configure(api_key=api_key_input)
                            chat_model = genai.GenerativeModel("gemini-3.6-flash")
                            prompt = (
                                "You are a helpful study assistant. Answer the student's question "
                                "using ONLY the information contained in the revision notes below. "
                                "If the answer isn't covered in these notes, say so honestly instead "
                                "of guessing.\n\n"
                                f"REVISION NOTES:\n{sub['master_notes_md']}\n\n"
                                f"STUDENT QUESTION: {user_question}"
                            )
                            response = chat_model.generate_content(prompt)
                            answer = response.text
                        except Exception as e:
                            answer = f"Sorry, I couldn't get an answer right now. ({e})"
                        st.markdown(answer)

                sub["chat_history"].append({"role": "assistant", "content": answer})

    st.markdown("---")
    if st.button("⬅️ Start New Session", type="secondary"):
        sub["pipeline_stage"] = "upload"
        st.rerun()
