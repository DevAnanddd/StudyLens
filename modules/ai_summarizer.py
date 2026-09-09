import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from utils.config import TOPIC_DETECTION_BATCH_SIZE, SUMMARIZATION_BATCH_SIZE

# The model name that used to live in utils.config (DEFAULT_GEMINI_MODEL) has been
# retired by Google. Models here are ordered by preference; when the first model
# is busy/overloaded (HTTP 503 / 429), the code automatically falls back to the next.
# NOTE: gemini-1.5-flash / gemini-2.0-flash / gemini-2.5-flash have been retired (404).
CURRENT_GEMINI_MODEL = "gemini-3.7-flash"
GEMINI_MODEL_CHAIN = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
]
API_TIMEOUT_SECONDS = 120
API_RETRY_ATTEMPTS = 3
API_RETRY_BACKOFF_BASE = 2.0  # wait 2s, 4s, 8s between transient-error retries


class GeminiAPIError(Exception):
    """Raised when the Gemini REST API returns an error response."""
    def __init__(self, status_code: int, message: str, error_type: str = "unknown"):
        self.status_code = status_code
        self.message = message
        self.error_type = error_type
        super().__init__(message)


def classify_gemini_error(status_code: int, error_body: str) -> tuple[str, str]:
    """Return (user_friendly_type, user_friendly_message) for a Gemini API error."""
    try:
        parsed = json.loads(error_body)
        detail = parsed.get("error", {}).get("message", error_body)
    except Exception:
        detail = error_body

    if status_code == 429 or "RESOURCE_EXHAUSTED" in error_body or "rate" in error_body.lower():
        return ("rate_limited", f"API rate limit / quota exceeded. {detail}")
    elif status_code == 403 or "PERMISSION_DENIED" in error_body:
        return ("permission_denied", f"API key is invalid or revoked. {detail}")
    elif status_code == 404 or "NOT_FOUND" in error_body or "models/" in detail:
        return ("model_not_found", f"Model '{CURRENT_GEMINI_MODEL}' not found or no longer available. {detail}")
    elif status_code == 400 or "INVALID_ARGUMENT" in error_body:
        return ("invalid_request", f"Bad request sent to API. {detail}")
    elif status_code == 401:
        return ("auth_error", f"Authentication failed — check your API key. {detail}")
    elif status_code == 503 or status_code == 500 or "UNAVAILABLE" in error_body or "high demand" in detail:
        return ("server_busy", f"The Gemini API is temporarily overloaded. {detail}")
    else:
        return ("server_error", f"Unexpected API error ({status_code}). {detail}")


def _http_post_json(url: str, payload: dict, timeout: int, api_key: str) -> str:
    """Perform a single HTTP POST to the Gemini API and return the response text."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"]


def call_gemini_rest(prompt: str, api_key: str, model: str = CURRENT_GEMINI_MODEL, json_response: bool = True) -> Optional[str]:
    """Call the Gemini API with automatic model fallback and retries.

    - Tries each model in GEMINI_MODEL_CHAIN until one responds.
    - Retries transient errors (429 / 503 / timeout) with exponential backoff.
    - Raises GeminiAPIError only if every model fails on every attempt.
    """
    if not api_key:
        return None

    # Prefer the explicitly requested model first, then the rest of the chain.
    model_chain = [model] if model and model in GEMINI_MODEL_CHAIN else []
    model_chain += [m for m in GEMINI_MODEL_CHAIN if m != model]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    if json_response:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    last_error: Optional[GeminiAPIError] = None
    for attempt in range(1, API_RETRY_ATTEMPTS + 1):
        for m in model_chain:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            try:
                return _http_post_json(url, payload, API_TIMEOUT_SECONDS, api_key)
            except urllib.error.HTTPError as e:
                error_body = ""
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    error_body = str(e)
                error_type, error_msg = classify_gemini_error(e.code, error_body)
                last_error = GeminiAPIError(e.code, error_msg, error_type)
                print(f"[attempt {attempt}] Gemini API Error [{error_type}] (HTTP {e.code}) on model '{m}': {error_msg}")
                # Transient errors: try the next model, then retry with backoff.
                if error_type in ("rate_limited", "server_busy", "server_error", "model_not_found"):
                    continue
                # Permanent errors (bad key, auth) can't be fixed by retrying.
                raise last_error
            except urllib.error.URLError as e:
                last_error = GeminiAPIError(0, f"Network error: {e.reason}", "network_error")
                print(f"[attempt {attempt}] Gemini API Network Error on model '{m}': {e}")
                continue
            except Exception as e:
                last_error = GeminiAPIError(0, f"Unexpected request failure: {e}", "unknown")
                print(f"[attempt {attempt}] Gemini API Request Error on model '{m}': {e}")
                continue

        if attempt < API_RETRY_ATTEMPTS:
            wait = API_RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            print(f"Retrying in {wait:.0f}s (attempt {attempt}/{API_RETRY_ATTEMPTS})...")
            time.sleep(wait)

    if last_error:
        raise last_error
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

    # Track topic names seen so far across batches so Gemini stays consistent
    seen_topics: List[str] = []

    for i in range(0, len(slides), TOPIC_DETECTION_BATCH_SIZE):
        batch = slides[i : i + TOPIC_DETECTION_BATCH_SIZE]
        batch_prompt_items = [
            {"slide_id": s["id"], "source": f"{s['source_file']} (Slide {s['slide_index']})", "content": s.get("text", "")[:1000]}
            for s in batch
        ]
        # Build seen-topics context for consistency across batches
        seen_topics_str = ""
        if seen_topics:
            unique_seen = list(dict.fromkeys(seen_topics))  # deduplicate, preserve order
            seen_topics_str = (
                f"\n\nIMPORTANT — topics already assigned in previous batches (reuse EXACTLY when a slide matches):\n"
                f"{json.dumps(unique_seen)}"
                "\nWhen a slide belongs to one of the above topics, use the EXACT same topic name. "
                "Only invent a new topic name when no existing topic fits."
            )

        prompt = f"""You are an academic organizer. Group slide items into meaningful academic topics.

