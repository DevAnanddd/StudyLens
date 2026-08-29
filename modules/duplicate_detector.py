from typing import List, Dict, Any, Tuple
from PIL import Image
import imagehash

def compute_slide_hashes(slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for slide in slides:
        img: Image.Image = slide['image']
        ph = imagehash.phash(img)
        dh = imagehash.dhash(img)
        slide['phash'] = ph
        slide['dhash'] = dh
        slide['phash_str'] = str(ph)
    return slides

def cluster_duplicates(
    slides: List[Dict[str, Any]],
    threshold: int = 5
) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
    if not slides:
        return [], []
    slides = compute_slide_hashes(slides)
    n = len(slides)
    parent = list(range(n))
    def find(i: int) -> int:
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]
    def union(i: int, j: int):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_j] = root_i
    for i in range(n):
        for j in range(i + 1, n):
            dist = slides[i]['phash'] - slides[j]['phash']
            if dist <= threshold:
                union(i, j)
    clusters_dict: Dict[int, List[Dict[str, Any]]] = {}
    for idx, slide in enumerate(slides):
        root = find(idx)
        if root not in clusters_dict:
            clusters_dict[root] = []
        primary_slide = slides[root]
        dist_from_primary = slide['phash'] - primary_slide['phash']
        slide_entry = dict(slide)
        slide_entry['hamming_dist'] = dist_from_primary
        slide_entry['is_primary'] = (idx == root)
        slide_entry['status'] = 'keep' if idx == root else 'flagged_duplicate'
        clusters_dict[root].append(slide_entry)
    duplicate_clusters = [cluster for cluster in clusters_dict.values() if len(cluster) > 1]
    unique_slides = [cluster[0] for cluster in clusters_dict.values()]
    return unique_slides, duplicate_clusters
