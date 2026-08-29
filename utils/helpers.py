import io
import shutil
from pathlib import Path
from typing import Union
from PIL import Image
import numpy as np

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    try:
        import cv2
        rgb = np.array(pil_img.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Exception:
        return np.array(pil_img.convert("RGB"))

def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    try:
        import cv2
        if len(cv_img.shape) == 2:
            return Image.fromarray(cv_img)
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    except Exception:
        return Image.fromarray(cv_img)

def pil_to_bytes(pil_img: Image.Image, format: str = "PNG") -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    return buf.getvalue()

def clear_directory(dir_path: Path):
    if dir_path.exists():
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
