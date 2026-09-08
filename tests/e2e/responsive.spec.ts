import { test, expect } from "@playwright/test";

// Block render-blocking external font CSS so tests never depend on the network.
test.beforeEach(async ({ page }) => {
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
  await page.route(/https:\/\/www\.google\.com\/.*fonts/, (route) => route.abort());
});

/**
 * Responsive smoke tests: StudyLens must never overflow horizontally
 * on small phones (320 / 375 / 414 px), on any of the four nav tabs.
 */

const MOBILE_VIEWPORTS = [
  { name: "iPhone SE (320px)", width: 320, height: 568 },
  { name: "iPhone 13/14 (375px)", width: 375, height: 667 },
  { name: "iPhone Plus / Pro Max (414px)", width: 414, height: 896 },
];

const NAV_TAB_NAME: Record<string, RegExp> = {
  workbench: /pipeline/i,
  worked_example: /example/i,
  prompts: /prompts/i,
  specs: /specs/i,
};

const PANEL_ID: Record<string, string> = {
  workbench: "tabpanel-workbench",
  worked_example: "tabpanel-worked_example",
  prompts: "tabpanel-prompts",
  specs: "tabpanel-specs",
};

for (const vp of MOBILE_VIEWPORTS) {
  test.describe(`${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });

    for (const [key, tabName] of Object.entries(NAV_TAB_NAME)) {
      test(`"${key}" tab renders without horizontal overflow`, async ({ page }) => {
        await page.goto("/");
        await page.waitForLoadState("domcontentloaded");
        await expect(page.getByRole("tablist", { name: "Primary navigation" })).toBeVisible();

        await page
          .getByRole("tablist", { name: "Primary navigation" })
          .getByRole("tab", { name: tabName })
          .click();

        // Lazy chunks compile on demand in the dev server — allow generous time.
        await expect(page.locator(`#${PANEL_ID[key]}`)).toBeVisible({ timeout: 30_000 });

        const metrics = await page.evaluate(() => {
          const doc = document.documentElement;
          return {
            scrollWidth: doc.scrollWidth,
            clientWidth: doc.clientWidth,
            hasHorizontalOverflow: doc.scrollWidth > doc.clientWidth + 1,
          };
        });

        expect(
          metrics.hasHorizontalOverflow,
          `document scrollWidth ${metrics.scrollWidth} exceeds clientWidth ${metrics.clientWidth} at ${vp.width}px`
        ).toBe(false);
      });
    }

    test("primary navigation exposes four tab stops in the tablist", async ({ page }) => {
      await page.goto("/");
      const nav = page.getByRole("tablist", { name: "Primary navigation" });
      await expect(nav).toBeVisible();
      const tabs = nav.getByRole("tab");
      await expect(tabs).toHaveCount(4);
      // Exactly one tab must be selected at a time.
      const selected = await nav.locator('[aria-selected="true"]').count();
      expect(selected).toBe(1);
    });
  });
}

test("PWA manifest is served at /manifest.webmanifest", async ({ request }) => {
  const res = await request.get("/manifest.webmanifest");
  expect(res.ok()).toBeTruthy();
  const manifest = await res.json();
  expect(manifest.name).toContain("StudyLens");
  expect(manifest.display).toBe("standalone");
  expect(manifest.icons.length).toBeGreaterThanOrEqual(3);
});

test("service worker script is served at /sw.js", async ({ request }) => {
  const res = await request.get("/sw.js");
  expect(res.ok()).toBeTruthy();
  expect(await res.text()).toContain("CACHE_NAME");
});

test("theme picker updates the theme-color meta and persists the choice", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto("/");
  await page.getByRole("button", { name: /change visual theme/i }).click();
  const dialog = page.getByRole("dialog", { name: "Select Application Theme" });
  await expect(dialog).toBeVisible();

  // Select the Rose Studio card — closes the dialog and saves the theme.
  await dialog.getByRole("button", { name: /rose studio/i }).click();
  await expect(dialog).toBeHidden();

  expect(await page.evaluate(() => localStorage.getItem("studylens_theme"))).toBe("rose_studio");

  // meta[name=theme-color] must sync to the rose palette (#FBF7F8).
  expect(await page.getAttribute('meta[name="theme-color"]', "content")).toBe("#FBF7F8");
});