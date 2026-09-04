# StudyLens 🔍📚

> Turn messy lecture slide photos, screenshots, and PDF notes into **clean, organized, searchable** revision notes — powered by AI.

StudyLens is an end-to-end study pipeline that ingests raw lecture materials (photos, screenshots, PDFs), runs image preprocessing and OCR, deduplicates slides, and uses **Google Gemini** to synthesize structured, exam-ready revision notes. It ships with two interfaces: a **Streamlit** app for quick local use, and a **React + Express** workbench for a richer, interactive pipeline experience.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **Multi-format Upload** | Supports PNG, JPG, JPEG, WEBP, and PDF documents. |
| 📄 **PDF Extraction** | Renders each PDF slide page using PyMuPDF for maximum fidelity. |
| 🎨 **Image Preprocessing** | Auto-enhances contrast, grayscaling, denoising, and sharpening using OpenCV for maximum OCR accuracy. |
| 🔁 **Duplicate Detection** | Groups duplicate and near-duplicate slides using perceptual hashing (`imagehash.phash`) with a human-in-the-loop review interface. |
| 🔤 **OCR Engine** | EasyOCR with Tesseract fallback — tracks source file, slide index, and confidence scores. |
| 🤖 **Gemini AI Synthesizer** | Groups slides logically by topic and generates structured Markdown revision notes with strict anti-hallucination rules. |
| 🔎 **Search Engine** | Jump directly to concepts with **Topic › Subheading › Snippet [Source]** breadcrumb navigation. |
| 💾 **Export** | Preview and download notes as Markdown (`.md`) or plain text (`.txt`). |
| 🌗 **Themeable UI** | Multiple dark/light themes with animated mesh backgrounds (React frontend). |
| 📐 **Architecture Docs** | Built-in pipeline architecture viewer and prompt inspector for transparency. |

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     StudyLens Pipeline                        │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  Upload   │──▶│Preprocess│──▶│   OCR    │──▶│ Dedup    │ │
│  │ (PDF/PNG) │   │ (OpenCV) │   │(EasyOCR) │   │ (pHash)  │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│                                                    │         │
│                                                    ▼         │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────────┐ │
│  │  Export   │◀──│ Search   │◀──│  Gemini AI Synthesizer   │ │
│  │(MD / TXT) │   │  Engine  │   │ (Topic Detect → Summarize)│ │
│  └──────────┘   └──────────┘   └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Processing flow:**

1. **Ingest** — User uploads slide images or PDFs.
2. **Preprocess** — Images are resized, grayscale-converted, denoised, contrast-enhanced (CLAHE), and sharpened via OpenCV.
3. **OCR** — Processed images go through EasyOCR (with Tesseract fallback) to extract raw text.
4. **Deduplicate** — Perceptual hashing (pHash + dHash) clusters near-identical slides; user reviews in a loop.
5. **Topic Detection** — Gemini AI categorizes each slide into normalized topic clusters.
6. **Summarization** — Each topic cluster is synthesized into structured revision Markdown with definitions, key points, and exam tips.
7. **Search & Export** — Notes are indexed for breadcrumb search and available for download.

---

## 🛠️ Tech Stack

### Python (Streamlit App)

