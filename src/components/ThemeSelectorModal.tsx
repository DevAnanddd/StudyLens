import React from "react";
import { useTheme, THEME_PRESETS, ThemeKey } from "../context/ThemeContext";
import { Palette, Check, Sparkles, X, Sun, Moon } from "lucide-react";

export const ThemeSelectorModal: React.FC = () => {
  const { themeKey, setThemeKey, isThemePickerOpen, setIsThemePickerOpen, theme } = useTheme();
  const panelRef = React.useRef<HTMLDivElement>(null);
  const restoreFocusRef = React.useRef<HTMLElement | null>(null);

  // Focus trap + Escape-to-close while the modal is open.
  React.useEffect(() => {
    if (!isThemePickerOpen) return;

    restoreFocusRef.current = document.activeElement as HTMLElement | null;
    const panel = panelRef.current;
    if (panel) {
      // Defer so the element is fully mounted before stealing focus.
      window.setTimeout(() => panel.focus(), 0);
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        setIsThemePickerOpen(false);
        restoreFocusRef.current?.focus?.();
        restoreFocusRef.current = null;
        return;
      }
      if (e.key !== "Tab" || !panel) return;

      const focusables = Array.from(
        panel.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => !el.hasAttribute("disabled"));
      if (focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isThemePickerOpen, setIsThemePickerOpen]);

  const handleClose = () => {
    setIsThemePickerOpen(false);
    restoreFocusRef.current?.focus?.();
    restoreFocusRef.current = null;
  };

  if (!isThemePickerOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-label="Select Application Theme"
    >
      <div
        ref={panelRef}
        tabIndex={-1}
        className={`w-full max-w-2xl rounded-2xl border ${theme.borderMain} ${theme.bgCard} ${theme.textPrimary} shadow-2xl overflow-hidden animate-scaleIn outline-none`}
      >
        {/* Modal Header */}
        <div className={`flex items-center justify-between px-6 py-4 border-b ${theme.borderMain} ${theme.bgSurface}`}>
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl ${theme.accentBgSubtle}`}>
              <Palette className="w-5 h-5" />
            </div>
            <div>
              <h3 className={`text-base font-bold ${theme.headingFont}`}>
                Select Application Theme
              </h3>
              <p className={`text-xs ${theme.textMuted}`}>
                Choose your preferred visual aesthetic for StudyLens AI
              </p>
            </div>
          </div>

          <button
            onClick={handleClose}
            aria-label="Close theme picker"
            className={`p-1.5 rounded-lg ${theme.textMuted} hover:${theme.textPrimary} hover:${theme.bgSurface} transition-colors cursor-pointer`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Themes Grid */}
        <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[70vh] overflow-y-auto">
          {(Object.keys(THEME_PRESETS) as ThemeKey[]).map((key) => {
            const preset = THEME_PRESETS[key];
            const isSelected = themeKey === key;

            return (
              <button
                key={key}
                aria-pressed={isSelected}
                aria-label={`Apply ${preset.name} theme`}
                onClick={() => {
                  setThemeKey(key);
                  setIsThemePickerOpen(false);
                }}
                className={`p-4 rounded-xl border text-left transition-all cursor-pointer relative flex flex-col justify-between ${
                  isSelected
                    ? `border-2 shadow-md ring-2 ring-offset-2 ring-indigo-500`
                    : `border ${theme.borderMain} hover:border-indigo-400`
                }`}
                style={{
                  backgroundColor: preset.bgPreview,
                  color: preset.textColor,
                  borderColor: isSelected ? preset.accentColor : undefined,
                }}
              >
                <div>
                  {/* Badge & Mode */}
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded"
                      style={{
                        backgroundColor: preset.accentColor + "20",
                        color: preset.accentColor,
                      }}
                    >
                      {preset.badge}
                    </span>

                    <div className="flex items-center gap-1.5 text-xs opacity-75">
                      {preset.category === "dark" ? (
                        <Moon className="w-3.5 h-3.5" />
                      ) : (
                        <Sun className="w-3.5 h-3.5" />
                      )}
                      <span className="capitalize">{preset.category}</span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <h4 className="font-bold text-sm">{preset.name}</h4>
                  <p className="text-xs mt-1 opacity-75 leading-relaxed">
                    {preset.description}
                  </p>
                </div>

                {/* Color Swatch Preview */}
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-black/10 dark:border-white/10">
                  <div className="flex items-center gap-1.5">
                    <div
                      className="w-4 h-4 rounded-full border border-black/20"
                      style={{ backgroundColor: preset.bgPreview }}
                      title="Canvas"
                    />
                    <div
                      className="w-4 h-4 rounded-full border border-black/20"
                      style={{ backgroundColor: preset.cardPreview }}
                      title="Card"
                    />
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: preset.accentColor }}
                      title="Accent"
                    />
                  </div>

                  {isSelected && (
                    <span
                      className="flex items-center gap-1 text-xs font-bold font-mono"
                      style={{ color: preset.accentColor }}
                    >
                      <Check className="w-3.5 h-3.5" />
                      ACTIVE
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className={`px-6 py-3 border-t ${theme.borderMain} ${theme.bgSurface} flex items-center justify-between text-xs`}>
          <span className={theme.textMuted}>Selection is saved automatically</span>
          <button
            onClick={handleClose}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold ${theme.accentBg} cursor-pointer`}
          >
            Apply & Close
          </button>
        </div>
      </div>
    </div>
  );
};

export const QuickThemeBar: React.FC = () => {
  const { themeKey, setThemeKey, setIsThemePickerOpen, theme } = useTheme();

  return (
    <div className={`border-b ${theme.borderSubtle} ${theme.bgSurface} py-1.5 px-4 text-xs glass-subtle`}>
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-2 overflow-x-auto hide-scrollbar">
        <div className="flex items-center gap-2 shrink-0">
          <Palette className={`w-3.5 h-3.5 ${theme.accentText}`} />
          <span className={`text-[11px] font-semibold font-mono uppercase tracking-wider ${theme.textMuted}`}>
            Theme:
          </span>
        </div>

        {/* Theme Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto hide-scrollbar py-0.5 flex-1 min-w-0 justify-end">
          {(Object.keys(THEME_PRESETS) as ThemeKey[]).map((key) => {
            const preset = THEME_PRESETS[key];
            const isSelected = themeKey === key;
            return (
              <button
                key={key}
                onClick={() => setThemeKey(key)}
                aria-pressed={isSelected}
                aria-label={`Switch to ${preset.name} theme`}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-200 shrink-0 cursor-pointer ${
                  isSelected
                    ? `${theme.accentBg} font-bold shadow-xs scale-105`
                    : `${theme.textSecondary} hover:text-current hover:${theme.bgCard}`
                }`}
              >
                <span
                  className="w-2 h-2 rounded-full border border-black/10"
                  style={{ backgroundColor: preset.accentColor }}
                />
                <span>{preset.name.split(" ")[0]}</span>
              </button>
            );
          })}

          <button
            onClick={() => setIsThemePickerOpen(true)}
            className={`px-2 py-1 rounded-lg text-[11px] font-mono ${theme.textMuted} hover:${theme.textPrimary} hover:${theme.bgCard} transition-colors shrink-0 flex items-center gap-1 cursor-pointer`}
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            <span>More Themes...</span>
          </button>
        </div>
      </div>
    </div>
  );
};
