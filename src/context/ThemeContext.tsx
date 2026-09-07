import React, { createContext, useContext, useEffect, useState } from "react";

export type ThemeKey =
  | "clean_light"
  | "oxford"
  | "dark_studio"
  | "royal_platinum"
  | "forest_sage"
  | "sepia_book"
  | "midnight_navy"
  | "neon_aurora"
  | "rose_studio";

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
  // Ambient backdrop colors (driven into CSS variables)
  orbA: string;
  orbB: string;
  orbC: string;
  gridColor: string;
  accentGradient: string;
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
    orbA: "rgba(79, 70, 229, 0.14)",
    orbB: "rgba(168, 85, 247, 0.10)",
    orbC: "rgba(14, 165, 233, 0.10)",
    gridColor: "rgba(100, 116, 139, 0.05)",
    accentGradient: "linear-gradient(135deg, #4F46E5, #8B5CF6, #EC4899)",
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
    orbA: "rgba(140, 45, 25, 0.12)",
    orbB: "rgba(180, 130, 60, 0.10)",
    orbC: "rgba(90, 110, 70, 0.08)",
    gridColor: "rgba(90, 80, 70, 0.05)",
    accentGradient: "linear-gradient(135deg, #8C2D19, #B45309, #A16207)",
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
    orbA: "rgba(99, 102, 241, 0.24)",
    orbB: "rgba(168, 85, 247, 0.20)",
    orbC: "rgba(34, 211, 238, 0.16)",
    gridColor: "rgba(148, 163, 184, 0.07)",
    accentGradient: "linear-gradient(135deg, #6366F1, #A855F7, #F59E0B)",
  },
  royal_platinum: {
    id: "royal_platinum",
    name: "Royal Platinum (Premium)",
    category: "dark",
    accentColor: "#C9A86A",
    bgPreview: "#08090F",
    cardPreview: "#12141E",
    textColor: "#F5F4F0",
    description: "Luxury graphite canvas, champagne-gold accents, refined premium editorial styling",
    badge: "Premium Editorial",
    bgApp: "bg-[#08090F]",
    bgCard: "bg-[#12141E]",
    bgCardHover: "hover:bg-[#191C2A]",
    bgSurface: "bg-[#0C0E16]",
    bgElevated: "bg-[#12141E] shadow-2xl",
    borderMain: "border-[#26293A]",
    borderSubtle: "border-[#1D202F]",
    textPrimary: "text-[#F5F4F0]",
    textSecondary: "text-[#D6D3CB]",
    textMuted: "text-[#9A978C]",
    accentBg: "bg-[#C9A86A] hover:bg-[#B8955A] text-[#0A0B10]",
    accentBgSubtle: "bg-amber-400/10 text-amber-300",
    accentText: "text-amber-300",
    accentBorder: "border-amber-400/25",
    accentShadow: "shadow-[0_0_18px_rgba(201,168,106,0.25)]",
    codeBg: "bg-[#05060B]",
    codeText: "text-amber-200",
    headingFont: "font-sans",
    isDark: true,
    orbA: "rgba(201, 168, 106, 0.16)",
    orbB: "rgba(139, 92, 246, 0.14)",
    orbC: "rgba(56, 189, 248, 0.12)",
    gridColor: "rgba(201, 175, 120, 0.05)",
    accentGradient: "linear-gradient(135deg, #C9A86A, #E8C890, #A78BFA)",
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
    orbA: "rgba(21, 128, 61, 0.14)",
    orbB: "rgba(132, 204, 22, 0.10)",
    orbC: "rgba(14, 116, 144, 0.08)",
    gridColor: "rgba(50, 90, 65, 0.05)",
    accentGradient: "linear-gradient(135deg, #15803D, #65A30D, #0D9488)",
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
    orbA: "rgba(154, 52, 18, 0.14)",
    orbB: "rgba(217, 119, 6, 0.10)",
    orbC: "rgba(120, 53, 15, 0.08)",
    gridColor: "rgba(110, 90, 70, 0.05)",
    accentGradient: "linear-gradient(135deg, #9A3412, #D97706, #92400E)",
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
    orbA: "rgba(56, 189, 248, 0.20)",
    orbB: "rgba(59, 130, 246, 0.16)",
    orbC: "rgba(168, 85, 247, 0.14)",
    gridColor: "rgba(148, 197, 255, 0.06)",
    accentGradient: "linear-gradient(135deg, #38BDF8, #3B82F6, #8B5CF6)",
  },
  neon_aurora: {
    id: "neon_aurora",
    name: "Neon Aurora (Ultraviolet)",
    category: "dark",
    accentColor: "#22D3EE",
    bgPreview: "#060714",
    cardPreview: "#0D1024",
    textColor: "#F4F6FF",
    description: "Deep-space ultraviolet canvas with pulsing neon cyan-magenta auroras",
    badge: "Neon Future",
    bgApp: "bg-[#060714]",
    bgCard: "bg-[#0D1024]",
    bgCardHover: "hover:bg-[#141837]",
    bgSurface: "bg-[#090B1B]",
    bgElevated: "bg-[#0D1024] shadow-xl",
    borderMain: "border-[#232A54]",
    borderSubtle: "border-[#1A1F44]",
    textPrimary: "text-[#F4F6FF]",
    textSecondary: "text-[#C7D2FE]",
    textMuted: "text-[#7C86B8]",
    accentBg: "bg-cyan-500 hover:bg-cyan-400 text-white",
    accentBgSubtle: "bg-cyan-500/10 text-cyan-300",
    accentText: "text-cyan-300",
    accentBorder: "border-cyan-500/30",
    accentShadow: "shadow-[0_0_18px_rgba(34,211,238,0.35)]",
    codeBg: "bg-[#070818]",
    codeText: "text-fuchsia-300",
    headingFont: "font-sans",
    isDark: true,
    orbA: "rgba(34, 211, 238, 0.24)",
    orbB: "rgba(217, 70, 239, 0.20)",
    orbC: "rgba(139, 92, 246, 0.18)",
    gridColor: "rgba(129, 140, 248, 0.07)",
    accentGradient: "linear-gradient(135deg, #22D3EE, #A855F7, #EC4899)",
  },
  rose_studio: {
    id: "rose_studio",
    name: "Rose Studio (Blush Editorial)",
    category: "light",
    accentColor: "#E11D48",
    bgPreview: "#FBF7F8",
    cardPreview: "#FFFFFF",
    textColor: "#1C1417",
    description: "Soft blush porcelain, warm rosewood accents, refined modern editorial clarity",
    badge: "Rose Editorial",
    bgApp: "bg-[#FBF7F8]",
    bgCard: "bg-white",
    bgCardHover: "hover:bg-[#FBF0F2]",
    bgSurface: "bg-[#F5ECEE]",
    bgElevated: "bg-white shadow-sm",
    borderMain: "border-[#EADCE0]",
    borderSubtle: "border-[#F3E7EA]",
    textPrimary: "text-[#1C1417]",
    textSecondary: "text-[#4A3B40]",
    textMuted: "text-[#8F7A82]",
    accentBg: "bg-[#E11D48] hover:bg-[#BE123C] text-white",
    accentBgSubtle: "bg-rose-50 text-rose-700",
    accentText: "text-rose-600",
    accentBorder: "border-rose-200",
    accentShadow: "shadow-[0_2px_10px_rgba(225,29,72,0.15)]",
    codeBg: "bg-[#2D1A24]",
    codeText: "text-rose-100",
    headingFont: "font-sans",
    isDark: false,
    orbA: "rgba(225, 29, 72, 0.10)",
    orbB: "rgba(217, 119, 6, 0.08)",
    orbC: "rgba(79, 70, 229, 0.06)",
    gridColor: "rgba(130, 100, 110, 0.04)",
    accentGradient: "linear-gradient(135deg, #E11D48, #F59E0B, #8B5CF6)",
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
    return "dark_studio"; // Default: cool cyber obsidian look
  });

  const [isThemePickerOpen, setIsThemePickerOpen] = useState<boolean>(false);

  const setThemeKey = (key: ThemeKey) => {
    setThemeKeyState(key);
    localStorage.setItem("studylens_theme", key);
  };

  const theme = THEME_PRESETS[themeKey] || THEME_PRESETS.clean_light;

  useEffect(() => {
    const root = document.documentElement;
    if (theme.isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    // Drive the ambient backdrop CSS variables from the active theme.
    root.style.setProperty("--orb-a", theme.orbA);
    root.style.setProperty("--orb-b", theme.orbB);
    root.style.setProperty("--orb-c", theme.orbC);
    root.style.setProperty("--grid-color", theme.gridColor);
    root.style.setProperty("--accent-grad", theme.accentGradient);
    root.style.setProperty("--accent-color", theme.accentColor);
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
