import React, { useEffect, useState } from "react";
import { Header, NavTab } from "./components/Header";
import { PipelineWorkbench } from "./components/PipelineWorkbench";
import { WorkedExampleView } from "./components/WorkedExampleView";
import { PromptInspector } from "./components/PromptInspector";
import { ArchitectureDocs } from "./components/ArchitectureDocs";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import { QuickThemeBar, ThemeSelectorModal } from "./components/ThemeSelectorModal";
import { AmbientBackground } from "./components/AmbientBackground";
import { Zap, Library, Timer, Target } from "lucide-react";

function MainApp() {
  const [activeTab, setActiveTab] = useState<NavTab>("workbench");
  const [hasApiKey, setHasApiKey] = useState<boolean>(false);
  const { theme } = useTheme();

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.hasApiKey) {
          setHasApiKey(true);
        }
      })
      .catch(() => {
        // Backend health check quiet fallback
      });
  }, []);

  return (
    <div className={`relative min-h-screen ${theme.bgApp} ${theme.textPrimary} font-sans antialiased transition-colors duration-300 animate-fadeIn`}>
      {/* Ambient animated backdrop — aurora mesh, orbs, grid, particles, cursor glow */}
      <AmbientBackground />

      {/* Top energy data-flow line */}
      <div
        className="data-flow-track"
        style={{ "--accent-grad": theme.accentGradient } as React.CSSProperties}
        aria-hidden="true"
      ></div>

      {/* Foreground content */}
      <div className="relative z-10 flex flex-col min-h-screen">

      {/* Quick Theme Selector Bar */}
      <div className="animate-fadeInDown">
        <QuickThemeBar />
      </div>

      {/* Top Navigation */}
      <div className="animate-fadeInDown" style={{ animationDelay: '0.1s' }}>
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          hasApiKey={hasApiKey}
        />
      </div>

      {/* Professional Hero / Stats Strip */}
      <div className="animate-fadeInUp" style={{ animationDelay: '0.12s' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-5">
          <div className={`${theme.bgCard} rounded-2xl border ${theme.borderMain} shadow-md bg-clip-padding pro-card`}>
            <div className="grid grid-cols-2 md:grid-cols-4">
              {[
                { icon: <Zap className="w-4 h-4" />, label: "PIPELINE STAGES", value: "4-Stage AI", color: "text-amber-500" },
                { icon: <Library className="w-4 h-4" />, label: "OCR SLIDES", value: "50–200 / batch", color: "text-sky-500" },
                { icon: <Timer className="w-4 h-4" />, label: "AVG LATENCY", value: "~480ms", color: "text-emerald-500" },
                { icon: <Target className="w-4 h-4" />, label: "ACCURACY", value: "98.2%", color: "text-rose-500" },
              ].map((stat, i) => (
                <div
                  key={i}
                  className={`stat-chip px-4 py-3 flex items-center gap-3 ${theme.borderSubtle} ${
                    i % 2 === 0 ? "md:border-r" : "md:border-l"
                  } ${i < 2 ? "border-b md:border-b-0" : ""}`}
                >
                  <span className={`${stat.color} shrink-0`} style={{ filter: `drop-shadow(0 0 6px ${theme.accentColor}55)` }}>
                    {stat.icon}
                  </span>
                  <div className="min-w-0">
                    <div className={`text-[10px] font-mono uppercase tracking-wider ${theme.textMuted} font-semibold truncate`}>
                      {stat.label}
                    </div>
                    <div className={`text-sm font-bold ${theme.textPrimary} truncate`}>
                      {stat.value}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Divider */}
          <div className="gradient-divider mt-5" />
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="animate-fadeInUp" style={{ animationDelay: '0.15s' }}>
          {activeTab === "specs" && <ArchitectureDocs />}
          {activeTab === "workbench" && <PipelineWorkbench />}
          {activeTab === "worked_example" && <WorkedExampleView />}
          {activeTab === "prompts" && <PromptInspector />}
        </div>
      </main>

      {/* Theme Picker Modal */}
      <ThemeSelectorModal />

      {/* Enhanced Footer */}
      <footer className={`border-t ${theme.borderMain} ${theme.bgSurface} py-5 text-xs font-mono ${theme.textMuted} animate-fadeIn`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <span className={`flex items-center gap-2 ${theme.textPrimary} font-semibold`}>
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
              </span>
              <span>STUDYLENS AI ENGINE</span>
            </span>
            <span className="hidden md:inline opacity-20">|</span>
            <span className={`${theme.textMuted} hidden md:inline`}>LATENCY: ~480ms</span>
            <span className="hidden md:inline opacity-20">|</span>
            <span className={`${theme.textMuted} hidden md:inline`}>CONCURRENCY: 3-4 WORKERS</span>
          </div>

          <div className="flex items-center gap-3 text-[11px]">
            <span
              className={`font-semibold px-2.5 py-0.5 rounded border ${theme.accentBgSubtle} ${theme.accentBorder} animate-borderGlow`}
            >
              MODEL: gemini-3.7-flash
            </span>
            <span className={`${theme.textMuted} opacity-60 hidden sm:inline`}>ACTIVE THEME: {theme.name}</span>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-3 mt-3">
          <div className="gradient-divider" />
        </div>
      </footer>
        </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <MainApp />
    </ThemeProvider>
  );
}
