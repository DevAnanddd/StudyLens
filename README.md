# StudyLens 🔍📚
Turn messy lecture slide photos, screenshots, and PDF notes into clean, organized, searchable revision notes.

## Features
- 📤 **Multi-format Upload**: Supports PNG, JPG, JPEG, WEBP, and PDF documents.
- 📄 **High-Res PDF Extraction**: Renders slide pages using PyMuPDF.
- 🎨 **Image Preprocessing**: Auto-enhances contrast, grayscaling, denoising, and sharpening using OpenCV for maximum OCR accuracy.
- 🔁 **Perceptual Duplicate Detection**: Groups duplicate and near-duplicate slides using imagehash.phash with a human-in-the-loop review interface.
- 🔤 **Accurate OCR**: EasyOCR with Tesseract fallback and metadata tracking (source, slide index, confidence).
- 🤖 **Batched Gemini AI Synthesizer**: Groups slides logically and generates structured revision notes with zero hallucinated facts.
- 🔎 **Breadcrumb Search Engine**: Jump directly to concepts with Topic > Subheading > Snippet [Source].
- 💾 **Export**: Preview and download notes in Markdown (.md) or text (.txt).

## Installation
`ash
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
`

## Run
`ash
streamlit run app.py
`
