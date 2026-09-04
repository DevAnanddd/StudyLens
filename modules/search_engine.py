import re
from typing import List, Dict, Any

class RevisionSearchEngine:
    def __init__(self, topic_summaries: List[Dict[str, Any]], raw_slides: List[Dict[str, Any]]):
        self.topic_summaries = topic_summaries
        self.raw_slides = raw_slides
        self.index = self._build_search_index()
        
    def _build_search_index(self) -> List[Dict[str, Any]]:
        chunks = []
        for topic_item in self.topic_summaries:
            topic = topic_item.get("topic", "General")
            for sub in topic_item.get("subheadings", []):
                title = sub.get("title", "")
                content = sub.get("content", "")
                sources = sub.get("sources", [])
                chunks.append({
                    "topic": topic,
                    "subheading": title,
                    "type": "content",
                    "text": f"{title}\n{content}",
                    "sources": sources,
                    "breadcrumb": f"{topic} › {title}"
                })
            for d in topic_item.get("definitions", []):
                term = d.get("term", "")
                defn = d.get("definition", "")
                src = d.get("source", "")
                chunks.append({
                    "topic": topic,
                    "subheading": f"Definition: {term}",
                    "type": "definition",
                    "text": f"{term}: {defn}",
                    "sources": [src] if src else [],
                    "breadcrumb": f"{topic} › Key Definitions › {term}"
                })
        for s in self.raw_slides:
            chunks.append({
                "topic": s.get("topic", "Slide Content"),
                "subheading": f"{s['source_file']} (Slide {s['slide_index']})",
                "type": "slide_ocr",
                "text": s.get("text", ""),
                "sources": [f"{s['source_file']} (Slide {s['slide_index']})"],
                "breadcrumb": f"{s.get('topic', 'Slide Content')} › Slide {s['slide_index']}"
            })
        return chunks

    def search(self, query: str, max_results: int = 15) -> List[Dict[str, Any]]:
        query = query.strip()
        if not query:
            return []
        terms = [re.escape(t.lower()) for t in query.split() if t.strip()]
        if not terms:
            return []
        pattern = re.compile("|".join(terms), re.IGNORECASE)
        results = []
        for item in self.index:
            text = item["text"]
            text_lower = text.lower()
            matches = list(pattern.finditer(text))
            if matches:
                score = len(matches)
                if re.search(pattern, item.get("subheading", "")):
                    score += 5
                if re.search(pattern, item.get("topic", "")):
                    score += 3
                # Bonus for exact multi-word matches (phrase in query)
                full_query = " ".join(t.strip().replace("\\", "") for t in terms if t.strip())
                if full_query.lower() in text_lower:
                    score += 10
                first_match = matches[0]
                start = max(0, first_match.start() - 60)
                end = min(len(text), first_match.end() + 100)
                snippet = text[start:end].replace("\n", " ")
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                results.append({
                    "topic": item["topic"],
                    "subheading": item["subheading"],
                    "breadcrumb": item["breadcrumb"],
                    "type": item["type"],
                    "snippet": snippet,
                    "sources": item["sources"],
                    "score": score
                })
            else:
                # Fuzzy fallback: check if any term appears as a partial substring match
                fuzzy_score = 0
                for term in terms:
                    clean_term = term.replace("\\", "")
                    # Check common stem variations (e.g. "optim" matches "optimization", "optimize")
                    if len(clean_term) >= 4 and clean_term in text_lower:
                        fuzzy_score += 2
                if fuzzy_score > 0:
                    snippet = text[:200].replace("\n", " ")
                    if len(text) > 200:
                        snippet += "..."
                    results.append({
                        "topic": item["topic"],
                        "subheading": item["subheading"],
                        "breadcrumb": item["breadcrumb"],
                        "type": item["type"],
                        "snippet": snippet,
                        "sources": item["sources"],
                        "score": fuzzy_score
                    })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
