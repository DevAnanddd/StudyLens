# Contributing to StudyLens

Welcome to the team! This guide will get you from zero to productive in under 10 minutes.

## Quick Setup

```bash
# 1. Clone the repo
git clone https://github.com/DevAnanddd/StudyLens.git
cd StudyLens

# 2. Create a virtual environment and install Python dependencies
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# 3. Install frontend dependencies (if working on the React workbench)
npm install

# 4. Copy the example env file and add your API key
cp .env.example .env
# Edit .env and paste your Gemini API key (get one at https://aistudio.google.com/apikey)

# 5. Run the app
streamlit run app.py
```

## Project Layout

```
Student-Lens/
├── app.py                  # Main Streamlit app (UI, views, orchestration)
├── modules/                # Core logic
│   ├── ai_summarizer.py    # Gemini API calls: topic detection, summarization
│   ├── duplicate_detector.py  # Perceptual-hash duplicate slide detection
│   ├── file_processor.py   # PDF→images, image loading
│   ├── image_preprocessor.py  # OpenCV CLAHE, denoise, deskew
│   ├── note_generator.py   # Markdown/PDF note assembly
│   ├── ocr_engine.py       # EasyOCR / Tesseract text extraction
│   └── search_engine.py    # Local keyword search over notes
├── utils/
│   ├── config.py           # Paths, constants, env loading
│   ├── data_store.py       # JSON persistence for subjects/notes
│   └── helpers.py          # Image conversion utilities
├── src/                    # React workbench frontend
│   ├── components/         # React components (Header, etc.)
│   ├── App.tsx             # React app entry
│   └── types.ts            # TypeScript interfaces
├── server.ts               # Express dev server
└── requirements.txt        # Python dependencies
```

## Development Workflow

### Branching
- `main` — stable, deployable at all times
- Create feature branches from `main`:
  ```bash
  git checkout -b feature/your-feature-name
  ```

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add fuzzy matching to local search engine
fix: handle missing API key gracefully in quiz view
docs: update README with architecture diagram
```

### Pull Requests
1. Push your branch and open a PR against `main`
2. Describe **what** you changed and **why**
3. Include screenshots for UI changes
4. Wait for review before merging

## Key Architecture Notes

### Backend (Python/Streamlit)
- **`app.py`** is the single entry point. Streamlit re-runs the entire script on every interaction, so state is stored in `st.session_state`.
- Each view (Overview, Materials, Revision Notes, Chat, Quizzes) is a section in `app.py` controlled by `st.session_state.current_view`.
- **`utils/data_store.py`** handles persisting subjects to disk as JSON so data survives restarts.
- The Gemini API is called via raw `urllib` (no SDK dependency) in `modules/ai_summarizer.py`.

### Frontend (React/TypeScript)
- Vite dev server proxies API calls to the Streamlit backend.
- The React "workbench" is a secondary interface for pipeline configuration and prompt inspection.

### API Key
- The app uses Google Gemini for AI features (summarization, chat, quizzes).
- You need your own API key from [Google AI Studio](https://aistudio.google.com/apikey).
- Store it in `.env` (never committed) or in Streamlit Cloud secrets.

## Code Style

### Python
- Follow PEP 8
- Use type hints where practical
- Keep functions focused (< 50 lines when possible)

### TypeScript/React
- Functional components only
- Use TypeScript interfaces for all props/state (see `src/types.ts`)

## Testing Changes

1. **Quick check**: `streamlit run app.py` — does the app load? Can you create a subject?
2. **Demo mode**: Click "✨ Try Sample Demo" — do all views work?
3. **Upload flow**: Upload a few slide images or a PDF — does OCR + summarization complete?
4. **Search**: After generating notes, search for a term — do results appear?
5. **Chat/Quiz**: Do they respond with content grounded in the notes?

## Questions?

Open a GitHub issue or message directly. Happy coding! 🚀
