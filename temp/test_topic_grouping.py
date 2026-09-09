"""Verify the automatic topic grouping feature (ai_summarizer.group_slides_by_topic).

Run:  python temp/test_topic_grouping.py
"""
import sys
sys.path.insert(0, r"c:\Users\neeru\OneDrive\Desktop\STUDENT LENS")

from modules.ai_summarizer import _canonicalize_topic, _string_similarity, group_slides_by_topic

failures = []

def check(name, got, expected):
    if got == expected:
        print(f"  PASS: {name}")
    else:
        print(f"  FAIL: {name}: got {got!r}, expected {expected!r}")
        failures.append(name)

# ── 1. canonicalization ──
print("=== canonicalize ===")
check("canon_1", _canonicalize_topic("Virtual Memory & Paging"), "virtual memory paging")
check("canon_2", _canonicalize_topic("Virtual Memory"), "virtual memory")
check("canon_3", _canonicalize_topic("Page Replacement Algorithms"), "page replacement algorithms")
check("canon_4", _canonicalize_topic("Page Replacement"), "page replacement")
check("canon_5", _canonicalize_topic(""), "general")

# ── 2. similarity (merged pairs must be high, distinct pairs low) ──
print("\n=== similarity: should merge (>= threshold) ===")
should_merge = [
    ("Virtual Memory & Paging", "Virtual Memory"),
    ("Page Replacement Algorithms", "Page Replacement"),
    ("TLB", "Translation Lookaside Buffer"),
    ("Character Arrays vs Strings", "Character Arrays and Strings"),
    ("Deadlock Handling", "Deadlocks"),
]
for a, b in should_merge:
    sim = _string_similarity(a, b)
    check(f"merge {a!r} / {b!r}", sim >= 0.5, True)

print("\n=== similarity: must NOT merge (< threshold) ===")
should_not_merge = [
    ("Page Replacement", "Page Table"),
    ("Virtual Memory", "Process Synchronization"),
    ("Threads", "Processes"),
    ("Deadlocks", "Memory Allocation"),
    ("Trees", "Graph Algorithms"),
    ("Sorting", "Searching"),
    ("Linked List", "Stack Operations"),
    ("Threads and Locking", "TLB Caching"),
    ("Paging Architecture", "Page Replacement"),
    ("Virtual Memory & Paging", "Thread Synchronization"),
]
for a, b in should_not_merge:
    sim = _string_similarity(a, b)
    check(f"no-merge {a!r} / {b!r}", sim < 0.5, True)

# ── 3. end-to-end grouping of a scrambled 6-topic deck ──
print("\n=== fuzzy grouping: 12 scrambled slides over 6 topics (2 each) ===")
slides = []
topics_by_idx = {
    0: "Virtual Memory",
    1: "Paging Architecture",
    2: "Page Replacement",
    3: "TLB Caching",
    4: "Thread Synchronization",
    5: "Deadlock Handling",
    6: "Virtual Memory & Paging",
    7: "Page Replacement Algorithms",
    8: "TLB",
    9: "Threads and Locking",
    10: "Deadlocks",
    11: "Translation Lookaside Buffer",
}
for idx, t in topics_by_idx.items():
    slides.append({"id": f"s{idx}", "topic": t, "text": f"content {idx}"})

grouped = group_slides_by_topic(slides)
for topic, topic_slides in grouped.items():
    ids = [s["id"] for s in topic_slides]
    print(f"  {topic}: {ids}")

# All 12 slides must be present exactly once
all_ids = set()
for topic_slides in grouped.values():
    all_ids.update({s["id"] for s in topic_slides})
check("all_slides_accounted", all_ids, {f"s{i}" for i in range(12)})

# Slides of the same topic must be grouped together
def ids_for(needle):
    for topic_slides in grouped.values():
        ids = {s["id"] for s in topic_slides}
        if needle in ids:
            return ids
    return set()

vm = ids_for("s0")
check("vm_pair_grouped", {"s0", "s6"} <= vm, True)
pr = ids_for("s2")
check("page_replacement_grouped", {"s2", "s7"} <= pr, True)
tlb = ids_for("s3")
check("tlb_grouped", {"s3", "s8", "s11"} <= tlb, True)
dl = ids_for("s5")
check("deadlock_grouped", {"s5", "s10"} <= dl, True)

# Paging Architecture and Thread topics must stay separate (no chaining)
def all_topics():
    return [sorted(s["id"] for s in topic_slides) for topic_slides in grouped.values()]
topics = all_topics()
check("paging_arch_separate", ["s1"] in topics, True)
check("thread_sync_separate", ["s4"] in topics, True)
check("threads_locking_separate", ["s9"] in topics, True)

print()
if failures:
    print(f"RESULT: {len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("RESULT: ALL TESTS PASSED")