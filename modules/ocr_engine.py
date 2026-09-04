from typing import List, Dict, Any, Optional
from PIL import Image
import os
import io
import json
import base64
import urllib.request


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


def run_ocr_gemini_vision(image: Image.Image, api_key: str, model: str = "gemini-3.6-flash") -> Dict[str, Any]:
    """Uses Gemini's multimodal vision to transcribe an image -- much stronger than
    classic OCR (Tesseract/EasyOCR) on handwriting, cursive, and math notation."""
    if not api_key:
        raise RuntimeError("No Gemini API key available for Vision OCR.")

    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=90)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt_text = (
        "Transcribe ALL text, numbers, mathematical formulas, and symbols visible in this image "
        "exactly as written -- including handwritten notes, equations, subscripts, fractions, and "
        "summations. Preserve mathematical notation using clear plain-text notation (e.g. P(E|A) for "
        "conditional probability, sum(i=1 to n) for summation). Do not summarize, explain, or add any "
        "commentary of your own -- output ONLY the transcribed content, nothing else."
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }],
        "generationConfig": {"temperature": 0.1}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        raise RuntimeError(f"Gemini Vision OCR error: {e}")

    return {
        "text": text,
        "confidence": 0.95,
        "word_count": len(text.split()),
        "engine": "Gemini Vision"
    }


def extract_text_from_slide(slide: Dict[str, Any], preferred_engine: str = "Tesseract", api_key: Optional[str] = None) -> Dict[str, Any]:
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

    if preferred_engine == "Gemini Vision":
        try:
            # Use the original (not preprocessed) image -- CLAHE/denoising is tuned
            # for classic OCR engines and isn't needed for Gemini's vision model.
            ocr_result = run_ocr_gemini_vision(slide["image"], api_key=api_key)
        except Exception as e:
            error_msg += f" Gemini Vision error: {e}."

        # If Gemini Vision fails (e.g. rate limit, no key), fall back to classic OCR
        # rather than leaving the slide with no text at all.
        if not ocr_result or not ocr_result.get("text"):
            for eng in ["EasyOCR", "Tesseract"]:
                try:
                    ocr_result = run_ocr_easyocr(img_to_ocr) if eng == "EasyOCR" else run_ocr_tesseract(img_to_ocr)
                    if ocr_result and ocr_result.get("text"):
                        ocr_result["vision_fallback"] = True
                        ocr_result["vision_fallback_reason"] = error_msg.strip()
                        break
                except Exception as e:
                    error_msg += f" {eng} error: {e}."
    else:
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
