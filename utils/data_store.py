"""
Persistent storage for StudyLens subjects.
Saves/loads subject state to disk so work survives app restarts.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from utils.config import BASE_DIR

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SUBJECTS_FILE = DATA_DIR / "subjects.json"

# Fields that contain non-JSON-serializable objects and must be stripped before saving
_SKIP_FIELDS = {"image", "preprocessed_image", "search_engine"}


def _sanitize_for_json(obj):
    """Recursively convert an object to JSON-serializable form, stripping non-serializable fields."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items() if k not in _SKIP_FIELDS}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item) for item in obj]
    if isinstance(obj, set):
        return sorted(list(obj))
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    # datetime objects -> ISO string
    if isinstance(obj, datetime):
        return obj.isoformat()
    # Fallback: convert to string
    return str(obj)


def save_subjects(subjects: Dict[str, Any]) -> bool:
    """
    Persist the full subjects dict to disk.
    Returns True on success, False on failure.
    """
    try:
        data = _sanitize_for_json(subjects)
        # Write to a temp file first, then rename (crash-safe)
        tmp_path = SUBJECTS_FILE.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(SUBJECTS_FILE)
        return True
    except Exception as e:
        print(f"[StudyLens] Warning: Could not save subjects to disk: {e}")
        return False


def load_subjects() -> Dict[str, Any]:
    """
    Load subjects dict from disk.
    Returns empty dict if no file exists or on error.
    Rebuilds non-serializable fields (search_engine, excluded_slide_ids as sets).
    """
    if not SUBJECTS_FILE.exists():
        return {}
    try:
        with open(SUBJECTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Rebuild per-subject runtime fields that aren't serialized
        for _name, sub in data.items():
            sub["search_engine"] = None  # Will be rebuilt on first use
            # Convert excluded_slide_ids back to a set if it was saved as a list
            if isinstance(sub.get("excluded_slide_ids"), list):
                sub["excluded_slide_ids"] = set(sub["excluded_slide_ids"])
            elif "excluded_slide_ids" not in sub:
                sub["excluded_slide_ids"] = set()
        return data
    except Exception as e:
        print(f"[StudyLens] Warning: Could not load subjects from disk: {e}")
        return {}


def delete_subject_data(subject_name: str) -> bool:
    """Delete a specific subject's saved data. Returns True on success."""
    subjects = load_subjects()
    if subject_name in subjects:
        del subjects[subject_name]
        return save_subjects(subjects)
    return True


def get_notes_history_path(subject_name: str) -> Path:
    """Return the path to a subject's notes history directory."""
    safe_name = subject_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    history_dir = DATA_DIR / "notes_history" / safe_name
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


def save_notes_snapshot(subject_name: str, master_notes_md: str, topic_summaries: list) -> bool:
    """
    Save a timestamped snapshot of generated notes for history/browsing later.
    """
    try:
        history_dir = get_notes_history_path(subject_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "display_time": datetime.now().strftime("%b %d, %Y at %I:%M %p"),
            "subject": subject_name,
            "master_notes_md": master_notes_md,
            "topics_count": len(topic_summaries),
            "topic_titles": [t.get("topic", "Untitled") for t in topic_summaries],
        }
        snapshot_file = history_dir / f"notes_{timestamp}.json"
        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[StudyLens] Warning: Could not save notes snapshot: {e}")
        return False


def load_notes_history(subject_name: str, max_items: int = 10) -> list:
    """
    Load recent notes history snapshots for a subject.
    Returns list of dicts sorted newest-first.
    """
    history_dir = get_notes_history_path(subject_name)
    if not history_dir.exists():
        return []
    snapshots = []
    for f in sorted(history_dir.glob("notes_*.json"), reverse=True):
        if len(snapshots) >= max_items:
            break
        try:
            with open(f, "r", encoding="utf-8") as fh:
                snapshots.append(json.load(fh))
        except Exception:
            continue
    return snapshots
