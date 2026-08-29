import React from "react";
import { Sparkles, Cpu, Zap, FileCode, CheckCircle2, Palette } from "lucide-react";
import { useTheme } from "../context/ThemeContext";

export type NavTab = "workbench" | "specs" | "worked_example" | "prompts";

interface HeaderProps {
  activeTab: NavTab;
  setActiveTab: (tab: NavTab) => void;
  hasApiKey: boolean;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, hasApiKey }) => {
  const { theme, setIsThemePickerOpen } = useTheme();

  return (
    <header className={`sticky top-0 z-40 border-b ${theme.borderMain} ${theme.bgCard}/95 backdrop-blur-md transition-colors`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3">
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white text-sm ${theme.accentShadow}`}
              style={{ backgroundColor: theme.accentColor }}
            >
              ⚡
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className={`font-bold text-lg tracking-tight ${theme.textPrimary} ${theme.headingFont}`}>
                  StudyLens <span style={{ color: theme.accentColor }}>AI</span>
                </h1>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 font-semibold rounded border ${theme.accentBgSubtle} ${theme.accentBorder} uppercase tracking-wider`}
                >
                  v3.7 Flash
                </span>
              </div>
              <p className={`text-[11px] ${theme.textMuted} hidden sm:block font-mono`}>
                Noisy OCR Slides → Synthesized Revision Notes
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className={`flex items-center gap-1 ${theme.bgSurface} p-1 rounded-xl border ${theme.borderMain}`}>
            <button
              onClick={() => setActiveTab("workbench")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "workbench"
                  ? `${theme.accentBg} ${theme.accentShadow}`
                  : `${theme.textSecondary} hover:${theme.textPrimary} hover:${theme.bgCard}`
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Interactive Pipeline</span>
            </button>

            <button
              onClick={() => setActiveTab("worked_example")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "worked_example"
                  ? `${theme.accentBg} ${theme.accentShadow}`
                  : `${theme.textSecondary} hover:${theme.textPrimary} hover:${theme.bgCard}`
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Worked Example</span>
            </button>

            <button
              onClick={() => setActiveTab("prompts")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "prompts"
                  ? `${theme.accentBg} ${theme.accentShadow}`
                  : `${theme.textSecondary} hover:${theme.textPrimary} hover:${theme.bgCard}`
              }`}
            >
              <FileCode className="w-3.5 h-3.5 text-purple-500" />
              <span>Prompt Inspector</span>
            </button>

            <button
              onClick={() => setActiveTab("specs")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "specs"
                  ? `${theme.accentBg} ${theme.accentShadow}`
                  : `${theme.textSecondary} hover:${theme.textPrimary} hover:${theme.bgCard}`
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-emerald-500" />
              <span>Architecture & Specs</span>
            </button>
          </nav>

          {/* Theme Switcher Button & Model Status */}
          <div className="flex items-center gap-2.5">
            {/* Theme Selector Button */}
            <button
              onClick={() => setIsThemePickerOpen(true)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium ${theme.borderMain} ${theme.bgSurface} ${theme.textPrimary} hover:${theme.bgCard} transition-all cursor-pointer`}
              title="Change visual theme"
            >
              <Palette className="w-3.5 h-3.5" style={{ color: theme.accentColor }} />
              <span className="hidden sm:inline font-mono">Theme</span>
            </button>

            <div className={`hidden md:flex h-8 ${theme.bgSurface} border ${theme.borderMain} rounded-lg items-center px-3 text-[11px] font-mono ${theme.textMuted}`}>
              {hasApiKey ? (
                <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  LIVE GEMINI API
                </span>
              ) : (
                <span>ENGINE: DETERMINISTIC</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
