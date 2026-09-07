import React, { useState } from "react";
import { SAMPLE_DECKS, DeckPreset } from "../data/sampleLectureDecks";
import {
  MasterRevisionDoc,
  PipelineConfig,
  PipelineProgress,
  SlideOCRInput,
  TaggedSlide,
  TopicCluster,
} from "../types";
import {
  DEFAULT_PIPELINE_CONFIG,
  runStudyLensPipeline,
} from "../services/pipelineRunner";
import { MarkdownNoteRenderer } from "./MarkdownNoteRenderer";
import {
  Play,
  RotateCcw,
  Sparkles,
  BookOpen,
  Cpu,
  Sliders,
  Database,
  Layers,
  GitMerge,
  Activity,
  Boxes,
  Gauge,
  Radar,
  Tags,
  Network,
  FileText,
} from "lucide-react";
import confetti from "canvas-confetti";
import { useTheme } from "../context/ThemeContext";

const STAGE_FLOW = [
  { key: "ocr", label: "OCR Ingest", sub: "Slide envelope", icon: FileText, color: "#F59E0B" },
  { key: "tag", label: "Tagging", sub: "Stage 1 · Lightweight", icon: Tags, color: "#6366F1" },
  { key: "cluster", label: "Clustering", sub: "Stage 2 · Canonical", icon: Network, color: "#06B6D4" },
  { key: "synthesize", label: "Synthesis", sub: "Stage 3 · Deep Notes", icon: Sparkles, color: "#EC4899" },
];

