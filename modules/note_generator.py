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


def generate_notes_pdf(master_markdown: str, subject_name: str = "Revision Notes") -> bytes:
    """Generates a clean PDF document from the markdown revision notes."""
    try:
        from fpdf import FPDF
        
        class NotesPDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 9)
                self.set_text_color(120, 120, 120)
                self.cell(w=0, h=8, text=f'StudyLens - {subject_name}', align='R')
                self.ln(10)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.set_text_color(150, 150, 150)
                self.cell(w=0, h=10, text=f'Page {self.page_no()}', align='C')

        pdf = NotesPDF(orientation="P", unit="mm", format="A4")
        pdf.set_margins(left=15, top=15, right=15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Cover / Header Title
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(w=pdf.epw, h=12, text=f"{subject_name} Revision Notes", new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(w=pdf.epw, h=7, text=f"Generated automatically by StudyLens AI", new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.ln(3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(6)
        
        for line in master_markdown.split('\n'):
            line_str = line.strip()
            if not line_str:
                pdf.ln(2)
                continue
                
            # Clean non-ascii/special characters for standard fpdf font
            safe_text = line_str.encode('latin-1', 'replace').decode('latin-1')
            safe_text = safe_text.replace('?', ' ')
            
            if line_str.startswith('# '):
                continue
            elif line_str.startswith('## '):
                pdf.ln(3)
                pdf.set_font('Helvetica', 'B', 13)
                pdf.set_text_color(30, 27, 75)
                heading = safe_text.replace('## ', '')
                pdf.multi_cell(w=pdf.epw, h=7, text=heading)
                pdf.ln(1)
            elif line_str.startswith('### '):
                pdf.ln(2)
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_text_color(67, 56, 202)
                subheading = safe_text.replace('### ', '')
                pdf.multi_cell(w=pdf.epw, h=6, text=subheading)
            elif line_str.startswith('> '):
                pdf.set_font('Helvetica', 'I', 9.5)
                pdf.set_text_color(71, 85, 105)
                quote_text = safe_text.replace('> ', '').replace('**', '')
                pdf.multi_cell(w=pdf.epw, h=5.5, text=quote_text)
            elif line_str.startswith('- ') or line_str.startswith('* '):
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(30, 41, 59)
                bullet_text = "  - " + safe_text[2:].replace('**', '')
                pdf.multi_cell(w=pdf.epw, h=5.5, text=bullet_text)
            else:
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(51, 65, 85)
                plain_text = safe_text.replace('**', '').replace('`', '')
                pdf.multi_cell(w=pdf.epw, h=5.5, text=plain_text)
                
        return bytes(pdf.output())
    except Exception as e:
        print(f"PDF generation error: {e}")
        return master_markdown.encode('utf-8')


