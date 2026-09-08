import React, { useEffect, useMemo, useRef, useState } from "react";
import { useTheme } from "../context/ThemeContext";

/**
 * Full-viewport animated ambient backdrop:
 * aurora mesh + floating orbs + perspective grid + film noise +
 * scanlines + floating particles + cursor-following glow + ripple handling.
 */
export const AmbientBackground: React.FC = () => {
  const { theme } = useTheme();
  const glowRef = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);

  // Deterministic particle field (client-only render, no SSR concern).
  // Fewer particles on mobile/touch devices to keep scrolling smooth.
  const particles = useMemo(() => {
    const isMobile =
      typeof window !== "undefined" &&
      window.matchMedia("(max-width: 768px), (pointer: coarse)").matches;
    const count = isMobile ? 10 : 28;
    return Array.from({ length: count }).map((_, i) => ({
      id: i,
      left: (i * 37 + 11) % 100,
      top: (i * 53 + 7) % 100,
      delay: ((i * 1.7) % 6).toFixed(2),
      dur: (4 + ((i * 911) % 5)).toFixed(2),
      size: 2 + ((i * 7) % 3),
    }));
  }, []);

  // Cursor-following glow + card spotlight position tracking.
  // Only attached for fine-pointer (mouse) devices — touch screens skip it.
  useEffect(() => {
    const isTouch = window.matchMedia("(pointer: coarse)").matches;
    if (isTouch) return;
    const el = glowRef.current;
    if (!el) return;
    const onMove = (e: PointerEvent) => {
      el.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0) translate3d(-50%, -50%, 0)`;
      const card = (e.target as HTMLElement | null)?.closest?.(
        ".card-spotlight"
      ) as HTMLElement | null;
      if (card) {
        const rect = card.getBoundingClientRect();
        card.style.setProperty("--mx", `${e.clientX - rect.left}px`);
        card.style.setProperty("--my", `${e.clientY - rect.top}px`);
      }
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  // Button ripple origin tracking for `.btn-ripple` elements.
  useEffect(() => {
    const onPointerDown = (e: PointerEvent) => {
      const btn = (e.target as HTMLElement | null)?.closest?.(
        ".btn-ripple"
      ) as HTMLElement | null;
      if (!btn) return;
      const rect = btn.getBoundingClientRect();
      btn.style.setProperty("--rx", `${e.clientX - rect.left}px`);
      btn.style.setProperty("--ry", `${e.clientY - rect.top}px`);
    };
    window.addEventListener("pointerdown", onPointerDown);
    return () => window.removeEventListener("pointerdown", onPointerDown);
  }, []);

  useEffect(() => {
    setReady(true);
  }, []);

  return (
    <div
      aria-hidden="true"
      className="mesh-bg animate-fadeIn"
      style={
        {
          "--orb-a": theme.orbA,
          "--orb-b": theme.orbB,
          "--orb-c": theme.orbC,
          "--grid-color": theme.gridColor,
          "--accent-grad": theme.accentGradient,
        } as React.CSSProperties
      }
    >
      {/* Aurora orbs */}
      <div
        className="orb w-[42vw] h-[42vw] -top-[12vw] -left-[8vw]"
        style={{ color: theme.orbA, animationDuration: "16s" }}
      />
      <div
        className="orb w-[34vw] h-[34vw] top-[6%] -right-[6%]"
        style={{ color: theme.orbB, animationDuration: "13s", animationDelay: "-4s" }}
      />
      <div
        className="orb w-[38vw] h-[38vw] -bottom-[14%] left-[18%]"
        style={{ color: theme.orbC, animationDuration: "19s", animationDelay: "-8s" }}
      />

      {/* Grid + noise + scanlines */}
      <div className="bg-grid" />
      <div className="bg-noise" />
      <div className="scanlines" />

      {/* Neural constellation / network graphic overlay */}
      <div className="neural-network">
        <svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" fill="none">
          <g style={{ color: theme.accentColor }}>
            <path
              className="nn-line"
              d="M120 180 L300 120 L520 200 L420 340 L560 420 M300 120 L480 90 M420 340 L240 380 M520 200 L720 260 L900 180 L1080 260 M720 260 L760 420 L1040 460 M1040 120 L1260 180 L1420 240 L1320 320 M1040 460 L1180 560 L1320 320 M120 640 L260 560 L420 620 L560 540 L760 640 M560 760 L760 640 L720 460 M1040 640 L1180 560 L1240 720 L1420 680 M140 800 L320 840 L500 780 L680 840 L840 760 L1040 840 M680 840 L760 940 M840 760 L980 680 L1180 720 L1240 860 M1240 860 L1420 900"
              stroke={theme.accentColor}
              strokeWidth="0.8"
              opacity="0.22"
            />
            <circle className="nn-node" cx="120" cy="180" r="3.5" fill={theme.accentColor} />
            <circle className="nn-node" cx="300" cy="120" r="4" fill={theme.accentColor} style={{ animationDelay: "0.6s" }} />
            <circle className="nn-node" cx="520" cy="200" r="3.5" fill={theme.accentColor} style={{ animationDelay: "1.2s" }} />
            <circle className="nn-node" cx="420" cy="340" r="4.5" fill={theme.accentColor} style={{ animationDelay: "1.8s" }} />
            <circle className="nn-node" cx="560" cy="420" r="3" fill={theme.accentColor} style={{ animationDelay: "2.4s" }} />
            <circle className="nn-node" cx="480" cy="90" r="3" fill={theme.accentColor} style={{ animationDelay: "0.3s" }} />
            <circle className="nn-node" cx="240" cy="380" r="3" fill={theme.accentColor} style={{ animationDelay: "0.9s" }} />
            <circle className="nn-node" cx="720" cy="260" r="4" fill={theme.accentColor} style={{ animationDelay: "1.5s" }} />
            <circle className="nn-node" cx="900" cy="180" r="3.5" fill={theme.accentColor} style={{ animationDelay: "2.1s" }} />
            <circle className="nn-node" cx="1080" cy="260" r="4.5" fill={theme.accentColor} style={{ animationDelay: "2.7s" }} />
            <circle className="nn-node" cx="760" cy="420" r="3.5" fill={theme.accentColor} style={{ animationDelay: "0.4s" }} />
            <circle className="nn-node" cx="1040" cy="460" r="4" fill={theme.accentColor} style={{ animationDelay: "1s" }} />
            <circle className="nn-node" cx="1040" cy="120" r="3" fill={theme.accentColor} style={{ animationDelay: "1.6s" }} />
            <circle className="nn-node" cx="1260" cy="180" r="4" fill={theme.accentColor} style={{ animationDelay: "2.2s" }} />
            <circle className="nn-node" cx="1320" cy="320" r="3.5" fill={theme.accentColor} style={{ animationDelay: "2.8s" }} />
            <circle className="nn-node" cx="1420" cy="240" r="3" fill={theme.accentColor} style={{ animationDelay: "0.5s" }} />
            <circle className="nn-node" cx="340" cy="40" r="3" fill={theme.accentColor} style={{ animationDelay: "1.1s" }} />
            <circle className="nn-node" cx="1180" cy="560" r="4.5" fill={theme.accentColor} style={{ animationDelay: "1.7s" }} />
            <circle className="nn-node" cx="1240" cy="720" r="3.5" fill={theme.accentColor} style={{ animationDelay: "2.3s" }} />
            <circle className="nn-node" cx="1420" cy="680" r="3" fill={theme.accentColor} style={{ animationDelay: "2.9s" }} />
            <circle className="nn-node" cx="140" cy="800" r="3.5" fill={theme.accentColor} style={{ animationDelay: "0.7s" }} />
            <circle className="nn-node" cx="320" cy="840" r="4" fill={theme.accentColor} style={{ animationDelay: "1.3s" }} />
            <circle className="nn-node" cx="500" cy="780" r="3" fill={theme.accentColor} style={{ animationDelay: "1.9s" }} />
            <circle className="nn-node" cx="680" cy="840" r="3.5" fill={theme.accentColor} style={{ animationDelay: "2.5s" }} />
            <circle className="nn-node" cx="840" cy="760" r="4" fill={theme.accentColor} style={{ animationDelay: "3.1s" }} />
            <circle className="nn-node" cx="1040" cy="840" r="3.5" fill={theme.accentColor} style={{ animationDelay: "0.6s" }} />
            <circle className="nn-node" cx="760" cy="940" r="3" fill={theme.accentColor} style={{ animationDelay: "1.2s" }} />
            <circle className="nn-node" cx="980" cy="680" r="3" fill={theme.accentColor} style={{ animationDelay: "1.8s" }} />
            <circle className="nn-node" cx="1180" cy="720" r="4" fill={theme.accentColor} style={{ animationDelay: "2.4s" }} />
            <circle className="nn-node" cx="1240" cy="860" r="3.5" fill={theme.accentColor} style={{ animationDelay: "3s" }} />
            <circle className="nn-node" cx="1180" cy="920" r="3" fill={theme.accentColor} style={{ animationDelay: "0.4s" }} />
            <circle className="nn-node" cx="1420" cy="900" r="3" fill={theme.accentColor} style={{ animationDelay: "1s" }} />
          </g>
        </svg>
      </div>

      {/* Floating particles */}
      <div className="particles text-white">
        {particles.map((p) => (
          <span
            key={p.id}
            className="particle"
            style={{
              left: `${p.left}%`,
              top: `${p.top}%`,
              width: p.size,
              height: p.size,
              animationDelay: `${p.delay}s`,
              animationDuration: `${p.dur}s`,
              boxShadow: `0 0 ${8 + p.size * 3}px 0 ${theme.accentColor}`,
            }}
          />
        ))}
      </div>

      {/* Cursor glow */}
      <div
        ref={glowRef}
        className="cursor-glow"
        style={{ opacity: ready ? 0.5 : 0 }}
      />
    </div>
  );
};