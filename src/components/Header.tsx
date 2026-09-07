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
    <header className={`sticky top-0 z-40 border-b ${theme.borderMain} glass-subtle transition-all duration-300`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Name */}
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-white transition-transform duration-300 hover:scale-110 hover:rotate-6 cursor-pointer relative overflow-hidden shadow-lg glyph-ring"
              style={{
                background: theme.accentGradient,
                boxShadow: `0 6px 26px ${theme.accentColor}50`,
              }}
            >
              <span
                className="absolute inset-0 opacity-25 animate-spinSlow"
                style={{
                  background:
                    "linear-gradient(115deg, transparent 40%, rgba(255,255,255,0.7) 50%, transparent 60%)",
                }}
              />
              <Zap className="w-5 h-5 relative z-10 drop-shadow-[0_0_6px_rgba(255,255,255,0.8)]" />
              <span
                className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-white animate-pulse"
                style={{ boxShadow: `0 0 10px ${theme.accentColor}` }}
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className={`font-bold text-lg tracking-tight ${theme.textPrimary} ${theme.headingFont} title-shimmer`}>
                  StudyLens{" "}
                  <span
                    className="font-extrabold"
                    style={{
                      background: theme.accentGradient,
                      WebkitBackgroundClip: "text",
                      backgroundClip: "text",
                      color: "transparent",
                      textShadow: `0 0 22px ${theme.accentColor}40`,
                    }}
                  >
                    AI
                  </span>
                </h1>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 font-semibold rounded-md border ${theme.accentBgSubtle} ${theme.accentBorder} uppercase tracking-wider animate-float`}
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
          <nav className={`flex items-center gap-1 ${theme.bgSurface} p-1 rounded-2xl border ${theme.borderMain} glass-subtle`}>
            {[
              { key: "workbench" as const, icon: <Zap className="w-3.5 h-3.5" />, label: "Interactive Pipeline", iconColor: "" },
              { key: "worked_example" as const, icon: <Sparkles className="w-3.5 h-3.5 text-amber-500" />, label: "Worked Example", iconColor: "" },
              { key: "prompts" as const, icon: <FileCode className="w-3.5 h-3.5 text-purple-500" />, label: "Prompt Inspector", iconColor: "" },
              { key: "specs" as const, icon: <Cpu className="w-3.5 h-3.5 text-emerald-500" />, label: "Architecture & Specs", iconColor: "" },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer ${
                  activeTab === tab.key
                    ? `${theme.accentBg} ${theme.accentShadow} scale-[1.02]`
                    : `${theme.textSecondary} hover:text-current hover:${theme.bgCard}`
                }`}
              >
                {tab.icon}
                <span className="hidden lg:inline">{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* Theme Switcher Button & Model Status */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsThemePickerOpen(true)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium ${theme.borderMain} ${theme.bgSurface} ${theme.textPrimary} hover:scale-105 transition-all duration-200 cursor-pointer`}
              title="Change visual theme"
            >
              <Palette className="w-3.5 h-3.5" style={{ color: theme.accentColor }} />
              <span className="hidden sm:inline font-mono">Theme</span>
            </button>

            <div className={`hidden md:flex h-8 ${theme.bgSurface} border ${theme.borderMain} rounded-xl items-center px-3 text-[11px] font-mono ${theme.textMuted}`}>
              {hasApiKey ? (
                <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 font-semibold">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
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
