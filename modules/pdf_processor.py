from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import io

def extract_pdf_pages(pdf_path_or_bytes: Any, source_name: str, zoom: float = 2.0) -> List[Dict[str, Any]]:
    slides = []
    try:
        import pypdf
        if isinstance(pdf_path_or_bytes, (str, Path)):
            reader = pypdf.PdfReader(str(pdf_path_or_bytes))
        else:
            reader = pypdf.PdfReader(io.BytesIO(pdf_path_or_bytes))
        total_pages = len(reader.pages)
        for page_num, page in enumerate(reader.pages):
            pil_img = None
            for img_obj in page.images:
                try:
                    pil_img = Image.open(io.BytesIO(img_obj.data)).convert('RGB')
                    break
                except Exception:
                    continue
            if pil_img is None:
                pil_img = Image.new('RGB', (1000, 650), color=(250, 250, 250))
            slide_id = f"{Path(source_name).stem}_p{page_num + 1}"
            slides.append({
                'id': slide_id,
                'source_file': source_name,
                'slide_index': page_num + 1,
                'total_slides': total_pages,
                'image': pil_img,
                'original_type': 'pdf',
                'direct_text': page.extract_text() or ''
            })
        return slides
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return slides
