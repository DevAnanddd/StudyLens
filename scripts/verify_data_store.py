"""
Verification harness for utils/data_store.py.

Run with:  python scripts/verify_data_store.py

Checks:
  1. Per-user isolation: visitor A and visitor B get separate files and can
     never see each other's subjects or notes history.
  2. PIL image stripping: save_subjects survives slides that carry raw
     PIL.Image objects (image / preprocessed_image) and a live search engine;
     those fields are stripped from disk AND from the loaded dict, while text,
     notes, quiz and chat data round-trip intact.
  3. Notes history snapshots are scoped per visitor.
  4. Legacy shared fallback (user_key=None) still behaves like the old code
     (data/subjects.json).
  5. Malformed user keys are rejected and fall back to the shared dir.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from utils import data_store  # noqa: E402

ALICE = "A_verify_alice_9f2a"
BOB = "B_verify_bob_9f2a"
FAILED = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}")
    if not cond:
        FAILED.append(name)

def make_processed_subject(name):
    """Mirror app.py's subject state AFTER slides have been processed."""
    slides = []
    for i in range(3):
        img = Image.new("RGB", (320, 180), (i * 40 + 10, 20, 10))
        slides.append({
            "id": f"slide_{i}",
            "source_file": "Lecture_07_Deep_Learning.pdf",
            "slide_index": i + 1,
            "image": img,               # raw PIL Image - NOT JSON-serializable
            "preprocessed_image": img,  # raw PIL Image - NOT JSON-serializable
            "text": f"Slide {i + 1}: linear algebra content.",
            "confidence": 0.95,
            "engine": "EasyOCR",
            "word_count": 120 + i,
        })
    return {
        "raw_slides": slides,
        "duplicate_clusters": ["cluster_abc"],
        "unique_slides": slides,
        "pipeline_stage": "completed",
        "ocr_done": True,
        "topic_summaries": [
            {
                "topic": "Matrices",
                "summary_markdown": "### Matrices overview\nVector spaces and linear maps.",
                "subheadings": [{"title": "Definitions", "content": "A matrix is...", "key_points": ["x", "y"]}],
                "definitions": [{"term": "Rank", "definition": "Dimension of the column space.", "source": "Slide 1"}],
            },
            {"topic": "Vectors", "summary_markdown": "### Vectors\nBasis and span.", "subheadings": [], "definitions": []},
        ],
        "master_notes_md": "# Linear Algebra Master Notes\n\nContent goes here.",
        "search_engine": object(),  # live engine - NOT JSON-serializable
        "excluded_slide_ids": {"slide_0", "slide_2"},
        "quiz_score": {"correct": 2, "total": 3},
        "study_streak_days": 4,
        "chat_history": [{"role": "user", "content": "Explain rank?"}],
        "last_updated": "Sep 9, 2026 at 10:00 AM",
    }

