import sys
from PIL import Image, ImageDraw
from modules.image_preprocessor import preprocess_slide_image
from modules.duplicate_detector import cluster_duplicates
from modules.ocr_engine import extract_text_from_slide
from modules.ai_summarizer import detect_topics_batch, group_slides_by_topic, summarize_topic_group
from modules.note_generator import generate_master_notes
from modules.search_engine import RevisionSearchEngine

print(--- Running End-to-End Pipeline Smoke Test ---)

# 1. Create sample images
img1 = Image.new(RGB, (600, 300), color=(255, 255, 255))
d1 = ImageDraw.Draw(img1)
d1.text((30, 30), Gradient Descent Optimization, fill=(0, 0, 0))
d1.text((30, 70), Learning rate alpha controls step size., fill=(0, 0, 0))
d1.text((30, 110), Stochastic Gradient Descent uses mini-batches., fill=(0, 0, 0))

# Exact duplicate of img1
img2 = img1.copy()

# New slide
img3 = Image.new(RGB, (600, 300), color=(255, 255, 255))
d3 = ImageDraw.Draw(img3)
d3.text((30, 30), Activation Functions in Deep Learning, fill=(0, 0, 0))
d3.text((30, 70), ReLU: Rectified Linear Unit f(x) = max(0, x), fill=(0, 0, 0))
d3.text((30, 110), Sigmoid: Maps values between 0 and 1., fill=(0, 0, 0))

slides = [
    {id: slide_1, source_file: lecture.png, slide_index: 1, total_slides: 3, image: img1, original_type: image},
    {id: slide_2_dup, source_file: lecture_copy.png, slide_index: 2, total_slides: 3, image: img2, original_type: image},
    {id: slide_3, source_file: lecture.png, slide_index: 3, total_slides: 3, image: img3, original_type: image}
]

print(1. Testing OpenCV / Image Preprocessing...)
for s in slides:
    proc, _ = preprocess_slide_image(s[image])
    s[preprocessed_image] = proc
print( [OK] Preprocessing completed.)

print(2. Testing pHash Duplicate Detection...)
unique_slides, clusters = cluster_duplicates(slides, threshold=5)
print(f [OK] Total: {len(slides)}, Unique: {len(unique_slides)}, Clusters: {len(clusters)})
assert len(clusters) == 1, Should identify 1 duplicate cluster
assert len(unique_slides) == 2, Should have 2 unique slides

print(3. Testing OCR Extraction...)
for s in unique_slides:
    extract_text_from_slide(s, preferred_engine=Tesseract)
    print(f Slide {s['id']}: Engine={s.get('engine')} Text='{s.get('text')[:30]}...')

print(4. Testing Topic Grouping & Offline Summarization...)
unique_slides = detect_topics_batch(unique_slides, api_key=")
grouped = group_slides_by_topic(unique_slides)
summaries = []
for topic, topic_slides in grouped.items():
 s_obj = summarize_topic_group(topic, topic_slides, api_key=)
 summaries.append(s_obj)
print(f   [OK] Generated {len(summaries)} topic summaries.)

print(5. Testing Markdown Note Generation...)
notes_md = generate_master_notes(summaries, {unique_slides: len(unique_slides), total_words: 150})
print(   [OK] Notes Markdown generated successfully.)
print(f   Preview:\n{notes_md[:200]}...\n)

print(6. Testing Breadcrumb Search Engine...)
search_engine = RevisionSearchEngine(summaries, unique_slides)
results = search_engine.search(Gradient)
print(f   [OK] Search query 'Gradient' returned {len(results)} matches.)
for r in results:
 print(f      - Breadcrumb: {r['breadcrumb']} -> Snippet: {r['snippet']})

print(\n🎉 ALL TESTS PASSED SUCCESSFULLY!)
