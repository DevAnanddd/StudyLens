from typing import List, Dict, Any
from datetime import datetime

def generate_master_notes(
    topic_summaries: List[Dict[str, Any]],
    stats: Dict[str, Any]
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    md_lines = [
        f"# 📚 StudyLens Revision Notes",
        f"**Generated:** {timestamp}  |  **Unique Slides:** {stats.get('unique_slides', 0)}  |  **Total Words:** {stats.get('total_words', 0)}",
        "",
        "---",
        "## 📑 Table of Contents"
    ]
    for idx, item in enumerate(topic_summaries, 1):
        topic_title = item.get("topic", f"Topic {idx}")
        anchor = topic_title.lower().replace(" ", "-").replace("/", "").replace(":", "")
        md_lines.append(f"{idx}. [{topic_title}](#{anchor})")
        if "subheadings" in item and isinstance(item["subheadings"], list):
            for sub in item["subheadings"]:
                sub_title = sub.get("title", "")
                if sub_title:
                    sub_anchor = sub_title.lower().replace(" ", "-").replace("/", "").replace(":", "")
                    md_lines.append(f"   - [{sub_title}](#{sub_anchor})")
    md_lines.append("")
    md_lines.append("---")
    for idx, item in enumerate(topic_summaries, 1):
        topic_title = item.get("topic", f"Topic {idx}")
        md_lines.append(f"\n## {idx}. {topic_title}\n")
        if "summary_markdown" in item and item["summary_markdown"]:
            md_lines.append(item["summary_markdown"])
        elif "subheadings" in item:
            for sub in item.get("subheadings", []):
                md_lines.append(f"### {sub.get('title', 'Section')}")
                md_lines.append(sub.get("content", ""))
                if sub.get("key_points"):
                    for kp in sub["key_points"]:
                        md_lines.append(f"- {kp}")
                md_lines.append("")
        definitions = item.get("definitions", [])
        if definitions:
            md_lines.append("\n> 💡 **Key Definitions & Terminology**")
            for d in definitions:
                term = d.get("term", "")
                defn = d.get("definition", "")
                src = f" *({d['source']})*" if d.get("source") else ""
                md_lines.append(f"> - **{term}**: {defn}{src}")
            md_lines.append("")
        md_lines.append("\n---\n")
    md_lines.append("Generated with **StudyLens** - Clean, Structured & Searchable Revision Notes.")
    return "\n".join(md_lines)