| Library | Purpose |
|---|---|
| [Streamlit](https://streamlit.io/) | Web UI framework |
| [OpenCV](https://opencv.org/) | Image preprocessing (CLAHE, denoise, sharpen) |
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Primary OCR engine |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | Fallback OCR engine |
| [PyMuPDF](https://pymupdf.readthedocs.io/) | PDF page rendering |
| [imagehash](https://github.com/JohannesBuchner/imagehash) | Perceptual duplicate detection |
| [Pillow](https://python-pillow.org/) | Image I/O and manipulation |
| [google-generativeai](https://ai.google.dev/) | Gemini API client |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable management |
| [NumPy](https://numpy.org/) | Array operations |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |

### TypeScript / React (Workbench UI)

| Library | Purpose |
|---|---|
| [React 19](https://react.dev/) | UI framework |
| [Vite](https://vitejs.dev/) | Build tool & dev server |
| [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first styling |
| [Express](https://expressjs.com/) | Backend API server |
| [@google/genai](https://ai.google.dev/) | Server-side Gemini SDK |
| [Motion](https://motion.dev/) | Animations |
| [Lucide React](https://lucide.dev/) | Icon library |
| [react-markdown](https://github.com/remarkjs/react-markdown) | Markdown rendering |

---

## 📁 Project Structure

```
STUDENT LENS/
├── app.py                      # Main Streamlit application
├── server.ts                   # Express backend for React frontend
├── index.html                  # Vite HTML entry
├── package.json                # Node.js dependencies & scripts
├── requirements.txt            # Python dependencies
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── .env.example                # Environment variable template
│
├── .streamlit/
│   └── config.toml             # Streamlit dark theme
│
├── modules/                    # Python processing modules
│   ├── ai_summarizer.py        # Gemini AI topic detection & summarization
│   ├── duplicate_detector.py   # Perceptual hash duplicate clustering
│   ├── file_processor.py       # Multi-format file upload handling
│   ├── image_preprocessor.py   # OpenCV image enhancement pipeline
│   ├── note_generator.py       # Master Markdown/PDF note generation
│   ├── ocr_engine.py           # EasyOCR + Tesseract OCR extraction
│   ├── pdf_processor.py        # PDF page-to-image extraction
│   └── search_engine.py        # Breadcrumb revision search engine
│
├── utils/                      # Python utilities
│   ├── config.py               # App configuration & constants
│   └── helpers.py              # Image conversion helpers
│
├── src/                        # React frontend
│   ├── App.tsx                 # Root React component
│   ├── main.tsx                # React entry point
│   ├── types.ts                # TypeScript interfaces
│   ├── index.css               # Global styles & animations
│   ├── components/
│   │   ├── Header.tsx              # Navigation header
│   │   ├── PipelineWorkbench.tsx   # Interactive pipeline runner
│   │   ├── WorkedExampleView.tsx   # Worked example demo
│   │   ├── PromptInspector.tsx     # AI prompt viewer
│   │   ├── ArchitectureDocs.tsx    # Pipeline architecture docs
│   │   ├── MarkdownNoteRenderer.tsx # Markdown rendering component
│   │   └── ThemeSelectorModal.tsx  # Theme picker
│   ├── context/
│   │   └── ThemeContext.tsx         # Theme state management
│   ├── data/
│   │   ├── promptsAndSpecs.ts      # Prompt templates & specs
│   │   └── sampleLectureDecks.ts   # Sample lecture data
│   └── services/
│       ├── groupingEngine.ts       # Client-side topic grouping
│       └── pipelineRunner.ts       # Pipeline execution engine
│
├── output/                     # Generated revision notes
└── temp/                       # Temporary processing files
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (and npm or bun)
- A **Google Gemini API key** — get one free at [Google AI Studio](https://aistudio.google.com/apikey)
- *(Optional)* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on your PATH for fallback OCR

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/student-lens.git
cd student-lens
```

### 2. Set Up the Python Environment (Streamlit App)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up the React Frontend (Workbench)

```bash
# Install Node.js dependencies
npm install                     # or: bun install
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Then open `.env` and add your Gemini API key:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Path to Tesseract (if not on PATH)
# TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## ▶️ Running the App

### Streamlit App (Python)

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**.

### React Workbench (TypeScript)

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm start
```

Opens at **http://localhost:3000**.

---

## 📖 How It Works

### Streamlit App

1. **Upload** your lecture slides (images or PDF) through the sidebar.
2. The app **preprocesses** each image for OCR clarity.
3. **OCR** extracts raw text from every slide.
4. **Duplicate detection** clusters near-identical slides — you review and confirm.
5. **Gemini AI** categorizes slides into topics, then generates structured Markdown notes.
6. Use the **search bar** to jump to specific concepts, or **download** your notes.

### React Workbench

1. Navigate to the **Pipeline Workbench** tab.
2. Load sample lecture decks or paste OCR text.
3. Run the full pipeline: **Tag → Cluster → Summarize → Assemble**.
4. Inspect prompts in the **Prompt Inspector** tab.
5. Read the **Architecture Docs** to understand the system design.

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `TESSERACT_PATH` | Auto-detected | Full path to `tesseract.exe` |
| `DEFAULT_HASH_THRESHOLD` | `5` | Perceptual hash distance for duplicate detection |
| `DEFAULT_OCR_ENGINE` | `EasyOCR` | Primary OCR engine (`EasyOCR` or `Tesseract`) |
| `DEFAULT_GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model for the Python pipeline |
| `TOPIC_DETECTION_BATCH_SIZE` | `8` | Slides per batch for topic tagging |
| `SUMMARIZATION_BATCH_SIZE` | `5` | Slides per batch for note summarization |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository.
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m "Add amazing feature"`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request.

Please make sure to:
- Follow existing code style and conventions.
- Add docstrings for new functions and modules.
- Test your changes before submitting.

---

## 📄 License

This project is open source. See the repository for license details.

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for the AI synthesis backbone
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) and [Tesseract](https://github.com/tesseract-ocr/tesseract) for OCR
- [OpenCV](https://opencv.org/) for image processing
- [imagehash](https://github.com/JohannesBuchner/imagehash) for perceptual hashing
- [Streamlit](https://streamlit.io/) for the rapid-prototyping UI
- [Vite](https://vitejs.dev/) + [React](https://react.dev/) for the workbench frontend