import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from utils.config import TOPIC_DETECTION_BATCH_SIZE, SUMMARIZATION_BATCH_SIZE

# The model name that used to live in utils.config (DEFAULT_GEMINI_MODEL) has been
# retired by Google. Hardcoding a currently-supported model here instead.
CURRENT_GEMINI_MODEL = "gemini-3.6-flash"


def call_gemini_rest(prompt: str, api_key: str, model: str = CURRENT_GEMINI_MODEL, json_response: bool = True) -> Optional[str]:
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    if json_response:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
    except Exception as e:
        print(f"Gemini API Request Error: {e}")
        return None


def detect_topics_batch(
    slides: List[Dict[str, Any]],
    model_name: str = CURRENT_GEMINI_MODEL,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    key = api_key or os.getenv("GEMINI_API_KEY", "")

    if not key:
        for slide in slides:
            first_line = slide.get("text", "").split("\n")[0] if slide.get("text") else "General Slide"
            slide["topic"] = first_line[:40].strip() or "General Lecture Content"
            slide["concepts"] = []
        return slides

    for i in range(0, len(slides), TOPIC_DETECTION_BATCH_SIZE):
        batch = slides[i : i + TOPIC_DETECTION_BATCH_SIZE]
        batch_prompt_items = [
            {"slide_id": s["id"], "source": f"{s['source_file']} (Slide {s['slide_index']})", "content": s.get("text", "")[:1000]}
            for s in batch
        ]
        prompt = f"""You are an academic organizer. Group slide items into meaningful academic topics.

Rules for the 'topic' field:
- Use a clear, descriptive subject name (e.g. "Shallow Copy vs Deep Copy", "Character Arrays vs Strings") that reflects the actual concept being taught.
- NEVER use a table header, column label, row number, or short fragment (e.g. "S.No.", "SNo", "Sr No", "Table 1") as a topic name, even if it appears first in the slide text.
- If a slide is a data table, name the topic after what the table is actually comparing or explaining, not its column headers.

Return ONLY JSON array with 'slide_id', 'topic', 'concepts'. Data: {json.dumps(batch_prompt_items)}"""
        resp_text = call_gemini_rest(prompt, key, model=model_name, json_response=True)
        if resp_text:
            try:
                parsed = json.loads(resp_text.strip())
                topic_map = {item["slide_id"]: item for item in parsed if "slide_id" in item}
                for s in batch:
                    if s["id"] in topic_map:
                        s["topic"] = topic_map[s["id"]].get("topic", "General Topic")
                        s["concepts"] = topic_map[s["id"]].get("concepts", [])
                    else:
                        first_line = s.get("text", "").split("\n")[0] if s.get("text") else "General Slide"
                        s["topic"] = first_line[:40].strip() or "General Topic"
                        s["concepts"] = []
            except Exception as e:
                print(f"Topic JSON parsing error: {e}")
        else:
            for s in batch:
                first_line = s.get("text", "").split("\n")[0] if s.get("text") else "General Slide"
                s["topic"] = first_line[:40].strip() or "General Topic"
                s["concepts"] = []
        time.sleep(0.5)
    return slides


def group_slides_by_topic(slides: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for slide in slides:
        topic = slide.get("topic", "General Overview").strip()
        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(slide)
    return grouped


def summarize_topic_group(
    topic: str,
    slides_in_topic: List[Dict[str, Any]],
    model_name: str = CURRENT_GEMINI_MODEL,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        combined = "\n\n".join([f"**{s['source_file']} [Slide {s['slide_index']}]:** {s.get('text', '')}" for s in slides_in_topic])
        return {
            "topic": topic,
            "subheadings": [{"title": "Extracted Content", "content": combined, "key_points": [], "sources": [f"{s['source_file']} (Slide {s['slide_index']})" for s in slides_in_topic]}],
            "definitions": [],
            "summary_markdown": f"### {topic}\n\n{combined}"
        }

    slides_payload = [{"source": f"{s['source_file']} (Slide {s['slide_index']})", "content": s.get("text", "")} for s in slides_in_topic]
    prompt = f"""Synthesize slides under topic "{topic}". Return JSON with topic, subheadings (title, content, key_points, sources), definitions (term, definition, source), summary_markdown. Strict factual grounding.

Formatting rule for summary_markdown: if the source content compares two or more things side by side (e.g. "X vs Y", feature comparisons, pros/cons across options), render that comparison as an actual markdown table using pipe syntax, e.g.:

| Feature | Option A | Option B |
|---|---|---|
| Example | Value | Value |

Do NOT flatten a comparison into a run-on paragraph of dashes and semicolons. Only use a table when the content is genuinely comparative; otherwise use normal prose and bullet points.

Data: {json.dumps(slides_payload)}"""
    resp_text = call_gemini_rest(prompt, key, model=model_name, json_response=True)
    if resp_text:
        try:
            return json.loads(resp_text.strip())
        except Exception as e:
            print(f"Summary parse error: {e}")

    combined = "\n\n".join([f"- **{s['source_file']} [Slide {s['slide_index']}]:** {s.get('text', '')}" for s in slides_in_topic])
    return {
        "topic": topic,
        "subheadings": [{"title": "Extracted Content", "content": combined, "key_points": [], "sources": []}],
        "definitions": [],
        "summary_markdown": f"### {topic}\n\n{combined}",
        "ai_summary_failed": True
    }
