import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { THEME_PRESETS, ThemeProvider, useTheme } from "./ThemeContext";

function Probe() {
  const { themeKey, setThemeKey } = useTheme();
  return (
    <div>
      <span data-testid="current-key">{themeKey}</span>
      <button onClick={() => setThemeKey("clean_light")}>Set Light</button>
      <button onClick={() => setThemeKey("dark_studio")}>Set Dark</button>
    </div>
  );
}

let themeColorMeta: HTMLMetaElement | null = null;

function setupMeta() {
  themeColorMeta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  if (!themeColorMeta) {
    themeColorMeta = document.createElement("meta");
    themeColorMeta.name = "theme-color";
    document.head.appendChild(themeColorMeta);
  }
  return themeColorMeta;
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("defaults to the dark_studio theme", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(screen.getByTestId("current-key").textContent).toBe("dark_studio");
  });

  it("persists theme selection to localStorage", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByText("Set Light"));
    expect(screen.getByTestId("current-key").textContent).toBe("clean_light");
    expect(localStorage.getItem("studylens_theme")).toBe("clean_light");
  });

  it("restores a previously saved theme on mount", () => {
    localStorage.setItem("studylens_theme", "rose_studio");
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(screen.getByTestId("current-key").textContent).toBe("rose_studio");
  });

  it("syncs the <meta name=theme-color> tag to the active theme", () => {
    const meta = setupMeta();
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(meta.getAttribute("content")).toBe(THEME_PRESETS.dark_studio.bgPreview);

    fireEvent.click(screen.getByText("Set Light"));
    expect(meta.getAttribute("content")).toBe(THEME_PRESETS.clean_light.bgPreview);
  });
});