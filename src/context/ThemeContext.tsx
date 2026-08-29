import React, { createContext, useContext, useEffect, useState } from "react";

export type ThemeKey =
  | "clean_light"
  | "oxford"
  | "dark_studio"
  | "forest_sage"
  | "sepia_book"
  | "midnight_navy";

export interface ThemeConfig {
  id: ThemeKey;
  name: string;
  category: "light" | "dark";
  accentColor: string;
  bgPreview: string;
  cardPreview: string;
  textColor: string;
  description: string;
  badge: string;
  // CSS Classes for dynamic binding
  bgApp: string;
  bgCard: string;
  bgCardHover: string;
  bgSurface: string;
  bgElevated: string;
  borderMain: string;
  borderSubtle: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  accentBg: string;
  accentBgSubtle: string;
  accentText: string;
  accentBorder: string;
  accentShadow: string;
  codeBg: string;
  codeText: string;
  headingFont: string;
  isDark: boolean;
}

export const THEME_PRESETS: Record<ThemeKey, ThemeConfig> = {
  clean_light: {
    id: "clean_light",
    name: "Clean Light (Modern)",
    category: "light",
    accentColor: "#4F46E5",
    bgPreview: "#F8FAFC",
    cardPreview: "#FFFFFF",
    textColor: "#0F172A",
    description: "Crisp white canvas, zinc borders, and modern sapphire indigo accents",
    badge: "Clean Slate",
    bgApp: "bg-[#F8FAFC]",
    bgCard: "bg-white",
    bgCardHover: "hover:bg-slate-50",
    bgSurface: "bg-[#F1F5F9]",
    bgElevated: "bg-white shadow-sm",
    borderMain: "border-[#E2E8F0]",
    borderSubtle: "border-[#F1F5F9]",
    textPrimary: "text-[#0F172A]",
    textSecondary: "text-[#475569]",
    textMuted: "text-[#94A3B8]",
    accentBg: "bg-indigo-600 hover:bg-indigo-700 text-white",
    accentBgSubtle: "bg-indigo-50 text-indigo-700",
    accentText: "text-indigo-600",
    accentBorder: "border-indigo-200",
    accentShadow: "shadow-[0_2px_10px_rgba(79,70,229,0.15)]",
    codeBg: "bg-slate-900",
    codeText: "text-slate-100",
    headingFont: "font-sans",
    isDark: false,
  },
  oxford: {
    id: "oxford",
    name: "Oxford Academic (Parchment)",
    category: "light",
    accentColor: "#8C2D19",
    bgPreview: "#F8F7F4",
    cardPreview: "#FDFCF9",
    textColor: "#1A1A1E",
    description: "Warm porcelain canvas, editorial serif headings, and rich terracotta accents",
    badge: "Academic Editorial",
    bgApp: "bg-[#F8F7F4]",
    bgCard: "bg-[#FDFCF9]",
    bgCardHover: "hover:bg-[#F4F1EA]",
    bgSurface: "bg-[#EFECE4]",
    bgElevated: "bg-[#FDFCF9] shadow-xs",
    borderMain: "border-[#E2DFD6]",
    borderSubtle: "border-[#EFECE4]",
    textPrimary: "text-[#1A1A1E]",
    textSecondary: "text-[#4A4740]",
    textMuted: "text-[#716E66]",
    accentBg: "bg-[#8C2D19] hover:bg-[#722312] text-white",
    accentBgSubtle: "bg-[#F4EBE6] text-[#8C2D19]",
    accentText: "text-[#8C2D19]",
    accentBorder: "border-[#E7C6BC]",
    accentShadow: "shadow-[0_2px_10px_rgba(140,45,25,0.12)]",
    codeBg: "bg-[#1C1C21]",
    codeText: "text-[#F5F2EB]",
    headingFont: "font-serif",
    isDark: false,
  },
  dark_studio: {
    id: "dark_studio",
    name: "Dark Studio (Obsidian)",
    category: "dark",
    accentColor: "#6366F1",
    bgPreview: "#0B0D13",
    cardPreview: "#131622",
    textColor: "#F3F4F6",
    description: "Deep obsidian canvas, midnight cards, and glowing electric indigo accents",
    badge: "Cyber Studio",
    bgApp: "bg-[#0B0D13]",
    bgCard: "bg-[#131622]",
    bgCardHover: "hover:bg-[#1A1F30]",
    bgSurface: "bg-[#0E1017]",
    bgElevated: "bg-[#131622] shadow-xl",
    borderMain: "border-[#232738]",
    borderSubtle: "border-[#1E2235]",
    textPrimary: "text-[#F3F4F6]",
    textSecondary: "text-[#D1D5DB]",
    textMuted: "text-[#9CA3AF]",
    accentBg: "bg-indigo-600 hover:bg-indigo-500 text-white",
    accentBgSubtle: "bg-indigo-500/10 text-indigo-400",
    accentText: "text-indigo-400",
    accentBorder: "border-indigo-500/30",
    accentShadow: "shadow-[0_0_15px_rgba(99,102,241,0.3)]",
    codeBg: "bg-[#090A0F]",
    codeText: "text-emerald-400",
    headingFont: "font-sans",
    isDark: true,
  },
  forest_sage: {
    id: "forest_sage",
    name: "Forest & Sage (Botanical)",
    category: "light",
    accentColor: "#15803D",
    bgPreview: "#F2F6F3",
    cardPreview: "#FFFFFF",
    textColor: "#14281D",
    description: "Earthy sage background, botanical forest green accents, and natural contrast",
    badge: "Natural Scholar",
    bgApp: "bg-[#F2F6F3]",
    bgCard: "bg-white",
    bgCardHover: "hover:bg-[#E8F0EA]",
    bgSurface: "bg-[#E2EBE5]",
    bgElevated: "bg-white shadow-sm",
    borderMain: "border-[#CCDCD2]",
    borderSubtle: "border-[#E2EBE5]",
    textPrimary: "text-[#14281D]",
    textSecondary: "text-[#2D4A3A]",
    textMuted: "text-[#5C786A]",
    accentBg: "bg-[#15803D] hover:bg-[#166534] text-white",
    accentBgSubtle: "bg-emerald-50 text-emerald-800",
    accentText: "text-emerald-700",
    accentBorder: "border-emerald-200",
    accentShadow: "shadow-[0_2px_10px_rgba(21,128,61,0.15)]",
    codeBg: "bg-[#13241B]",
    codeText: "text-emerald-300",
    headingFont: "font-sans",
    isDark: false,
  },
  sepia_book: {
    id: "sepia_book",
    name: "Warm Sepia (Vintage)",
    category: "light",
    accentColor: "#9A3412",
    bgPreview: "#FBF6EE",
    cardPreview: "#FFFDF9",
    textColor: "#291E16",
    description: "Cozy sepia study room palette, espresso brown accents, and gentle warm contrast",
    badge: "Vintage Library",
    bgApp: "bg-[#FBF6EE]",
    bgCard: "bg-[#FFFDF9]",
    bgCardHover: "hover:bg-[#F5ECE0]",
    bgSurface: "bg-[#EFE5D5]",
    bgElevated: "bg-[#FFFDF9] shadow-xs",
    borderMain: "border-[#DFD2BF]",
    borderSubtle: "border-[#EFE5D5]",
    textPrimary: "text-[#291E16]",
    textSecondary: "text-[#57483B]",
    textMuted: "text-[#7D6B5A]",
    accentBg: "bg-[#9A3412] hover:bg-[#7C2D12] text-white",
    accentBgSubtle: "bg-amber-50 text-amber-900",
    accentText: "text-amber-800",
    accentBorder: "border-amber-200",
    accentShadow: "shadow-[0_2px_10px_rgba(154,52,18,0.15)]",
    codeBg: "bg-[#251A14]",
    codeText: "text-[#FBE8D6]",
    headingFont: "font-serif",
    isDark: false,
  },
  midnight_navy: {
    id: "midnight_navy",
    name: "Midnight Navy (Deep Slate)",
    category: "dark",
    accentColor: "#38BDF8",
    bgPreview: "#0B1120",
    cardPreview: "#131D31",
    textColor: "#F8FAFC",
    description: "Deep oceanic navy canvas, slate surfaces, and neon cyan accents",
    badge: "Navy Slate",
    bgApp: "bg-[#0B1120]",
    bgCard: "bg-[#131D31]",
    bgCardHover: "hover:bg-[#1A2742]",
    bgSurface: "bg-[#080D1A]",
    bgElevated: "bg-[#131D31] shadow-xl",
    borderMain: "border-[#202E4C]",
    borderSubtle: "border-[#19243C]",
    textPrimary: "text-[#F8FAFC]",
    textSecondary: "text-[#CBD5E1]",
    textMuted: "text-[#64748B]",
    accentBg: "bg-sky-600 hover:bg-sky-500 text-white",
    accentBgSubtle: "bg-sky-500/10 text-sky-400",
    accentText: "text-sky-400",
    accentBorder: "border-sky-500/30",
    accentShadow: "shadow-[0_0_15px_rgba(56,189,248,0.25)]",
    codeBg: "bg-[#060913]",
    codeText: "text-sky-300",
    headingFont: "font-sans",
    isDark: true,
  },
};

interface ThemeContextValue {
  themeKey: ThemeKey;
  theme: ThemeConfig;
  setThemeKey: (key: ThemeKey) => void;
  isThemePickerOpen: boolean;
  setIsThemePickerOpen: (open: boolean) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [themeKey, setThemeKeyState] = useState<ThemeKey>(() => {
    const saved = localStorage.getItem("studylens_theme");
    if (saved && saved in THEME_PRESETS) {
      return saved as ThemeKey;
    }
    return "clean_light"; // Default clean modern
  });

  const [isThemePickerOpen, setIsThemePickerOpen] = useState<boolean>(false);

  const setThemeKey = (key: ThemeKey) => {
    setThemeKeyState(key);
    localStorage.setItem("studylens_theme", key);
  };

  const theme = THEME_PRESETS[themeKey] || THEME_PRESETS.clean_light;

  useEffect(() => {
    if (theme.isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  return (
    <ThemeContext.Provider
      value={{
        themeKey,
        theme,
        setThemeKey,
        isThemePickerOpen,
        setIsThemePickerOpen,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextValue => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
