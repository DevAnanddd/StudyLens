import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_HASH_THRESHOLD = 5
DEFAULT_OCR_ENGINE = "EasyOCR"
DEFAULT_GEMINI_MODEL = "gemini-3.7-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

TOPIC_DETECTION_BATCH_SIZE = 8
SUMMARIZATION_BATCH_SIZE = 5

SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "webp"]
SUPPORTED_DOC_TYPES = ["pdf"]
ALL_SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES + SUPPORTED_DOC_TYPES

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
