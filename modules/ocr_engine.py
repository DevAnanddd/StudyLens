from typing import List, Dict, Any, Optional
from PIL import Image
import os

def run_ocr_tesseract(image: Image.Image) -> Dict[str, Any]:
    import pytesseract
    tess_path = os.getenv("TESSERACT_PATH")
    if not tess_path:
        for candidate in [
            r"C:\msys64\ucrt64\bin\tesseract.exe",
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]:
            if os.path.exists(candidate):
                tess_path = candidate
                break
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
        
    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        words = []
        confs = []
        for text, conf in zip(data["text"], data["conf"]):
            text_str = str(text).strip()
            if text_str and int(conf) > 0:
                words.append(text_str)
                confs.append(float(conf) / 100.0)
                
        full_text = pytesseract.image_to_string(image).strip()
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return {
            "text": full_text,
            "confidence": avg_conf,
            "word_count": len(full_text.split()),
            "engine": "Tesseract"
        }
    except Exception as e:
        raise RuntimeError(f"Tesseract execution error: {e}")

def run_ocr_easyocr(image: Image.Image) -> Dict[str, Any]:
    import easyocr
    import numpy as np
    reader = easyocr.Reader(["en"], gpu=False)
    img_np = np.array(image.convert("RGB"))
    results = reader.readtext(img_np)
    extracted_lines = []
    confidences = []
    for bbox, text, conf in results:
        cleaned = text.strip()
        if cleaned:
            extracted_lines.append(cleaned)
            confidences.append(float(conf))
    full_text = "\n".join(extracted_lines)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return {
        "text": full_text,
        "confidence": avg_conf,
        "word_count": len(full_text.split()),
        "engine": "EasyOCR"
    }

def extract_text_from_slide(slide: Dict[str, Any], preferred_engine: str = "Tesseract") -> Dict[str, Any]:
    if slide.get("direct_text") and len(slide["direct_text"].strip()) > 10:
        text = slide["direct_text"].strip()
        slide.update({
            "text": text,
            "confidence": 0.98,
            "word_count": len(text.split()),
            "engine": "PDF Direct Extraction"
        })
        return slide
        
    img_to_ocr = slide.get("preprocessed_image", slide["image"])
    ocr_result = None
    error_msg = ""
    engines = ["Tesseract", "EasyOCR"] if preferred_engine == "Tesseract" else ["EasyOCR", "Tesseract"]
    for eng in engines:
        try:
            if eng == "Tesseract":
                ocr_result = run_ocr_tesseract(img_to_ocr)
            else:
                ocr_result = run_ocr_easyocr(img_to_ocr)
            if ocr_result and ocr_result.get("text"):
                break
        except Exception as e:
            error_msg += f" {eng} error: {e}."
            
    if not ocr_result or not ocr_result.get("text"):
        ocr_result = {
            "text": slide.get("direct_text", ""),
            "confidence": 0.5 if slide.get("direct_text") else 0.0,
            "word_count": len(slide.get("direct_text", "").split()),
            "engine": "Fallback Direct",
            "error": error_msg.strip()
        }
    slide.update(ocr_result)
    return slide
