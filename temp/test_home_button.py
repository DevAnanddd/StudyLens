"""AppTest-based validation that the Home buttons navigate to the home screen."""
import sys
from streamlit.testing.v1 import AppTest

APP = r"C:\Users\neeru\OneDrive\Desktop\STUDENT LENS\app.py"
HOME = "__home_screen__"
FAILURES = []


def check(cond, msg):
    if cond:
        print(f"  PASS: {msg}")
    else:
        print(f"  FAIL: {msg}")
        FAILURES.append(msg)


def element_texts(at):
    """Collect visible text from rendered elements to 'see' the screen."""
    texts = []
    for e in getattr(at, "markdown", []):
        v = getattr(e, "value", "") or ""
        texts.append(v)
    for e in getattr(at, "button", []):
        texts.append(getattr(e, "label", ""))
    for e in getattr(at, "heading", []):
        texts.append(getattr(e, "value", "") or "")
    for e in getattr(at, "caption", []):
        texts.append(getattr(e, "value", "") or "")
    return " ".join(texts)


at = AppTest.from_file(APP, default_timeout=180)
at.run()

print("== Initial run (fresh session) ==")
if at.exception:
    print("  UNEXPECTED EXCEPTION ON FIRST RUN:", at.exception)
    sys.exit(1)
check(len(at.session_state["subjects"]) == 0, "fresh session starts with no subjects")

print("\n== Create a subject via the Home-screen form ==")
at.text_input(key="hero_empty_sub_input").set_value("Physics")
at.button(key="btn_hero_create").click()
at.run()
if at.exception:
    print("  UNEXPECTED EXCEPTION AFTER CREATE:", at.exception)
    sys.exit(1)
check(at.session_state["current_subject"] == "Physics", "creating subject opens its workspace")
check(at.session_state["current_view"] == "Overview", "current view is Overview")
check("Physics" in at.session_state["subjects"], "subject persisted in session state")

print("\n== Click the top-nav '← Home' button ==")
at.button(key="btn_top_back_home").click()
at.run()
if at.exception:
    print("  UNEXPECTED EXCEPTION AFTER TOP HOME:", at.exception)
    sys.exit(1)
check(at.session_state["current_subject"] == HOME, "top Home sets current_subject to HOME sentinel")
texts = element_texts(at)
if "Select an Existing Subject" in texts or "Create a New Subject" in texts:
    check(True, "home/landing screen rendered in main area")
else:
    check(False, "home/landing screen rendered in main area")

print("\n== Re-open the subject ==")
at.button(key="open_sub_Physics").click()
at.run()
if at.exception:
    print("  UNEXPECTED EXCEPTION AFTER RE-OPEN:", at.exception)
    sys.exit(1)
check(at.session_state["current_subject"] == "Physics", "re-opened Physics workspace")

print("\n== Click sidebar '🏠 Home / Change Subject' button ==")
at.button(key="sb_home_btn").click()
at.run()
if at.exception:
    print("  UNEXPECTED EXCEPTION AFTER SIDEBAR HOME:", at.exception)
    sys.exit(1)
check(at.session_state["current_subject"] == HOME, "sidebar Home sets current_subject to HOME sentinel")
texts = element_texts(at)
if "Select an Existing Subject" in texts or "Create a New Subject" in texts:
    check(True, "home/landing screen rendered in main area")
else:
    check(False, "home/landing screen rendered in main area")

print("\n== Home-screen subject picker still works ==")
at.button(key="open_sub_Physics").click()
at.run()
check(at.session_state["current_subject"] == "Physics", "can return to Physics from home")

print()
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILURE(S)")
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED")