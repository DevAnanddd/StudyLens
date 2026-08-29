import { SlideOCRInput, TaggedSlide, TopicCluster } from "../types";

/**
 * Normalizes a raw topic string into a clean, canonical key for grouping.
 * Strips punctuation, removes common filler words, trims whitespace, and converts to lowercase.
 */
export function canonicalizeTopicName(rawTopic: string): string {
  if (!rawTopic) return "general_concepts";
  return rawTopic
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\b(intro|introduction|basics|overview|part\s*\d+|lecture\s*\d+)\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Calculates string similarity using Dice's Bigram Coefficient.
 * Fast and highly effective for canonicalizing fuzzy topic names without external dependencies.
 */
export function stringSimilarity(str1: string, str2: string): number {
  const s1 = canonicalizeTopicName(str1);
  const s2 = canonicalizeTopicName(str2);

  if (s1 === s2) return 1.0;
  if (s1.length < 2 || s2.length < 2) return 0.0;

  const getBigrams = (str: string) => {
    const bigrams = new Set<string>();
    for (let i = 0; i < str.length - 1; i++) {
      bigrams.add(str.substring(i, i + 2));
    }
    return bigrams;
  };

  const bg1 = getBigrams(s1);
  const bg2 = getBigrams(s2);
  let intersection = 0;

  for (const b of bg1) {
    if (bg2.has(b)) intersection++;
  }

  return (2.0 * intersection) / (bg1.size + bg2.size);
}

/**
 * Stage 2.1: Contextual Smoothing (Sliding Window Mislabeled Tag Filter)
 * If an isolated slide is surrounded by identical topic tags (e.g., [A, A, B_noisy, A, A]),
 * and B has low confidence or high keyword overlap with A, smooth B's tag to A.
 */
export function smoothMislabeledTags(taggedSlides: TaggedSlide[]): TaggedSlide[] {
  if (taggedSlides.length < 3) return [...taggedSlides];

  const smoothed = taggedSlides.map((s) => ({ ...s }));

  for (let i = 1; i < smoothed.length - 1; i++) {
    const prev = smoothed[i - 1];
    const curr = smoothed[i];
    const next = smoothed[i + 1];

    const prevCanon = canonicalizeTopicName(prev.topic);
    const nextCanon = canonicalizeTopicName(next.topic);
    const currCanon = canonicalizeTopicName(curr.topic);

    // If surrounding neighbors agree and current slide disagrees
    if (prevCanon === nextCanon && currCanon !== prevCanon) {
      // Check if current slide is an isolated outlier (e.g. low confidence or short content)
      if (curr.confidence < 0.85 || curr.slideType === "content") {
        curr.topic = prev.topic; // Reassign to dominant neighbor topic
        if (!curr.subtopic && prev.subtopic) {
          curr.subtopic = prev.subtopic;
        }
      }
    }
  }

  return smoothed;
}

/**
 * Stage 2.2: Cluster Formation & Non-Consecutive Topic Aggregation
 * Groups slides by canonical topic key, merging slides that belong to the same topic
 * even if they appear non-consecutively across different lecture decks.
 */
export function clusterSlidesByTopic(
  rawSlides: SlideOCRInput[],
  taggedSlides: TaggedSlide[],
  options: {
    similarityThreshold?: number;
    minClusterSize?: number;
    maxClusterSize?: number;
  } = {}
): TopicCluster[] {
  const {
    similarityThreshold = 0.65,
    minClusterSize = 2,
    maxClusterSize = 18,
  } = options;

  const slideMap = new Map<string, SlideOCRInput>();
  rawSlides.forEach((s) => slideMap.set(s.id, s));

  // 1. Contextual tag smoothing
  const smoothedTags = smoothMislabeledTags(taggedSlides);

  // 2. Aggregate into canonical topic buckets with fuzzy matching
  const topicBuckets: Array<{
    canonicalName: string;
    displayTitle: string;
    slideIds: string[];
  }> = [];

  for (const tagged of smoothedTags) {
    const canon = canonicalizeTopicName(tagged.topic);

    // Find if an existing bucket matches closely (exact or above similarity threshold)
    let matchedBucket = topicBuckets.find(
      (b) => b.canonicalName === canon || stringSimilarity(b.canonicalName, canon) >= similarityThreshold
    );

    if (matchedBucket) {
      matchedBucket.slideIds.push(tagged.slideId);
      // Prefer longer, cleaner display title
      if (tagged.topic.length > matchedBucket.displayTitle.length && !tagged.topic.includes("...")) {
        matchedBucket.displayTitle = tagged.topic;
      }
    } else {
      topicBuckets.push({
        canonicalName: canon,
        displayTitle: tagged.topic,
        slideIds: [tagged.slideId],
      });
    }
  }

  // 3. Stage 2.3: Outlier & Tiny Group Absorption
  // If a cluster has fewer than minClusterSize slides, attempt to merge with the closest cluster,
  // or aggregate into a comprehensive foundations/miscellaneous cluster if isolated.
  const refinedBuckets: typeof topicBuckets = [];
  const tinyBuckets: typeof topicBuckets = [];

  for (const bucket of topicBuckets) {
    if (bucket.slideIds.length >= minClusterSize) {
      refinedBuckets.push(bucket);
    } else {
      tinyBuckets.push(bucket);
    }
  }

  // Merge tiny buckets into the most similar valid cluster if possible
  for (const tiny of tinyBuckets) {
    let bestMatch: (typeof topicBuckets)[0] | null = null;
    let highestSim = 0;

    for (const valid of refinedBuckets) {
      const sim = stringSimilarity(tiny.canonicalName, valid.canonicalName);
      if (sim > highestSim) {
        highestSim = sim;
        bestMatch = valid;
      }
    }

    if (bestMatch && highestSim >= 0.4) {
      bestMatch.slideIds.push(...tiny.slideIds);
    } else if (refinedBuckets.length > 0) {
      // Absorb into nearest chronological neighbor or first cluster
      refinedBuckets[0].slideIds.push(...tiny.slideIds);
    } else {
      // No other valid buckets, keep it
      refinedBuckets.push(tiny);
    }
  }

  // 4. Construct final TopicCluster structures with source provenance
  const clusters: TopicCluster[] = [];

  refinedBuckets.forEach((bucket, index) => {
    // Deduplicate slide IDs
    const uniqueSlideIds = Array.from(new Set(bucket.slideIds));
    const clusterSlides = uniqueSlideIds
      .map((id) => slideMap.get(id))
      .filter((s): s is SlideOCRInput => !!s);

    if (clusterSlides.length === 0) return;

    // Split overly large clusters (> maxClusterSize) into sequential sub-parts
    if (clusterSlides.length > maxClusterSize) {
      const parts = Math.ceil(clusterSlides.length / maxClusterSize);
      for (let p = 0; p < parts; p++) {
        const slice = clusterSlides.slice(p * maxClusterSize, (p + 1) * maxClusterSize);
        clusters.push({
          id: `cluster_${index + 1}_part_${p + 1}`,
          topicName: `${bucket.displayTitle} (Part ${p + 1})`,
          normalizedKey: `${bucket.canonicalName}_part_${p + 1}`,
          slideIds: slice.map((s) => s.id),
          slides: slice,
          sources: slice.map((s) => ({ filename: s.filename, pageNumber: s.pageNumber })),
          status: "pending",
        });
      }
    } else {
      clusters.push({
        id: `cluster_${index + 1}`,
        topicName: bucket.displayTitle,
        normalizedKey: bucket.canonicalName,
        slideIds: uniqueSlideIds,
        slides: clusterSlides,
        sources: clusterSlides.map((s) => ({ filename: s.filename, pageNumber: s.pageNumber })),
        status: "pending",
      });
    }
  });

  return clusters;
}