Rules for the 'topic' field:
- Use a clear, descriptive subject name (e.g. "Shallow Copy vs Deep Copy", "Character Arrays vs Strings") that reflects the actual concept being taught.
- NEVER use a table header, column label, row number, or short fragment (e.g. "S.No.", "SNo", "Sr No", "Table 1") as a topic name, even if it appears first in the slide text.
- If a slide is a data table, name the topic after what the table is actually comparing or explaining, not its column headers.
- If a slide covers the same concept as one already listed above, use the EXACT same topic name — do not invent a near-synonym.{seen_topics_str}

Return ONLY JSON array with 'slide_id', 'topic', 'concepts'. Data: {json.dumps(batch_prompt_items)}"""
        try:
            resp_text = call_gemini_rest(prompt, key, model=model_name, json_response=True)
        except GeminiAPIError:
            raise  # Let caller handle API errors (rate limit, model not found, etc.)
        except Exception as e:
            print(f"Topic detection request error: {e}")
            resp_text = None
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
        # Record this batch's topics so the next batch can stay consistent
        seen_topics.extend(s.get("topic", "") for s in batch if s.get("topic"))
        time.sleep(0.5)
    return slides


def _canonicalize_topic(raw: str) -> str:
    """Normalize a topic string into a canonical lowercase key for fuzzy matching."""
    import re
    if not raw:
        return "general"
    s = raw.lower().strip()
    # Remove common filler words that don't affect grouping
    s = re.sub(r"\b(intro|introduction|basics|overview|part\s*\d+|lecture\s*\d+|chapter\s*\d+)\b", "", s)
    # Remove punctuation except hyphens inside words
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or "general"


def _string_similarity(a: str, b: str) -> float:
    """Combined topic similarity: bigram Dice + token containment + acronym match.

    - Dice bigram handles near-identical names ("Virtual Memory & Paging" vs
      "Virtual Memory - Paging").
    - Token containment handles "Convolutional Neural Networks (CNN)" vs
      "Convolutional Neural Networks".
    - Acronym matching handles "TLB" vs "Translation Lookaside Buffer" and
      "CNNs" vs "Convolutional Neural Networks" — only for genuine
      all-caps acronym tokens, with exact initials equality (no substring
      matching, which caused false positives like "page"~"Paging Architecture").
    """
    ca, cb = _canonicalize_topic(a), _canonicalize_topic(b)
    if ca == cb:
        return 1.0
    if len(ca) < 2 or len(cb) < 2:
        return 0.0

    # 1) Dice bigram
    bg_a = {ca[i:i+2] for i in range(len(ca) - 1)}
    bg_b = {cb[i:i+2] for i in range(len(cb) - 1)}
    dice = (2.0 * len(bg_a & bg_b)) / (len(bg_a) + len(bg_b))

    # 2) Token-level containment / Jaccard on content words (order preserved)
    _STOP = {"a", "an", "the", "and", "for", "with", "of", "on", "in", "to", "vs", "v", "part"}
    ta = [w for w in ca.split() if w and w not in _STOP]
    tb = [w for w in cb.split() if w and w not in _STOP]
    token_score = 0.0
    if ta and tb:
        set_a, set_b = set(ta), set(tb)
        inter = set_a & set_b
        jac = len(inter) / len(set_a | set_b)
        # If all tokens of the smaller side appear in the larger, strong signal
        if inter:
            if inter == set_a or inter == set_b:
                token_score = min(len(set_a), len(set_b)) / max(len(set_a), len(set_b))
            else:
                token_score = jac

    # 3) Acronym match — only for genuine all-caps acronym tokens (e.g. "TLB",
    #    "CNN", "CNNs", "OS") compared against the exact initials of the other topic.
    def _acronym_tokens(raw: str) -> list:
        import re
        # Matches ALL-CAPS tokens, optionally with a trailing lowercase "s" (CNNs)
        return re.findall(r"\b[A-Z]{2,}[a-z]?\b", raw)

    def _initials_of(tokens: list) -> str:
        return "".join(w[0] for w in tokens if w)

    def _normalize_acronym(tok: str) -> str:
        t = tok.lower().rstrip("s")  # "CNNs" -> "cnn"
        return t

    acronym_score = 0.0
    toks_a, toks_b = _acronym_tokens(a), _acronym_tokens(b)
    # A) Both sides have acronyms -> compare directly
    if toks_a and toks_b:
        na, nb = _normalize_acronym(toks_a[0]), _normalize_acronym(toks_b[0])
        if na and nb and na == nb:
            acronym_score = 0.9
    # B) One side has an acronym, other is a phrase -> compare to its initials
    if not acronym_score:
        if toks_a and tb:
            if _normalize_acronym(toks_a[0]) == _initials_of(tb).lower():
                acronym_score = 0.9
        elif toks_b and ta:
            if _normalize_acronym(toks_b[0]) == _initials_of(ta).lower():
                acronym_score = 0.9

    return max(dice, token_score, acronym_score)


def group_slides_by_topic(slides: List[Dict[str, Any]], fuzzy_threshold: float = 0.58) -> Dict[str, List[Dict[str, Any]]]:
    """Group slides by detected topic with fuzzy name merging.

    Stage 1: exact-name grouping.
    Stage 2: agglomerative average-linkage merge — two topic groups are only
    merged when their *average pairwise* name similarity is >= fuzzy_threshold.
    Average-linkage (rather than single-linkage / union-find) prevents
    transitive chaining, e.g. "Virtual Memory" ~ "Virtual Memory & Paging" ~
    "Paging Architecture" — the bridge term "paging" alone can't chain three
    distinct topics into one.
    """
    # Stage 1 – exact grouping
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for slide in slides:
        topic = slide.get("topic", "General Overview").strip()
        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(slide)

    if len(grouped) <= 1:
        return grouped

    # Stage 2 – agglomerative average-linkage clustering on topic names
    names = list(grouped.keys())

    def _avg_sim(cluster_a: List[str], cluster_b: List[str]) -> float:
        if not cluster_a or not cluster_b:
            return 0.0
        total = 0.0
        for x in cluster_a:
            for y in cluster_b:
                total += _string_similarity(x, y)
        return total / (len(cluster_a) * len(cluster_b))

    clusters: List[List[str]] = [[n] for n in names]
    # Repeatedly merge the closest pair until nothing reaches the threshold
    while True:
        best_i, best_j, best_sim = -1, -1, 0.0
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                sim = _avg_sim(clusters[i], clusters[j])
                if sim > best_sim:
                    best_sim, best_i, best_j = sim, i, j
        if best_i < 0 or best_sim < fuzzy_threshold:
            break
        # Merge (keep the cluster with the longest, most descriptive name first)
        merged = clusters[best_i] + clusters[best_j]
        merged.sort(key=len, reverse=True)
        clusters.pop(best_j)
        clusters.pop(best_i)
        clusters.append(merged)

    # Stage 3 – rebuild grouped dict using the merged clusters
    result: Dict[str, List[Dict[str, Any]]] = {}
    for cluster in clusters:
        # Representative title = longest member name (most descriptive)
        display = max(cluster, key=len)
        if display not in result:
            result[display] = []
        for name in cluster:
            result[display].extend(grouped[name])

    return result


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
