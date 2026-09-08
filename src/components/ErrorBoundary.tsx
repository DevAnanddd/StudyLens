import React from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

/**
 * Prevents full-app blank screens when an unhandled error is thrown.
 * Renders a self-contained recovery card with a "Reload app" action.
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error: unknown): ErrorBoundaryState {
    return {
      hasError: true,
      message: error instanceof Error ? error.message : "An unexpected error occurred.",
    };
  }

  componentDidCatch(error: unknown, errorInfo: React.ErrorInfo): void {
    console.error("[StudyLens] Unhandled error caught by boundary:", error, errorInfo);
  }

  private resetApp = () => {
    // Clear persisted UI state that may be corrupt, then reload.
    try {
      localStorage.removeItem("studylens_active_tab");
      localStorage.removeItem("studylens.workbench");
    } catch {
      // Ignore storage failures in environments where localStorage is unavailable.
    }
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        role="alert"
        className="relative min-h-screen w-full flex items-center justify-center p-6 font-sans antialiased"
        style={{ background: "linear-gradient(135deg, #0B0C14, #141625)" }}
      >
        <div className="w-full max-w-lg rounded-2xl border border-[#262B3E] bg-[#12141F] p-8 text-center shadow-2xl animate-scaleIn">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mb-5">
            <AlertTriangle className="w-7 h-7 text-rose-400" />
          </div>

          <h1 className="text-xl font-bold text-white tracking-tight">
            Something went wrong
          </h1>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            StudyLens hit an unexpected error. Your saved work is untouched — you can
            safely reload to continue.
          </p>

          <div className="mt-4 rounded-lg bg-slate-900/80 border border-slate-800 px-4 py-3 text-left">
            <code className="text-xs font-mono text-slate-400 break-words">
              {this.state.message || "Unknown render error"}
            </code>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
            <button
              onClick={this.resetApp}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold text-white transition-all duration-200 cursor-pointer hover:scale-[1.04]"
              style={{
                background: "linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899)",
                boxShadow: "0 4px 22px rgba(99, 102, 241, 0.35)",
              }}
            >
              <RotateCcw className="w-4 h-4" />
              Reload App
            </button>
          </div>
        </div>
      </div>
    );
  }
}