def main():
    # Clean any leftovers from a previous run
    for key in (ALICE, BOB):
        shutil.rmtree(data_store._store_dir(key), ignore_errors=True)

    # ---- 1. Per-user isolation ---------------------------------------------
    print("1) Per-user isolation")
    alice_subjects = {"Linear Algebra": make_processed_subject("Linear Algebra")}
    bob_subjects = {"Physics": {"raw_slides": [], "unique_slides": [], "master_notes_md": "Newton's laws",
                                "excluded_slide_ids": set(), "search_engine": None,
                                "chat_history": [], "quiz_score": {"correct": 0, "total": 0}}}

    check("Alice save succeeds even with PIL images present", data_store.save_subjects(alice_subjects, user_key=ALICE))
    check("Alice file is at data/users/<alice>/subjects.json",
          (data_store._store_dir(ALICE) / "subjects.json").exists())
    check("Bob sees NO data before he has his own (empty dict)",
          data_store.load_subjects(user_key=BOB) == {})

    data_store.save_subjects(bob_subjects, user_key=BOB)
    bob_loaded = data_store.load_subjects(user_key=BOB)
    alice_loaded = data_store.load_subjects(user_key=ALICE)
    check("Bob only sees his own subjects", list(bob_loaded.keys()) == ["Physics"])
    check("Alice only sees her own subjects", list(alice_loaded.keys()) == ["Linear Algebra"])
    check("Alice cannot read Bob's Physics subject", "Physics" not in alice_loaded)

    # ---- 2. PIL image serialization safety ---------------------------------
    print("2) PIL image serialization safety")
    al = alice_loaded["Linear Algebra"]
    check("image key stripped from loaded slides",
          all("image" not in s and "preprocessed_image" not in s for s in al["unique_slides"]))
    check("other slide text/quiz data survived",
          al["unique_slides"][0]["text"].startswith("Slide 1:")
          and al["quiz_score"] == {"correct": 2, "total": 3}
          and al["chat_history"][0]["content"] == "Explain rank?")
    check("search_engine rebuilt to None on load", al["search_engine"] is None)
    check("excluded_slide_ids restored as a set", isinstance(al["excluded_slide_ids"], set)
          and al["excluded_slide_ids"] == {"slide_0", "slide_2"})
    raw = json.loads((data_store._store_dir(ALICE) / "subjects.json").read_text(encoding="utf-8"))
    check("on-disk JSON contains NO image payloads",
          "image" not in raw["Linear Algebra"]["unique_slides"][0]
          and "preprocessed_image" not in raw["Linear Algebra"]["raw_slides"][0]
          and "search_engine" not in raw["Linear Algebra"])
    check("master_notes_md persisted intact",
          raw["Linear Algebra"]["master_notes_md"] == "# Linear Algebra Master Notes\n\nContent goes here.")

    # ---- 3. Notes history scoping ------------------------------------------
    print("3) Notes history snapshots scoped per visitor")
    summaries = [{"topic": "Matrices"}, {"topic": "Vectors"}]
    check("Alice snapshot saved", data_store.save_notes_snapshot(
        "Linear Algebra", "# Notes v1", summaries, user_key=ALICE))
    hist_alice = data_store.load_notes_history("Linear Algebra", max_items=10, user_key=ALICE)
    check("Alice history has 1 snapshot", len(hist_alice) == 1 and hist_alice[0]["topics_count"] == 2)
    check("Bob history for same subject is empty",
          data_store.load_notes_history("Linear Algebra", max_items=10, user_key=BOB) == [])

    # ---- 4. Legacy shared fallback -----------------------------------------
    print("4) Legacy shared fallback (user_key=None)")
    legacy = data_store.SUBJECTS_FILE
    had_legacy = legacy.exists()
    legacy_bytes = legacy.read_bytes() if had_legacy else None
    try:
        ok = data_store.save_subjects({"Legacy": {"master_notes_md": "old shared data"}}, user_key=None)
        check("legacy save writes data/subjects.json", ok and legacy.exists())
        check("legacy load reads it back", "Legacy" in data_store.load_subjects(user_key=None))
    finally:
        if had_legacy:
            legacy.write_bytes(legacy_bytes)
        else:
            legacy.unlink(missing_ok=True)

    # ---- 5. Invalid user keys ----------------------------------------------
    print("5) Malformed user-key safety")
    check("../../ trick key rejected -> legacy dir", data_store._store_dir("../../evil") == data_store.DATA_DIR)
    check("empty key rejected -> legacy dir", data_store._store_dir("") == data_store.DATA_DIR)
    check("None -> legacy dir", data_store._store_dir(None) == data_store.DATA_DIR)

    # ---- Cleanup -----------------------------------------------------------
    for key in (ALICE, BOB):
        shutil.rmtree(data_store._store_dir(key), ignore_errors=True)
    users_dir = data_store.DATA_DIR / "users"
    if users_dir.exists() and not any(users_dir.iterdir()):
        users_dir.rmdir()

    if FAILED:
        print(f"\n{len(FAILED)} CHECK(S) FAILED: {FAILED}")
        raise SystemExit(1)
    print("\nAll data_store checks passed.")


if __name__ == "__main__":
    main()
