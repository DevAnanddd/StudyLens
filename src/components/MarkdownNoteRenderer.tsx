import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Download, BookOpen, AlertTriangle, Sparkles } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

interface MarkdownNoteRendererProps {
  markdown: string;
  title?: string;
  className?: string;
}

export const MarkdownNoteRenderer: React.FC<MarkdownNoteRendererProps> = ({
  markdown,
  title,
  className = "",
}) => {
  const [copied, setCopied] = useState(false);
  const { theme } = useTheme();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([markdown], { type: "text/markdown" });
    const objectUrl = URL.createObjectURL(file);
    element.href = objectUrl;
    element.download = `${(title || "StudyLens_Revision_Notes")
      .toLowerCase()
      .replace(/[^\w]+/g, "_")}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    // Clean up the blob URL to prevent memory leaks
    setTimeout(() => URL.revokeObjectURL(objectUrl), 100);
  };

  return (
    <div className={`rounded-2xl border ${theme.borderMain} ${theme.bgCard} shadow-md overflow-hidden card-hover ${className}`}>
      {/* Header bar */}
      <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-4 sm:px-6 py-4 border-b ${theme.borderMain} ${theme.bgSurface} glass-subtle`}>
        <div className="flex items-center gap-3 min-w-0">
          <div className={`w-7 h-7 rounded-lg border ${theme.accentBgSubtle} ${theme.accentBorder} flex items-center justify-center animate-pulseGlowGreen shrink-0`}>
            <BookOpen className="w-3.5 h-3.5" />
          </div>
          <div className="min-w-0">
            <span className={`text-[10px] font-mono uppercase tracking-[0.2em] ${theme.textMuted} font-bold block`}>
              Synthesized Revision Folio
            </span>
            <span className={`text-sm font-semibold ${theme.textPrimary} block truncate`}>
              {title || "Revision Notes"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleCopy}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium border ${theme.borderMain} ${theme.bgCard} hover:scale-105 ${theme.textSecondary} transition-all duration-200 cursor-pointer`}
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span className="text-emerald-500 font-semibold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 opacity-70" />
                <span>Copy Markdown</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownload}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium ${theme.accentBg} ${theme.accentShadow} transition-all duration-200 cursor-pointer hover:scale-105`}
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export .md</span>
          </button>
        </div>
      </div>

      {/* Rendered content */}
      <div className={`p-4 sm:p-6 ${theme.bgSurface}`}>
        <div className={`${theme.bgCard} ${theme.textPrimary} rounded-xl p-6 sm:p-10 shadow-sm border ${theme.borderMain} leading-relaxed max-w-none`}>
          <div className={`flex items-center justify-between border-b ${theme.borderMain} pb-4 mb-6`}>
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${theme.accentBgSubtle} ${theme.accentBorder}`}>
                Exam Revision Output
              </span>
              <span className={`text-[11px] font-mono ${theme.textMuted}`}>
                Standard Markdown
              </span>
            </div>
            <span className={`text-[11px] font-mono ${theme.accentText} font-semibold flex items-center gap-1`}>
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              100% Formula Preserved
            </span>
          </div>

          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => (
                <h1 className={`text-2xl sm:text-3xl font-bold ${theme.headingFont} tracking-tight ${theme.textPrimary} pb-3 border-b ${theme.borderMain} mt-2 mb-6`}>
                  {children}
                </h1>
              ),
              h2: ({ children }) => {
                const text = String(children);
                let accentBorder = `border-l-3 ${theme.accentBorder}`;
                let accentColor = theme.accentText;

                if (text.includes("Exam Revision")) {
                  accentColor = "text-rose-600 dark:text-rose-400";
                  accentBorder = "border-l-3 border-rose-500";
                } else if (text.includes("Definitions")) {
                  accentColor = "text-sky-600 dark:text-cyan-400";
                  accentBorder = "border-l-3 border-sky-500";
                } else if (text.includes("Sources")) {
                  accentColor = "text-emerald-600 dark:text-emerald-400";
                  accentBorder = "border-l-3 border-emerald-500";
                }

                return (
                  <div className="mt-8 mb-4">
                    <h2 className={`text-lg font-bold ${accentBorder} pl-3 tracking-tight ${accentColor} ${theme.headingFont}`}>
                      {children}
                    </h2>
                  </div>
                );
              },
              ul: ({ children }) => (
                <ul className="space-y-2.5 my-3 pl-2 list-none">{children}</ul>
              ),
              li: ({ children }) => {
                const contentStr = String(children);
                const isUnclear = contentStr.includes("⚠️ Unclear OCR");

                if (isUnclear) {
                  return (
                    <li className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-sm font-medium">
                      <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                      <div>{children}</div>
                    </li>
                  );
                }

                return (
                  <li className={`flex items-start gap-2.5 ${theme.textSecondary} text-[15px] leading-relaxed`}>
                    <span
                      className="w-1.5 h-1.5 rounded-full shrink-0 mt-2.5"
                      style={{ backgroundColor: theme.accentColor }}
                    />
                    <div className="flex-1">{children}</div>
                  </li>
                );
              },
              strong: ({ children }) => (
                <strong className={`font-bold ${theme.textPrimary}`}>{children}</strong>
              ),
              code: ({ inline, children }: any) => {
                if (inline) {
                  return (
                    <code className={`px-1.5 py-0.5 rounded ${theme.accentBgSubtle} font-mono text-xs border ${theme.accentBorder} font-semibold`}>
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className={`p-4 rounded-xl ${theme.codeBg} ${theme.codeText} font-mono text-xs overflow-x-auto my-4 border ${theme.borderMain} shadow-inner`}>
                    <code>{children}</code>
                  </pre>
                );
              },
              blockquote: ({ children }) => (
                <blockquote className={`border-l-3 ${theme.accentBorder} pl-4 italic ${theme.textMuted} my-4 ${theme.bgSurface} py-2.5 rounded-r-lg`}>
                  {children}
                </blockquote>
              ),
              hr: () => <hr className={`my-8 ${theme.borderMain}`} />,
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
