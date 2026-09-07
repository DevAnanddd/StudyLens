import React, { useState } from "react";
import {
  WORKED_EXAMPLE_INPUT,
  WORKED_EXAMPLE_TAGGED_OUTPUT,
  WORKED_EXAMPLE_FINAL_MARKDOWN,
} from "../data/promptsAndSpecs";
import { MarkdownNoteRenderer } from "./MarkdownNoteRenderer";
import { Sparkles, AlertCircle, Copy, Check, CheckCircle2 } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export const WorkedExampleView: React.FC = () => {
  const { theme } = useTheme();
  const [activeStep, setActiveStep] = useState<"input" | "tagged" | "final">("final");
  const [copied, setCopied] = useState(false);

  const copyMarkdown = async () => {
    await navigator.clipboard.writeText(WORKED_EXAMPLE_FINAL_MARKDOWN);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className={`${theme.bgCard} rounded-2xl p-6 sm:p-8 border ${theme.borderMain} ${theme.bgElevated} pro-card card-spotlight animate-fadeInUp`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider ${theme.accentBgSubtle} border ${theme.accentBorder} gradient-border mb-3`}>
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Full End-to-End Pipeline Walkthrough</span>
            </div>
            <h2 className={`text-2xl font-bold ${theme.textPrimary} ${theme.headingFont} tracking-tight`}>
              Worked Example: <span className="gradient-text-warm">Noisy OCR → Tagged JSON → Revision Notes</span>
            </h2>
            <p className={`text-xs sm:text-sm ${theme.textMuted} mt-1 max-w-2xl font-mono leading-relaxed`}>
              Demonstrates how OCR character errors (e.g. <code className="text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded-md border border-rose-500/20 font-mono">1imited</code>, <code className="text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded-md border border-rose-500/20 font-mono">iso1ation</code>) are corrected, formulas preserved, and sources tracked through each stage.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyMarkdown}
              className={`flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl text-xs font-mono font-semibold text-white transition-all duration-200 cursor-pointer hover:scale-[1.03] btn-ripple`}
              style={{
                background: theme.accentGradient,
                boxShadow: `0 4px 22px ${theme.accentColor}55`,
              }}
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-300" /> : <Copy className="w-3.5 h-3.5" />}
              <span>Copy Final Markdown</span>
            </button>
          </div>
        </div>

        {/* Step Progress Pills */}
        <div className={`grid grid-cols-3 gap-3 mt-6 pt-6 border-t ${theme.borderSubtle} stagger-children`}>
          <button
            onClick={() => setActiveStep("input")}
            className={`p-3 rounded-xl text-left border transition-all duration-200 cursor-pointer ${
              activeStep === "input"
                ? `${theme.accentBgSubtle} ${theme.accentBorder} ${theme.accentText} font-semibold shadow-xs animate-scaleIn`
                : `${theme.bgSurface} ${theme.borderMain} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover}`
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-amber-500">Stage 1: Input</span>
              <span className={`text-[10px] ${theme.textMuted} font-mono`}>Raw OCR</span>
            </div>
            <div className={`text-xs font-bold ${theme.textPrimary} mt-1`}>Noisy Raw Text</div>
          </button>

          <button
            onClick={() => setActiveStep("tagged")}
            className={`p-3 rounded-xl text-left border transition-all duration-200 cursor-pointer ${
              activeStep === "tagged"
                ? `${theme.accentBgSubtle} ${theme.accentBorder} ${theme.accentText} font-semibold shadow-xs animate-scaleIn`
                : `${theme.bgSurface} ${theme.borderMain} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover}`
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-purple-500">Stage 2: Tagged</span>
              <span className={`text-[10px] ${theme.textMuted} font-mono`}>JSON Schema</span>
            </div>
            <div className={`text-xs font-bold ${theme.textPrimary} mt-1`}>Structured Metadata</div>
          </button>

          <button
            onClick={() => setActiveStep("final")}
            className={`p-3 rounded-xl text-left border transition-all duration-200 cursor-pointer ${
              activeStep === "final"
                ? `${theme.accentBgSubtle} ${theme.accentBorder} ${theme.accentText} font-semibold shadow-xs animate-scaleIn`
                : `${theme.bgSurface} ${theme.borderMain} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover}`
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-500">Stage 3 & 4: Final</span>
              <span className={`text-[10px] ${theme.textMuted} font-mono`}>Study Note</span>
            </div>
            <div className={`text-xs font-bold ${theme.textPrimary} mt-1`}>Exam Revision Folio ✨</div>
          </button>
        </div>
      </div>

      {/* STEP 1: RAW INPUT INSPECTOR */}
      {activeStep === "input" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed font-mono">
              <strong>Notice the input noise:</strong> Mislabeled digits (<code>1imited</code> instead of <code>limited</code>, <code>iso1ation</code> instead of <code>isolation</code>), OCR header artifacts, fragmented bullet points, and mixed consecutive topics.
            </div>
          </div>

          <div className={`${theme.bgCard} rounded-2xl border ${theme.borderMain} p-6 shadow-sm`}>
            <h3 className={`text-sm font-bold ${theme.textPrimary} uppercase tracking-wider font-mono mb-4`}>
              Raw Slide OCR Text Batch (3 Representative Slides)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {WORKED_EXAMPLE_INPUT.map((slide, idx) => (
                <div
                  key={slide.id}
                  className={`${theme.bgSurface} p-4 rounded-xl border ${theme.borderMain} space-y-2`}
                >
                  <div className="flex items-center justify-between text-xs font-mono pb-2 border-b border-black/10 dark:border-white/10">
                    <span className={`font-bold ${theme.accentText}`}>Slide #{idx + 1}</span>
                    <span className={theme.textMuted}>{slide.filename} : p{slide.pageNumber}</span>
                  </div>
                  <pre className={`font-mono text-[11px] ${theme.codeText} ${theme.codeBg} p-3 rounded-lg border ${theme.borderMain} overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-60`}>
                    {slide.rawOcr}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: TAGGED JSON */}
      {activeStep === "tagged" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-start gap-3">
            <CheckCircle2 className="w-4 h-4 text-purple-500 shrink-0 mt-0.5" />
            <div className="text-xs text-purple-800 dark:text-purple-300 leading-relaxed font-mono">
              <strong>Stage 1 Lightweight Tagging Output:</strong> Gemini 3.7 Flash extracts standardized topic names, slide classification, and confidence score at ~150 tokens per slide with deterministic temperature 0.1.
            </div>
          </div>

          <div className={`${theme.bgCard} rounded-2xl border ${theme.borderMain} p-6 shadow-sm`}>
            <div className={`flex items-center justify-between pb-3 mb-4 border-b ${theme.borderSubtle}`}>
              <h3 className={`text-sm font-bold ${theme.textPrimary} uppercase tracking-wider font-mono`}>
                Parsed Structured JSON Response
              </h3>
              <span className={`text-[11px] font-mono ${theme.accentText} font-semibold`}>
                Schema: SlideTaggingResponse
              </span>
            </div>
            <pre className={`font-mono text-xs ${theme.codeText} ${theme.codeBg} p-4 rounded-xl border ${theme.borderMain} overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-[500px]`}>
              {JSON.stringify(WORKED_EXAMPLE_TAGGED_OUTPUT, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* STEP 3 & 4: FINAL REVISION NOTE */}
      {activeStep === "final" && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3">
            <Sparkles className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div className="text-xs text-emerald-800 dark:text-emerald-300 leading-relaxed font-mono">
              <strong>Final Master Output:</strong> Note how OCR errors were corrected, mathematical formulas <code className="bg-emerald-500/20 px-1 py-0.5 rounded">E = mc^2</code> and <code className="bg-emerald-500/20 px-1 py-0.5 rounded">PA = f(VA)</code> were preserved, definitions were extracted, and slide page citations were retained.
            </div>
          </div>

          <MarkdownNoteRenderer
            title="Lecture 4 — Virtual Memory Architecture"
            markdown={WORKED_EXAMPLE_FINAL_MARKDOWN}
          />
        </div>
      )}
    </div>
  );
};
