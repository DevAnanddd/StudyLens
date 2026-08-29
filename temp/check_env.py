import sys

modules = [streamlit, cv2, fitz, PIL, imagehash, numpy, easyocr, pytesseract, google.generativeai]
missing = []

for m in modules:
    try:
        __import__(m)
        print(f[OK] {m} is available)
    except ImportError as e:
        print(f[MISSING] {m} ({e}))
        missing.append(m)

if missing:
    print(f\nMissing packages: {missing})
else:
    print(\nAll dependencies ready!)