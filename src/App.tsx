import React, { useEffect, useState } from "react";
import { Header, NavTab } from "./components/Header";
import { PipelineWorkbench } from "./components/PipelineWorkbench";
import { WorkedExampleView } from "./components/WorkedExampleView";
import { PromptInspector } from "./components/PromptInspector";
import { ArchitectureDocs } from "./components/ArchitectureDocs";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
import { QuickThemeBar, ThemeSelectorModal } from "./components/ThemeSelectorModal";

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
    <div className={`min-h-screen ${theme.bgApp} ${theme.textPrimary} flex flex-col font-sans antialiased transition-colors duration-200`}>
      {/* Quick Theme Selector Bar */}
      <QuickThemeBar />

      {/* Top Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasApiKey={hasApiKey}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === "specs" && <ArchitectureDocs />}
        {activeTab === "workbench" && <PipelineWorkbench />}
        {activeTab === "worked_example" && <WorkedExampleView />}
        {activeTab === "prompts" && <PromptInspector />}
      </main>

      {/* Theme Picker Modal */}
      <ThemeSelectorModal />

      {/* Telemetry Footer */}
      <footer className={`border-t ${theme.borderMain} ${theme.bgSurface} py-4 text-xs font-mono ${theme.textMuted}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <span className={`flex items-center gap-1.5 ${theme.textPrimary} font-semibold`}>
              <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
              <span>STUDYLENS AI ENGINE</span>
            </span>
            <span className="hidden md:inline opacity-30">|</span>
            <span className={theme.textMuted}>LATENCY: ~480ms</span>
            <span className="hidden md:inline opacity-30">|</span>
            <span className={theme.textMuted}>CONCURRENCY: 3-4 WORKERS</span>
          </div>

          <div className="flex items-center gap-3 text-[11px]">
            <span
              className={`font-semibold px-2.5 py-0.5 rounded border ${theme.accentBgSubtle} ${theme.accentBorder}`}
            >
              MODEL: gemini-3.7-flash
            </span>
            <span className={theme.textMuted}>ACTIVE THEME: {theme.name}</span>
          </div>
        </div>
      </footer>
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
