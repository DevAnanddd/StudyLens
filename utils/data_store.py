"""
Persistent storage for StudyLens subjects.
Saves/loads subject state to disk so work survives app restarts.

Per-visitor isolation
---------------------
Every visitor is given a stable visitor id (created in app.py and kept in a
browser cookie / URL token). All persisted files are scoped under:

    data/users/<visitor-id>/subjects.json
    data/users/<visitor-id>/notes_history/<subject>/notes_<timestamp>.json

so different visitors never read, see, or overwrite each other's data, while a
single visitor keeps their data across page refreshes and new app sessions.

When no ``user_key`` is passed the module falls back to the legacy shared
location (``data/subjects.json``) for backwards compatibility and tests.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from utils.config import BASE_DIR

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
_USERS_DIR = DATA_DIR / "users"

# Legacy / default storage file - only used when no user_key is supplied.
# This is what every visitor shared before per-user isolation was added.
SUBJECTS_FILE = DATA_DIR / "subjects.json"

# Fields that contain non-JSON-serializable objects and must be stripped before
# saving. PIL images live under "image"/"preprocessed_image" on every slide
# dict, and "search_engine" holds a live RevisionSearchEngine instance.
_SKIP_FIELDS = {"image", "preprocessed_image", "search_engine"}

# Visitor keys are UUID hex strings (or short test values) - keep them safe
# to use as a directory name.
_VALID_KEY_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _store_dir(user_key: Optional[str]) -> Path:
    """Return the directory scoped to one visitor, or the legacy shared dir."""
    if user_key and _VALID_KEY_RE.match(user_key):
        return _USERS_DIR / user_key
    return DATA_DIR


def _sanitize_for_json(obj: Any) -> Any:
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


def save_subjects(subjects: Dict[str, Any], user_key: Optional[str] = None) -> bool:
    """
    Persist the full subjects dict to this visitor's own store.
    Non-serializable fields (PIL images, search engine) are stripped first.
    Returns True on success, False on failure.
    """
    try:
        data = _sanitize_for_json(subjects)
        store_dir = _store_dir(user_key)
        store_dir.mkdir(parents=True, exist_ok=True)
        target = store_dir / "subjects.json"
        # Write to a temp file first, then rename (crash-safe)
        tmp_path = store_dir / "subjects.json.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(target)
        return True
    except Exception as e:
        print(f"[StudyLens] Warning: Could not save subjects to disk: {e}")
        return False


def load_subjects(user_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Load this visitor's subjects dict from disk.
    Returns empty dict if no file exists or on error.
    Rebuilds non-serializable fields (search_engine, excluded_slide_ids as sets).
    """
    target = _store_dir(user_key) / "subjects.json"
    if not target.exists():
        return {}
    try:
        with open(target, "r", encoding="utf-8") as f:
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


def delete_subject_data(subject_name: str, user_key: Optional[str] = None) -> bool:
    """Delete a specific subject's saved data for this visitor. Returns True on success."""
    subjects = load_subjects(user_key=user_key)
    if subject_name in subjects:
        del subjects[subject_name]
        return save_subjects(subjects, user_key=user_key)
    return True


def get_notes_history_path(subject_name: str, user_key: Optional[str] = None) -> Path:
    """Return the path to this visitor's notes history directory for a subject."""
    safe_name = subject_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    history_dir = _store_dir(user_key) / "notes_history" / safe_name
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir


def save_notes_snapshot(
    subject_name: str, master_notes_md: str, topic_summaries: list, user_key: Optional[str] = None
) -> bool:
    """
    Save a timestamped snapshot of generated notes (scoped to this visitor).
    """
    try:
        history_dir = get_notes_history_path(subject_name, user_key=user_key)
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


def load_notes_history(
    subject_name: str, max_items: int = 10, user_key: Optional[str] = None
) -> list:
    """
    Load recent notes history snapshots for this visitor's subject.
    Returns list of dicts sorted newest-first.
    """
    history_dir = get_notes_history_path(subject_name, user_key=user_key)
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
