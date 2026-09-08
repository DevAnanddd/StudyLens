import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../context/ThemeContext";
import { Header } from "./Header";

describe("Header", () => {
  it("renders a scrollable tablist with four tabs", () => {
    render(
      <ThemeProvider>
        <Header activeTab="workbench" setActiveTab={vi.fn()} hasApiKey={false} />
      </ThemeProvider>
    );

    const tablist = screen.getByRole("tablist", { name: /primary navigation/i });
    expect(tablist).toBeInTheDocument();
    expect(tablist.className).toContain("mobile-scroll-tabs");
    expect(screen.getAllByRole("tab")).toHaveLength(4);
  });

  it("marks the active tab as aria-selected", () => {
    render(
      <ThemeProvider>
        <Header activeTab="prompts" setActiveTab={vi.fn()} hasApiKey={false} />
      </ThemeProvider>
    );

    const promptsTab = screen.getByRole("tab", { name: /prompt inspector/i });
    expect(promptsTab).toHaveAttribute("aria-selected", "true");
    expect(promptsTab).toHaveAttribute("id", "nav-tab-prompts");
    expect(promptsTab).toHaveAttribute("aria-controls", "tabpanel-prompts");
  });

  it("fires setActiveTab when a tab is clicked", () => {
    const setActiveTab = vi.fn();
    render(
      <ThemeProvider>
        <Header activeTab="workbench" setActiveTab={setActiveTab} hasApiKey={false} />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole("tab", { name: /architecture/i }));
    expect(setActiveTab).toHaveBeenCalledWith("specs");
  });
});