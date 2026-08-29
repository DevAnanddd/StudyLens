from typing import Dict, Any, Tuple
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np

def preprocess_slide_image(
    pil_img: Image.Image,
    apply_clahe: bool = True,
    apply_denoise: bool = True,
    apply_sharpen: bool = True,
    max_dim: int = 2000
) -> Tuple[Image.Image, Image.Image]:
    w, h = pil_img.size
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        
    try:
        import cv2
        from utils.helpers import pil_to_cv2
        img_bgr = pil_to_cv2(pil_img)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        if apply_denoise:
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        else:
            denoised = gray
            
        if apply_clahe:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
        else:
            enhanced = denoised
            
        if apply_sharpen:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
            sharpened = cv2.filter2D(enhanced, -1, kernel)
        else:
            sharpened = enhanced
            
        processed_pil = Image.fromarray(sharpened)
        return processed_pil, pil_img
    except Exception:
        gray = ImageOps.grayscale(pil_img)
        if apply_clahe:
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.4)
        else:
            enhanced = gray
            
        if apply_denoise:
            denoised = enhanced.filter(ImageFilter.MedianFilter(size=3))
        else:
            denoised = enhanced
            
        if apply_sharpen:
            sharpened = denoised.filter(ImageFilter.SHARPEN)
        else:
            sharpened = denoised
            
        return sharpened, pil_img