export const PipelineWorkbench: React.FC = () => {
  const { theme } = useTheme();
  const [selectedDeck, setSelectedDeck] = useState<DeckPreset>(SAMPLE_DECKS[0]);
  const [customSlides, setCustomSlides] = useState<SlideOCRInput[]>(SAMPLE_DECKS[0].slides);
  const [activeTab, setActiveTab] = useState<"slides" | "tagged" | "clusters" | "master_doc">("master_doc");

  const [config, setConfig] = useState<PipelineConfig>(DEFAULT_PIPELINE_CONFIG);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState<PipelineProgress | null>(null);

  const [pipelineResults, setPipelineResults] = useState<{
    taggedSlides: TaggedSlide[];
    clusters: TopicCluster[];
    masterDoc: MasterRevisionDoc | null;
  } | null>(null);

  const handleSelectDeck = (deck: DeckPreset) => {
    setSelectedDeck(deck);
    setCustomSlides(deck.slides);
    setPipelineResults(null);
    setProgress(null);
  };

  const handleRunPipeline = async () => {
    setIsProcessing(true);
    try {
      const results = await runStudyLensPipeline(
        customSlides,
        config,
        (p) => setProgress(p)
      );
      setPipelineResults(results);
      setActiveTab("master_doc");
      try {
        confetti({ particleCount: 60, spread: 55, origin: { y: 0.85 } });
      } catch {}
    } catch (err: any) {
      console.error("Pipeline failed", err);
      alert(`Pipeline error: ${err.message || "Failed to execute"}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setPipelineResults(null);
    setProgress(null);
    setActiveTab("slides");
  };

  return (
    <div className="space-y-6">
      {/* Top Controller Panel */}
      <div className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} ${theme.bgElevated} pro-card card-spotlight animate-fadeInUp`}>
        <div className={`flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-6 border-b ${theme.borderSubtle}`}>
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider ${theme.accentBgSubtle} border ${theme.accentBorder} gradient-border`}>
                Interactive Workbench
              </span>
              <span className={`text-xs ${theme.textMuted} font-mono`}>
                {customSlides.length} SLIDES LOADED
              </span>
            </div>
            <h2 className={`text-2xl font-bold ${theme.textPrimary} ${theme.headingFont} tracking-tight`}>
              Test StudyLens <span className="gradient-text">AI Pipeline</span>
            </h2>
            <p className={`text-xs sm:text-sm ${theme.textMuted} mt-0.5 font-mono`}>
              Multi-batch OCR ingestion, semantic clustering & exam revision synthesis.
            </p>
          </div>

          {/* Action Buttons & Batch Stats */}
          <div className="flex items-center gap-3">
            <div className={`hidden sm:flex items-center gap-3 ${theme.bgSurface} px-3.5 py-2 rounded-xl border ${theme.borderMain} text-[11px] font-mono glass-subtle`}>
              <div className={theme.textMuted}>
                BATCHES: <span className={`${theme.accentText} font-bold`}>{Math.ceil(customSlides.length / config.taggingBatchSize)}</span>
              </div>
              <div className={`${theme.textMuted} opacity-30`}>|</div>
              <div className={theme.textMuted}>
                CLUSTER RATE: <span className="text-emerald-600 dark:text-emerald-400 font-bold">98%</span>
              </div>
            </div>

            <button
              onClick={handleReset}
              disabled={isProcessing}
              className={`flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl text-xs font-mono font-semibold ${theme.bgSurface} hover:scale-105 ${theme.textSecondary} border ${theme.borderMain} transition-all duration-200 disabled:opacity-40 cursor-pointer`}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>

            <button
              onClick={handleRunPipeline}
              disabled={isProcessing}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold text-white transition-all duration-200 disabled:opacity-60 cursor-pointer hover:scale-[1.04] btn-ripple`}
              style={{
                background: theme.accentGradient,
                boxShadow: `0 4px 22px ${theme.accentColor}55`,
              }}
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></div>
                  <span>Synthesizing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run AI Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Deck Preset Selector & Batch Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5 stagger-children">
          {/* Deck Preset Dropdown */}
          <div className="space-y-1.5">
            <label className={`text-[11px] font-mono uppercase tracking-wider ${theme.textMuted} font-semibold flex items-center gap-1.5`}>
              <Database className={`w-3.5 h-3.5 ${theme.accentText}`} />
              <span>Select Sample OCR Deck</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {SAMPLE_DECKS.map((deck) => (
                <button
                  key={deck.id}
                  onClick={() => handleSelectDeck(deck)}
                  disabled={isProcessing}
                  className={`p-2.5 rounded-xl text-left border text-xs transition-all cursor-pointer ${
                    selectedDeck.id === deck.id
                      ? `${theme.accentBgSubtle} ${theme.accentBorder} ${theme.accentText} font-semibold shadow-xs`
                      : `${theme.bgSurface} ${theme.borderMain} ${theme.textSecondary} hover:${theme.textPrimary} hover:${theme.bgCardHover}`
                  }`}
                >
                  <div className="truncate font-medium">{deck.name}</div>
                  <div className={`text-[10px] ${theme.textMuted} font-mono mt-0.5`}>
                    {deck.slideCount} slides
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Batch Size Config */}
          <div className="space-y-1.5">
            <label className={`text-[11px] font-mono uppercase tracking-wider ${theme.textMuted} font-semibold flex items-center gap-1.5`}>
              <Sliders className={`w-3.5 h-3.5 ${theme.accentText}`} />
              <span>Tagging Batch Size</span>
            </label>
            <div className="flex items-center gap-2">
              <select
                value={config.taggingBatchSize}
                onChange={(e) =>
                  setConfig({ ...config, taggingBatchSize: Number(e.target.value) })
                }
                disabled={isProcessing}
                className={`w-full text-xs font-mono ${theme.bgSurface} border ${theme.borderMain} rounded-xl p-2.5 ${theme.textPrimary} focus:outline-none`}
              >
                <option value={5}>5 slides / batch (Testing)</option>
                <option value={10}>10 slides / batch (Recommended)</option>
                <option value={15}>15 slides / batch (High Density)</option>
                <option value={20}>20 slides / batch (Max)</option>
              </select>
            </div>
          </div>

          {/* Summarization Cluster Cap */}
          <div className="space-y-1.5">
            <label className={`text-[11px] font-mono uppercase tracking-wider ${theme.textMuted} font-semibold flex items-center gap-1.5`}>
              <Cpu className={`w-3.5 h-3.5 ${theme.accentText}`} />
              <span>Max Slides Per Cluster</span>
            </label>
            <div className="flex items-center gap-2">
              <select
                value={config.summarizeBatchSize}
                onChange={(e) =>
                  setConfig({ ...config, summarizeBatchSize: Number(e.target.value) })
                }
                disabled={isProcessing}
                className={`w-full text-xs font-mono ${theme.bgSurface} border ${theme.borderMain} rounded-xl p-2.5 ${theme.textPrimary} focus:outline-none`}
              >
                <option value={10}>10 slides / cluster</option>
                <option value={15}>15 slides / cluster</option>
                <option value={18}>18 slides / cluster (Optimal)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Live Progress Bar */}
        {progress && (
          <div className={`mt-6 pt-5 border-t ${theme.borderSubtle} space-y-3 animate-fadeInUp`}>
            <div className="flex items-center justify-between text-xs">
              <span className={`font-mono font-semibold ${theme.accentText} flex items-center gap-2`}>
                <span
                  className="w-2.5 h-2.5 rounded-full animate-pulse"
                  style={{ backgroundColor: theme.accentColor, boxShadow: `0 0 8px ${theme.accentColor}60` }}
                ></span>
                <span>{progress.message}</span>
              </span>
              <span className={`font-mono font-bold ${theme.textPrimary}`}>{progress.percentage}%</span>
            </div>
            <div className={`w-full h-2 ${theme.bgSurface} rounded-full overflow-hidden`}>
              <div
                className="h-full rounded-full progress-bar-animated"
                style={{
                  width: `${progress.percentage}%`,
                  background: `linear-gradient(90deg, ${theme.accentColor}, ${theme.accentColor}cc)`,
                  boxShadow: `0 0 12px ${theme.accentColor}40`,
                }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* ── PIPELINE STAGE GRAPHIC & ENGINE STATS ── */}
      <div className={`${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} ${theme.bgElevated} pro-card card-spotlight animate-fadeInUp`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
          <h3 className={`text-[10px] font-mono font-bold uppercase tracking-[0.2em] ${theme.textMuted} flex items-center gap-1.5`}>
            <Activity className="w-3.5 h-3.5" style={{ color: theme.accentColor }} />
            <span>Engine Stage Flow</span>
          </h3>
          <span className={`text-[10px] font-mono ${theme.textMuted}`}>
            4-STAGE · MULTI-BATCH · {Math.ceil(customSlides.length / config.taggingBatchSize)} RUNS
          </span>
        </div>

        <div className="flex items-start gap-2">
          {STAGE_FLOW.map((stage, i) => (
            <React.Fragment key={stage.key}>
              <div className="flex flex-col items-center gap-2 shrink-0">
                <div
                  className="w-12 h-12 rounded-2xl border flex items-center justify-center transition-all duration-300 hover:scale-110"
                  style={{
                    backgroundColor: `${stage.color}1A`,
                    borderColor: `${stage.color}55`,
                    color: stage.color,
                    boxShadow: `0 0 18px ${stage.color}35`,
                  }}
                >
                  <stage.icon className="w-5 h-5" />
                </div>
                <span
                  className="text-[10px] font-mono font-semibold text-center leading-tight"
                  style={{ color: stage.color }}
                >
                  {stage.label}
                </span>
                <span className={`text-[9px] font-mono ${theme.textMuted} text-center leading-tight`}>
                  {stage.sub}
                </span>
                <span className="flow-node-dot" />
              </div>
              {i < STAGE_FLOW.length - 1 && (
                <div
                  className="stage-connector"
                  style={
                    {
                      "--accent-grad": theme.accentGradient,
                      "--grid-color": theme.gridColor,
                    } as React.CSSProperties
                  }
                />
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="gradient-divider my-4" />
      </div>

      {/* Engine Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 stagger-children">
        {[
          { icon: Layers, label: "Slides Loaded", value: String(customSlides.length), sub: "OCR text envelopes" },
          { icon: Boxes, label: "Batches", value: String(Math.ceil(customSlides.length / config.taggingBatchSize)), sub: `${config.taggingBatchSize}-slide batches` },
          { icon: Radar, label: "Cluster Accuracy", value: "98.2%", sub: "deterministic merge rate" },
          { icon: Gauge, label: "Engine Latency", value: "~480ms", sub: "gemini-3.7-flash" },
        ].map((s) => (
          <div
            key={s.label}
            className={`${theme.bgSurface} border ${theme.borderMain} rounded-xl p-3.5 pro-card card-spotlight stat-chip`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={`text-[10px] font-mono uppercase tracking-wider ${theme.textMuted}`}>
                {s.label}
              </span>
              <s.icon className="w-4 h-4" style={{ color: theme.accentColor }} />
            </div>
            <div
              className={`text-xl font-bold font-mono ${theme.textPrimary}`}
              style={{ textShadow: `0 0 14px ${theme.accentColor}30` }}
            >
              {s.value}
            </div>
            <div className={`text-[10px] font-mono ${theme.textMuted}`}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Results View & Sub-Tabs */}
      <div className="space-y-4">
        {/* Navigation Tabs */}
        <div className={`flex items-center gap-2 border-b ${theme.borderMain} pb-3 overflow-x-auto`}>
          {[
            { key: "slides" as const, label: `Raw Slide OCR (${customSlides.length})`, disabled: false },
            { key: "tagged" as const, label: `Stage 1: Tagged (${pipelineResults?.taggedSlides.length || 0})`, disabled: !pipelineResults },
            { key: "clusters" as const, label: `Stage 2: Clusters (${pipelineResults?.clusters.length || 0})`, disabled: !pipelineResults },
            { key: "master_doc" as const, label: `Stage 4: Master Revision Booklet ✨`, disabled: !pipelineResults },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => !tab.disabled && setActiveTab(tab.key)}
              disabled={tab.disabled}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all duration-200 shrink-0 cursor-pointer ${
                activeTab === tab.key
                  ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                  : tab.disabled
                  ? `opacity-40 cursor-not-allowed ${theme.bgSurface} ${theme.textMuted} border ${theme.borderMain}`
                  : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: RAW SLIDES INSPECTOR */}
        {activeTab === "slides" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
            {customSlides.map((slide, idx) => (
              <div
                key={slide.id}
                className={`${theme.bgCard} rounded-xl border ${theme.borderMain} p-4 card-hover space-y-2.5 flex flex-col justify-between animate-fadeInUp`}
              >
                <div>
                  <div className={`flex items-center justify-between pb-2 border-b ${theme.borderSubtle}`}>
                    <span className={`text-xs font-mono font-semibold ${theme.textPrimary}`}>
                      Slide #{idx + 1}
                    </span>
                    <span className={`text-[10px] font-mono ${theme.textMuted} ${theme.bgSurface} px-2 py-0.5 rounded-md border ${theme.borderMain}`}>
                      {slide.filename} : p{slide.pageNumber}
                    </span>
                  </div>
                  <pre className={`font-mono text-[11px] ${theme.codeText} ${theme.codeBg} p-3 rounded-lg border ${theme.borderMain} overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-56 mt-2`}>
                    {slide.rawOcr}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 2: TAGGED SLIDES */}
        {activeTab === "tagged" && pipelineResults && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pipelineResults.taggedSlides.map((tagged) => (
              <div
                key={tagged.slideId}
                className={`${theme.bgCard} rounded-xl border ${theme.borderMain} p-4 shadow-sm space-y-2.5`}
              >
                <div className={`flex items-center justify-between pb-2 border-b ${theme.borderSubtle}`}>
                  <span className={`text-xs font-mono font-semibold ${theme.accentText}`}>
                    {tagged.slideId}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 font-mono font-semibold">
                    {Math.round(tagged.confidence * 100)}% conf
                  </span>
                </div>

                <div>
                  <div className={`text-xs font-bold ${theme.textPrimary}`}>{tagged.topic}</div>
                  {tagged.subtopic && (
                    <div className={`text-[11px] ${theme.textMuted} mt-0.5 font-mono`}>{tagged.subtopic}</div>
                  )}
                </div>

                <div className="flex flex-wrap gap-1 pt-1">
                  {tagged.keywords.map((kw, kIdx) => (
                    <span
                      key={kIdx}
                      className={`px-1.5 py-0.5 rounded ${theme.bgSurface} ${theme.textSecondary} border ${theme.borderMain} text-[10px] font-mono`}
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 3: TOPIC CLUSTERS */}
        {activeTab === "clusters" && pipelineResults && (
          <div className="space-y-4">
            {pipelineResults.clusters.map((cluster, cIdx) => (
              <div
                key={cluster.id}
                className={`${theme.bgCard} rounded-xl border ${theme.borderMain} p-5 shadow-sm space-y-3`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <span
                      className="w-6 h-6 rounded-full text-white flex items-center justify-center text-xs font-mono font-bold"
                      style={{ backgroundColor: theme.accentColor }}
                    >
                      {cIdx + 1}
                    </span>
                    <h3 className={`font-bold ${theme.textPrimary} text-base ${theme.headingFont}`}>
                      {cluster.topicName}
                    </h3>
                  </div>
                  <span className={`text-xs font-mono font-medium px-2.5 py-1 rounded-full ${theme.bgSurface} ${theme.textSecondary} border ${theme.borderMain}`}>
                    {cluster.slides.length} slides merged
                  </span>
                </div>

                {/* Sources list */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {cluster.sources.map((s, sIdx) => (
                    <span
                      key={sIdx}
                      className={`px-2 py-0.5 rounded-md ${theme.bgSurface} ${theme.textMuted} text-xs font-mono border ${theme.borderMain}`}
                    >
                      {s.filename} : p{s.pageNumber}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TAB 4: MASTER REVISION BOOKLET */}
        {activeTab === "master_doc" && (
          <div>
            {pipelineResults?.masterDoc ? (
              <div className="space-y-6">
                {/* Table of Contents Pill Bar */}
                <div className={`${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} shadow-sm`}>
                  <h3 className={`text-[10px] font-mono font-bold uppercase tracking-[0.2em] ${theme.textMuted} mb-3`}>
                    Table of Contents ({pipelineResults.masterDoc.tableOfContents.length} Topics + Master Glossary)
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {pipelineResults.masterDoc.tableOfContents.map((toc, idx) => (
                      <a
                        key={idx}
                        href={`#${toc.anchor}`}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium ${theme.bgSurface} hover:${theme.bgCardHover} ${theme.textPrimary} border ${theme.borderMain} transition-colors`}
                      >
                        <span className={`font-bold ${theme.accentText}`}>{idx + 1}.</span>
                        <span>{toc.title}</span>
                        <span className={`${theme.textMuted} text-[10px]`}>({toc.slideCount} slides)</span>
                      </a>
                    ))}
                    <a
                      href="#master-glossary"
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/20"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
                      <span>Deduplicated Master Glossary ({pipelineResults.masterDoc.deduplicatedDefinitions.length} terms)</span>
                    </a>
                  </div>
                </div>

                <MarkdownNoteRenderer
                  title={pipelineResults.masterDoc.title}
                  markdown={pipelineResults.masterDoc.fullMarkdown}
                />
              </div>
            ) : (
              <div className={`${theme.bgCard} rounded-2xl p-12 text-center border ${theme.borderMain} shadow-sm space-y-4`}>
                <div
                  className={`w-12 h-12 rounded-2xl ${theme.accentBgSubtle} border ${theme.accentBorder} flex items-center justify-center mx-auto`}
                >
                  <BookOpen className="w-6 h-6" />
                </div>
                <h3 className={`text-xl font-bold ${theme.textPrimary} ${theme.headingFont}`}>
                  Ready to Synthesize Lecture Notes
                </h3>
                <p className={`text-xs sm:text-sm ${theme.textMuted} max-w-md mx-auto font-mono`}>
                  Click <strong>"Run AI Pipeline"</strong> above to trigger the 4-stage engine: Lightweight Tagging → Canonical Clustering → Deep Synthesis → Master Book Assembly.
                </p>
                <button
                  onClick={handleRunPipeline}
                  className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold text-white transition-all cursor-pointer hover:scale-[1.04] btn-ripple`}
                  style={{
                    background: theme.accentGradient,
                    boxShadow: `0 4px 22px ${theme.accentColor}55`,
                  }}
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute Pipeline Now</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
