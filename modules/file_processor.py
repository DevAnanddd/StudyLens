from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import io
from modules.pdf_processor import extract_pdf_pages

def process_uploaded_files(uploaded_files: List[Any]) -> List[Dict[str, Any]]:
    slides: List[Dict[str, Any]] = []
    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        ext = Path(filename).suffix.lower().lstrip('.')
        file_bytes = uploaded_file.getvalue()
        if ext == 'pdf':
            try:
                pdf_slides = extract_pdf_pages(file_bytes, source_name=filename)
                slides.extend(pdf_slides)
            except Exception as e:
                print(f"Error processing PDF {filename}: {e}")
        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
            try:
                pil_img = Image.open(io.BytesIO(file_bytes)).convert('RGB')
                slide_id = f"{Path(filename).stem}_s1"
                slides.append({
                    'id': slide_id,
                    'source_file': filename,
                    'slide_index': 1,
                    'total_slides': 1,
                    'image': pil_img,
                    'original_type': 'image'
                })
            except Exception as e:
                print(f"Error processing image {filename}: {e}")
    return slides
