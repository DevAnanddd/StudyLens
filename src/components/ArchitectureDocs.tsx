import React, { useState } from "react";
import {
  Layers,
  GitMerge,
  ShieldCheck,
  Timer,
  FileCheck2,
  Cpu,
  Sliders,
} from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export const ArchitectureDocs: React.FC = () => {
  const { theme } = useTheme();
  const [activeSection, setActiveSection] = useState<
    "pipeline" | "grouping" | "batching" | "attribution"
  >("pipeline");

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className={`${theme.bgCard} rounded-2xl p-6 sm:p-8 border ${theme.borderMain} ${theme.bgElevated} pro-card card-spotlight animate-fadeInUp`}>
        <div className={`flex items-center gap-2 ${theme.accentText} text-xs font-mono font-bold uppercase tracking-wider mb-2`}>
          <Cpu className="w-4 h-4" />
          <span>System Architecture & Engineering Specification</span>
        </div>
        <h2 className={`text-2xl sm:text-3xl font-bold ${theme.textPrimary} ${theme.headingFont} tracking-tight`}>
          StudyLens <span className="gradient-text-cool">AI Engine Design</span>
        </h2>
        <p className={`text-sm ${theme.textMuted} mt-1 max-w-3xl leading-relaxed`}>
          Comprehensive specification covering multi-stage batching, token economy, deterministic clustering algorithms, exponential backoff with jitter, and end-to-end source attribution traceability.
        </p>

        {/* Section Navigation */}
        <div
          role="tablist"
          aria-label="Architecture specification sections"
          className={`mobile-scroll-tabs flex-wrap sm:flex-wrap gap-2 mt-6 pt-6 border-t ${theme.borderSubtle} stagger-children overflow-x-auto hide-scrollbar`}
        >
          <button
            role="tab"
            id="arch-tab-pipeline"
            aria-selected={activeSection === "pipeline"}
            aria-controls="arch-panel-pipeline"
            onClick={() => setActiveSection("pipeline")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer shrink-0 ${
              activeSection === "pipeline"
                ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
            }`}
          >
            <Layers className="w-4 h-4" />
            <span className="whitespace-nowrap">1. Batching Pipeline (50–200 Slides)</span>
          </button>

          <button
            role="tab"
            id="arch-tab-grouping"
            aria-selected={activeSection === "grouping"}
            aria-controls="arch-panel-grouping"
            onClick={() => setActiveSection("grouping")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer shrink-0 ${
              activeSection === "grouping"
                ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
            }`}
          >
            <GitMerge className="w-4 h-4" />
            <span className="whitespace-nowrap">2. Topic Grouping & Merge Logic</span>
          </button>

          <button
            role="tab"
            id="arch-tab-batching"
            aria-selected={activeSection === "batching"}
            aria-controls="arch-panel-batching"
            onClick={() => setActiveSection("batching")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer shrink-0 ${
              activeSection === "batching"
                ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span className="whitespace-nowrap">3. Batch Sizes, Configs & Rate Limits</span>
          </button>

          <button
            role="tab"
            id="arch-tab-attribution"
            aria-selected={activeSection === "attribution"}
            aria-controls="arch-panel-attribution"
            onClick={() => setActiveSection("attribution")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer shrink-0 ${
              activeSection === "attribution"
                ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
            }`}
          >
            <FileCheck2 className="w-4 h-4" />
            <span className="whitespace-nowrap">4. End-to-End Source Attribution</span>
          </button>
        </div>
      </div>

      {/* SECTION 1: BATCHING PIPELINE */}
      {activeSection === "pipeline" && (
        <div
          role="tabpanel"
          id="arch-panel-pipeline"
          aria-labelledby="arch-tab-pipeline"
          className="space-y-6"
        >
          <div className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-6`}>
            <div>
              <h3 className={`text-xl font-bold ${theme.textPrimary} ${theme.headingFont}`}>
                Four-Stage Pipeline for 50–200 Slide Decks
              </h3>
              <p className={`text-sm ${theme.textMuted} mt-1 leading-relaxed`}>
                Sending 200 slides in a single prompt causes prompt truncation, degraded reasoning, lost technical entities, and high latency. StudyLens utilizes a decoupled map-cluster-reduce architecture.
              </p>
            </div>

            {/* Architecture Pipeline Diagram */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <div className={`flex items-center justify-between text-xs font-mono font-bold ${theme.accentText} uppercase`}>
                  <span>Stage 1</span>
                  <span>Fast & Cheap</span>
                </div>
                <h4 className={`font-bold ${theme.textPrimary} text-sm mt-1`}>Lightweight Tagging</h4>
                <p className={`text-xs ${theme.textMuted} mt-1 leading-relaxed`}>
                  Batches of 10–15 slides sent to Gemini with structured JSON schema to extract canonical topic titles and keywords.
                </p>
                <div className={`mt-3 text-[11px] font-mono ${theme.accentText} ${theme.accentBgSubtle} px-2 py-1 rounded border ${theme.accentBorder}`}>
                  ~150 tokens/slide input
                </div>
              </div>

              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <div className="flex items-center justify-between text-xs font-mono font-bold text-purple-600 dark:text-purple-400 uppercase">
                  <span>Stage 2</span>
                  <span>Deterministic</span>
                </div>
                <h4 className={`font-bold ${theme.textPrimary} text-sm mt-1`}>Topic Clustering</h4>
                <p className={`text-xs ${theme.textMuted} mt-1 leading-relaxed`}>
                  Runs localized tag smoothing, merges non-consecutive slides into canonical buckets, and absorbs straggler slides.
                </p>
                <div className="mt-3 text-[11px] font-mono text-purple-700 dark:text-purple-300 bg-purple-500/10 px-2 py-1 rounded border border-purple-500/20">
                  0 LLM tokens (local CPU)
                </div>
              </div>

              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <div className="flex items-center justify-between text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400 uppercase">
                  <span>Stage 3</span>
                  <span>Deep Synthesis</span>
                </div>
                <h4 className={`font-bold ${theme.textPrimary} text-sm mt-1`}>Cluster Summarization</h4>
                <p className={`text-xs ${theme.textMuted} mt-1 leading-relaxed`}>
                  Applies the Master System Prompt per topic cluster (6–18 slides) to produce clean Markdown with formulas and definitions.
                </p>
                <div className="mt-3 text-[11px] font-mono text-emerald-700 dark:text-emerald-300 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                  Gemini 3.7 Flash
                </div>
              </div>

              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <div className="flex items-center justify-between text-xs font-mono font-bold text-amber-600 dark:text-amber-400 uppercase">
                  <span>Stage 4</span>
                  <span>Assembly</span>
                </div>
                <h4 className={`font-bold ${theme.textPrimary} text-sm mt-1`}>Master Assembly</h4>
                <p className={`text-xs ${theme.textMuted} mt-1 leading-relaxed`}>
                  Generates Table of Contents, extracts and deduplicates definitions into a global master glossary, and unifies sources.
                </p>
                <div className="mt-3 text-[11px] font-mono text-amber-700 dark:text-amber-300 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20">
                  Single Master Revision Doc
                </div>
              </div>
            </div>

            {/* Math & Token Breakdown Table */}
            <div className="mt-6">
              <h4 className={`text-base font-bold ${theme.textPrimary} ${theme.headingFont} mb-3`}>
                Token & Request Budgeting (100 Slides Example)
              </h4>
              <div className="overflow-x-auto">
                <table className={`w-full text-xs text-left border ${theme.borderMain} rounded-lg`}>
                  <thead className={`${theme.bgSurface} ${theme.textMuted} border-b ${theme.borderMain} font-mono`}>
                    <tr>
                      <th className="p-2.5 font-semibold">Stage</th>
                      <th className="p-2.5 font-semibold">Requests</th>
                      <th className="p-2.5 font-semibold">Avg Input Tokens / Req</th>
                      <th className="p-2.5 font-semibold">Avg Output Tokens / Req</th>
                      <th className="p-2.5 font-semibold">Total Stage Time (Parallel)</th>
                    </tr>
                  </thead>
                  <tbody className={`divide-y ${theme.borderSubtle} ${theme.textSecondary} font-mono`}>
                    <tr>
                      <td className={`p-2.5 font-bold ${theme.textPrimary}`}>1. Lightweight Tagging</td>
                      <td className="p-2.5">10 reqs (10 slides/batch)</td>
                      <td className="p-2.5">~1,500 tokens</td>
                      <td className="p-2.5">~400 tokens (JSON)</td>
                      <td className="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">~2.5s (with concurrency 4)</td>
                    </tr>
                    <tr>
                      <td className={`p-2.5 font-bold ${theme.textPrimary}`}>2. Local Clustering</td>
                      <td className="p-2.5">0 (In-Memory)</td>
                      <td className="p-2.5">0</td>
                      <td className="p-2.5">0</td>
                      <td className="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">&lt; 5ms</td>
                    </tr>
                    <tr>
                      <td className={`p-2.5 font-bold ${theme.textPrimary}`}>3. Topic Summarization</td>
                      <td className="p-2.5">~8 reqs (8 clusters)</td>
                      <td className="p-2.5">~2,200 tokens</td>
                      <td className="p-2.5">~900 tokens (Markdown)</td>
                      <td className="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">~4.5s (with concurrency 3)</td>
                    </tr>
                    <tr>
                      <td className={`p-2.5 font-bold ${theme.textPrimary}`}>4. Master Assembly</td>
                      <td className="p-2.5">0 (Client/Server merge)</td>
                      <td className="p-2.5">0</td>
                      <td className="p-2.5">0</td>
                      <td className="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">&lt; 10ms</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 2: GROUPING LOGIC */}
      {activeSection === "grouping" && (
        <div
          role="tabpanel"
          id="arch-panel-grouping"
          aria-labelledby="arch-tab-grouping"
          className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-6`}
        >
          <h3 className={`text-xl font-bold ${theme.textPrimary} ${theme.headingFont}`}>
            Clustering & Merge Logic Specification
          </h3>
          <p className={`text-sm ${theme.textMuted} leading-relaxed`}>
            Real lecture slide decks frequently have non-consecutive topics (e.g. Professor introduces Topic A on slides 1-4, switches to Topic B, then returns to Topic A on slides 12-14), mislabeled OCR tags, and tiny isolated slides. Here is the exact algorithm to resolve them:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Rule 1 */}
            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} space-y-2`}>
              <div className={`flex items-center gap-2 ${theme.accentText} font-mono font-bold text-xs`}>
                <GitMerge className="w-4 h-4" />
                <span>1. Non-Consecutive Aggregation</span>
              </div>
              <p className={`text-xs ${theme.textMuted} leading-relaxed`}>
                Topic tags are canonicalized using stop-word stripping and Dice coefficient bigram matching (<span className={`font-mono ${theme.textPrimary}`}>≥ 0.65</span>). Slides with the same canonical key (e.g. <code>"Virtual Memory"</code>) are merged into one cluster regardless of page distance.
              </p>
            </div>

            {/* Rule 2 */}
            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} space-y-2`}>
              <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-mono font-bold text-xs">
                <Sliders className="w-4 h-4" />
                <span>2. Sliding-Window Smoothing</span>
              </div>
              <p className={`text-xs ${theme.textMuted} leading-relaxed`}>
                If an isolated slide is tagged <code>"Hardware"</code> in the middle of a continuous sequence tagged <code>"Paging Architecture"</code> with low confidence (&lt;0.85), a 3-slide sliding window majority filter re-assigns the tag to <code>"Paging Architecture"</code>.
              </p>
            </div>

            {/* Rule 3 */}
            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} space-y-2`}>
              <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-mono font-bold text-xs">
                <ShieldCheck className="w-4 h-4" />
                <span>3. Tiny Group Absorption</span>
              </div>
              <p className={`text-xs ${theme.textMuted} leading-relaxed`}>
                Any cluster with <span className={`font-mono ${theme.textPrimary}`}>≤ 2</span> slides is evaluated for semantic similarity against adjacent clusters. If similarity exceeds <span className={`font-mono ${theme.textPrimary}`}>0.4</span>, it is absorbed into the parent topic; otherwise, it merges into the nearest chronological section.
              </p>
            </div>
          </div>

          {/* Pseudocode Box */}
          <div className={`rounded-xl p-5 border ${theme.borderMain} ${theme.codeBg}`}>
            <div className={`text-xs font-mono ${theme.textMuted} mb-2`}>// Grouping Algorithm Pseudocode</div>
            <pre className={`font-mono text-xs ${theme.codeText} overflow-x-auto whitespace-pre-wrap leading-relaxed`}>
{`function clusterSlides(rawSlides, taggedSlides):
  // 1. Sliding window noise smoothing (window size = 3)
  smoothedTags = smoothMislabeledTags(taggedSlides)

  // 2. Fuzzy canonical topic aggregation
  buckets = Map<CanonicalTopicKey, List<Slide>>()
  for slide in smoothedTags:
    canonKey = canonicalize(slide.topic)
    matchKey = findBestMatch(canonKey, buckets.keys(), threshold=0.65)
    buckets[matchKey ?? canonKey].append(slide)

  // 3. Straggler absorption (clusters with <= 2 slides)
  for [key, cluster] in buckets:
    if cluster.size <= 2:
      parentKey = findClosestCluster(key, buckets, minThreshold=0.40)
      if parentKey:
        buckets[parentKey].merge(cluster)
        buckets.remove(key)

  // 4. Split oversize clusters (> 18 slides)
  return partitionOversizeClusters(buckets, maxPerCluster=18)`}
            </pre>
          </div>
        </div>
      )}

      {/* SECTION 3: BATCH SIZES & RATE LIMITS */}
      {activeSection === "batching" && (
        <div
          role="tabpanel"
          id="arch-panel-batching"
          aria-labelledby="arch-tab-batching"
          className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-6`}
        >
          <h3 className={`text-xl font-bold ${theme.textPrimary} ${theme.headingFont}`}>
            Batch Size, Hyperparameters & Rate Limit Resilience
          </h3>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <h4 className={`text-xs font-mono font-bold ${theme.accentText} uppercase`}>Recommended Batch Sizes</h4>
                <ul className={`mt-2 space-y-1.5 text-xs ${theme.textMuted} list-disc pl-4 leading-relaxed`}>
                  <li><strong>Topic Tagging Batch:</strong> 10 – 15 slides per request.</li>
                  <li><strong>Cluster Summarization Batch:</strong> 6 – 18 slides per topic.</li>
                  <li><strong>Oversize Threshold:</strong> Clusters &gt; 18 slides are automatically divided into <em>(Part 1)</em>, <em>(Part 2)</em> to avoid token exhaustion.</li>
                </ul>
              </div>

              <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain}`}>
                <h4 className={`text-xs font-mono font-bold ${theme.accentText} uppercase`}>Generation Configuration</h4>
                <ul className={`mt-2 space-y-1.5 text-xs ${theme.textMuted} list-disc pl-4 leading-relaxed`}>
                  <li><strong>Tagging Temperature:</strong> <code>0.1</code> (strictly deterministic JSON).</li>
                  <li><strong>Summarization Temperature:</strong> <code>0.2</code> (factual precision, zero creative invention).</li>
                  <li><strong>topP:</strong> <code>0.95</code> | <strong>Seed:</strong> Optional fixed seed for reproducible test suites.</li>
                </ul>
              </div>
            </div>

            {/* Rate Limit Strategy */}
            <div className={`p-5 rounded-xl ${theme.accentBgSubtle} border ${theme.accentBorder} space-y-3`}>
              <div className={`flex items-center gap-2 ${theme.accentText} font-mono font-bold text-sm`}>
                <Timer className="w-4 h-4" />
                <span>Rate-Limit & Retry Strategy (429 & 503 Mitigation)</span>
              </div>
              <p className={`text-xs ${theme.textPrimary} leading-relaxed`}>
                When processing 200 slides, rate limit spikes (HTTP 429) can occur. StudyLens applies a 3-layer safety protocol:
              </p>
              <ol className={`list-decimal pl-5 space-y-1.5 text-xs ${theme.textSecondary} leading-relaxed`}>
                <li><strong>Concurrency Control:</strong> Limit simultaneous requests to 3–4 workers using a promise queue pool.</li>
                <li><strong>Exponential Backoff with Full Jitter:</strong>
                  <code className={`ml-1 ${theme.codeBg} ${theme.codeText} px-2 py-0.5 rounded border ${theme.borderMain} font-mono text-[11px]`}>
                    delay = min(max_ms, base_ms * 2^attempt) + uniform(0, jitter)
                  </code>
                </li>
                <li><strong>Partial Checkpointing:</strong> Store completed cluster summaries in state so a transient network failure only retries the uncompleted cluster.</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 4: SOURCE ATTRIBUTION */}
      {activeSection === "attribution" && (
        <div
          role="tabpanel"
          id="arch-panel-attribution"
          aria-labelledby="arch-tab-attribution"
          className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-6`}
        >
          <h3 className={`text-xl font-bold ${theme.textPrimary} ${theme.headingFont}`}>
            How Source Attribution Survives Every Pipeline Stage
          </h3>
          <p className={`text-sm ${theme.textMuted} leading-relaxed`}>
            For academic study notes, students need to verify every bullet point against original slide page numbers. Here is how attribution is guaranteed through each transformation:
          </p>

          <div className="space-y-4">
            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} flex items-start gap-3`}>
              <span
                className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-mono font-bold shrink-0"
                style={{ backgroundColor: theme.accentColor }}
              >
                1
              </span>
              <div className={`text-xs ${theme.textSecondary} leading-relaxed`}>
                <strong className={theme.textPrimary}>Slide Ingestion UID:</strong> Every slide is assigned an immutable composite key: <code>{`\${filename}#p\${pageNumber}`}</code>.
              </div>
            </div>

            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} flex items-start gap-3`}>
              <span
                className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-mono font-bold shrink-0"
                style={{ backgroundColor: theme.accentColor }}
              >
                2
              </span>
              <div className={`text-xs ${theme.textSecondary} leading-relaxed`}>
                <strong className={theme.textPrimary}>Tagging Preservation:</strong> The structured JSON response matches <code>slideId</code> directly back to the slide record, ensuring tag associations never lose origin metadata.
              </div>
            </div>

            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} flex items-start gap-3`}>
              <span
                className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-mono font-bold shrink-0"
                style={{ backgroundColor: theme.accentColor }}
              >
                3
              </span>
              <div className={`text-xs ${theme.textSecondary} leading-relaxed`}>
                <strong className={theme.textPrimary}>Cluster Source Manifest Injection:</strong> When invoking the summarizer prompt, an explicit <code>### SLIDE SOURCE MANIFEST</code> is prepended. The system prompt mandates the final <code>## Sources</code> section list every contributing slide.
              </div>
            </div>

            <div className={`p-4 rounded-xl ${theme.bgSurface} border ${theme.borderMain} flex items-start gap-3`}>
              <span
                className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-mono font-bold shrink-0"
                style={{ backgroundColor: theme.accentColor }}
              >
                4
              </span>
              <div className={`text-xs ${theme.textSecondary} leading-relaxed`}>
                <strong className={theme.textPrimary}>Master Glossary Cross-Referencing:</strong> When terms are merged into the deduplicated global glossary, the set of contributing source filenames and pages is aggregated into the definition metadata.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
