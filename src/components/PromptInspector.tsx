import React, { useState } from "react";
import {
  EXACT_SYSTEM_PROMPT,
  EXACT_TAGGING_SYSTEM_PROMPT,
  USER_PROMPT_TAGGING_TEMPLATE,
  SLIDE_ENVELOPE_TAGGING_EXAMPLE,
  USER_PROMPT_SUMMARIZATION_TEMPLATE,
} from "../data/promptsAndSpecs";
import { Copy, Check, Terminal, ShieldAlert, Cpu, Sparkles, Sliders } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export const PromptInspector: React.FC = () => {
  const { theme } = useTheme();
  const [activeSubTab, setActiveSubTab] = useState<
    "summarizer_system" | "tagger_system" | "user_templates" | "configs"
  >("summarizer_system");

  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className={`${theme.bgCard} rounded-2xl p-6 sm:p-8 border ${theme.borderMain} ${theme.bgElevated} pro-card card-spotlight animate-fadeInUp`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-md text-[10px] font-mono font-bold uppercase tracking-wider ${theme.accentBgSubtle} border ${theme.accentBorder} gradient-border mb-3`}>
              <Cpu className="w-3.5 h-3.5" />
              <span>Production Prompt Engineering Layer</span>
            </div>
            <h2 className={`text-2xl sm:text-3xl font-bold tracking-tight ${theme.textPrimary} ${theme.headingFont}`}>
              Gemini <span className="gradient-text-cool">System & User Prompts</span>
            </h2>
            <p className={`text-xs sm:text-sm ${theme.textMuted} mt-1 max-w-2xl font-mono leading-relaxed`}>
              Exact system instructions, user envelopes, structured JSON schemas, and anti-hallucination guardrails designed specifically for noisy OCR lecture slides.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => copyToClipboard(EXACT_SYSTEM_PROMPT, "all_summarizer")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-mono font-bold text-white transition-all duration-200 cursor-pointer hover:scale-[1.03] btn-ripple`}
              style={{
                background: theme.accentGradient,
                boxShadow: `0 4px 22px ${theme.accentColor}55`,
              }}
            >
              {copiedKey === "all_summarizer" ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4 text-white" />}
              <span>Copy System Prompt</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className={`flex flex-wrap gap-2 border-b ${theme.borderMain} pb-3 stagger-children`}>
        <button
          onClick={() => setActiveSubTab("summarizer_system")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer ${
            activeSubTab === "summarizer_system"
              ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
              : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>Topic Summarization System Prompt</span>
        </button>

        <button
          onClick={() => setActiveSubTab("tagger_system")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer ${
            activeSubTab === "tagger_system"
              ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
              : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
          }`}
        >
          <Cpu className="w-4 h-4 text-cyan-500" />
          <span>Lightweight Tagging System & Schema</span>
        </button>

        <button
          onClick={() => setActiveSubTab("user_templates")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer ${
            activeSubTab === "user_templates"
              ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
              : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
          }`}
        >
          <Terminal className="w-4 h-4 text-purple-500" />
          <span>User Message Formats</span>
        </button>

        <button
          onClick={() => setActiveSubTab("configs")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all duration-200 cursor-pointer ${
            activeSubTab === "configs"
              ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
              : `${theme.bgSurface} ${theme.textSecondary} hover:text-current hover:${theme.bgCardHover} border ${theme.borderMain}`
          }`}
        >
          <Sliders className="w-4 h-4 text-emerald-500" />
          <span>Model Configs & Hyperparameters</span>
        </button>
      </div>

      {/* TAB CONTENT: Summarizer System Prompt */}
      {activeSubTab === "summarizer_system" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Code Box */}
            <div className={`lg:col-span-2 ${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} shadow-sm`}>
              <div className={`flex items-center justify-between pb-3 mb-4 border-b ${theme.borderSubtle}`}>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/60 border border-rose-500"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-400/60 border border-amber-500"></div>
                  <div className="w-3 h-3 rounded-full bg-emerald-500/60 border border-emerald-600"></div>
                  <span className={`text-xs font-mono ${theme.textMuted} ml-2 font-medium`}>systemInstruction (Gemini 3.7 Flash)</span>
                </div>
                <button
                  onClick={() => copyToClipboard(EXACT_SYSTEM_PROMPT, "sys_prompt_box")}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium ${theme.bgSurface} hover:${theme.bgCardHover} ${theme.textPrimary} border ${theme.borderMain} transition-colors cursor-pointer`}
                >
                  {copiedKey === "sys_prompt_box" ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-500" />
                      <span className="text-emerald-500 font-semibold">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 opacity-70" />
                      <span>Copy Prompt</span>
                    </>
                  )}
                </button>
              </div>

              <pre className={`font-mono text-xs ${theme.codeText} ${theme.codeBg} leading-relaxed overflow-x-auto whitespace-pre-wrap p-5 rounded-xl border ${theme.borderMain}`}>
                {EXACT_SYSTEM_PROMPT}
              </pre>
            </div>

            {/* Sidebar Guardrails */}
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
                <div className="flex items-center gap-2 text-amber-800 dark:text-amber-400 font-mono font-bold text-xs">
                  <ShieldAlert className="w-4 h-4 text-amber-500" />
                  <span>Rule 1: OCR Typo Healing</span>
                </div>
                <p className="text-xs text-amber-900/90 dark:text-amber-200/80 leading-relaxed font-mono">
                  Corrects character-level OCR swaps (e.g. <code>"1imited"</code> → <code>"limited"</code>) but explicitly forbids introducing new scientific concepts not mentioned in the slides.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-400 font-mono font-bold text-xs">
                  <Sparkles className="w-4 h-4 text-emerald-500" />
                  <span>Rule 2: Mathematical Invariance</span>
                </div>
                <p className="text-xs text-emerald-900/90 dark:text-emerald-200/80 leading-relaxed font-mono">
                  Any math symbols or formulas (e.g. <code>`PA = f(VA)`</code>, <code>`O(log N)`</code>) must be preserved in exact notation with backtick wrappers.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 space-y-2">
                <div className="flex items-center gap-2 text-rose-800 dark:text-rose-400 font-mono font-bold text-xs">
                  <ShieldAlert className="w-4 h-4 text-rose-500" />
                  <span>Rule 3: Unclear Flagging</span>
                </div>
                <p className="text-xs text-rose-900/90 dark:text-rose-200/80 leading-relaxed font-mono">
                  If OCR is too garbled to resolve unambiguously, the system outputs: <code>⚠️ Unclear OCR on [Slide #]</code> rather than guessing.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Tagging System Prompt */}
      {activeSubTab === "tagger_system" && (
        <div className="space-y-6">
          <div className={`${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} shadow-sm`}>
            <div className={`flex items-center justify-between pb-3 mb-4 border-b ${theme.borderSubtle}`}>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-mono ${theme.accentText} font-semibold`}>
                  Stage 1: Lightweight Classifier (Low-Cost Deterministic JSON)
                </span>
              </div>
              <button
                onClick={() => copyToClipboard(EXACT_TAGGING_SYSTEM_PROMPT, "tagger_prompt")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium ${theme.bgSurface} hover:${theme.bgCardHover} ${theme.textPrimary} border ${theme.borderMain} transition-colors cursor-pointer`}
              >
                {copiedKey === "tagger_prompt" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-500" />
                    <span className="text-emerald-500 font-semibold">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 opacity-70" />
                    <span>Copy Prompt</span>
                  </>
                )}
              </button>
            </div>

            <pre className={`font-mono text-xs ${theme.codeText} ${theme.codeBg} leading-relaxed overflow-x-auto whitespace-pre-wrap p-5 rounded-xl border ${theme.borderMain}`}>
              {EXACT_TAGGING_SYSTEM_PROMPT}
            </pre>
          </div>
        </div>
      )}

      {/* TAB CONTENT: User Templates */}
      {activeSubTab === "user_templates" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className={`${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} shadow-sm space-y-3`}>
              <div className={`flex items-center justify-between pb-2 border-b ${theme.borderSubtle}`}>
                <h3 className={`text-xs font-mono font-bold ${theme.accentText} uppercase`}>
                  Stage 1 User Envelope Template
                </h3>
              </div>
              <pre className={`font-mono text-xs ${theme.codeText} ${theme.codeBg} p-4 rounded-xl border ${theme.borderMain} overflow-x-auto whitespace-pre-wrap leading-relaxed`}>
                {USER_PROMPT_TAGGING_TEMPLATE}
              </pre>
            </div>

            <div className={`${theme.bgCard} rounded-2xl p-5 border ${theme.borderMain} shadow-sm space-y-3`}>
              <div className={`flex items-center justify-between pb-2 border-b ${theme.borderSubtle}`}>
                <h3 className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400 uppercase">
                  Stage 3 Cluster Summarizer Envelope
                </h3>
              </div>
              <pre className={`font-mono text-xs ${theme.codeText} ${theme.codeBg} p-4 rounded-xl border ${theme.borderMain} overflow-x-auto whitespace-pre-wrap leading-relaxed`}>
                {USER_PROMPT_SUMMARIZATION_TEMPLATE}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Model Configs */}
      {activeSubTab === "configs" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-4`}>
            <h3 className={`text-base font-bold ${theme.textPrimary} ${theme.headingFont}`}>
              Stage 1 (Lightweight Tagging) Parameters
            </h3>
            <div className={`space-y-2 text-xs font-mono ${theme.textSecondary}`}>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Model:</span>
                <span className={`font-bold ${theme.accentText}`}>gemini-3.7-flash</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Temperature:</span>
                <span className="font-bold">0.1 (Strict Determinism)</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Response MIME:</span>
                <span className="font-bold">application/json</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Concurrency Pool:</span>
                <span className="font-bold">4 concurrent workers</span>
              </div>
            </div>
          </div>

          <div className={`${theme.bgCard} rounded-2xl p-6 border ${theme.borderMain} shadow-sm space-y-4`}>
            <h3 className={`text-base font-bold ${theme.textPrimary} ${theme.headingFont}`}>
              Stage 3 (Deep Summarization) Parameters
            </h3>
            <div className={`space-y-2 text-xs font-mono ${theme.textSecondary}`}>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Model:</span>
                <span className={`font-bold ${theme.accentText}`}>gemini-3.7-flash</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Temperature:</span>
                <span className="font-bold">0.2 (Factually Precise)</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Max Output Tokens:</span>
                <span className="font-bold">3,000 tokens</span>
              </div>
              <div className={`flex justify-between p-2 rounded-lg ${theme.bgSurface}`}>
                <span>Retry Policy:</span>
                <span className="font-bold">Exp Backoff + Full Jitter</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
