import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json({ limit: "20mb" }));

// Server-Side Gemini Initialization
const apiKey = process.env.GEMINI_API_KEY;
let ai: GoogleGenAI | null = null;

if (apiKey && apiKey !== "MY_GEMINI_API_KEY") {
  ai = new GoogleGenAI({
    apiKey: apiKey,
    httpOptions: {
      headers: {
        "User-Agent": "aistudio-build",
      },
    },
  });
}

// 1. Health check endpoint
app.get("/api/health", (_req, res) => {
  res.json({
    status: "ok",
    hasApiKey: !!(apiKey && apiKey !== "MY_GEMINI_API_KEY"),
  });
});

// 2. Lightweight Topic Tagging Endpoint
app.post("/api/pipeline/tag", async (req, res) => {
  try {
    const { slides } = req.body;
    if (!slides || !Array.isArray(slides)) {
      return res.status(400).json({ error: "slides array is required" });
    }

    if (!ai) {
      return res.status(503).json({
        error: "Gemini API key is not configured on server. Please use client simulation or provide GEMINI_API_KEY.",
      });
    }

    const systemInstruction = `You are a high-speed topic categorization engine for lecture slides.
Your task is to analyze a batch of raw, noisy OCR slides and assign a concise, standardized topic title and 1-3 key concept keywords for each slide.

Rules:
1. Normalize topic names into clean Title Case (e.g., "Virtual Memory", "Page Replacement Algorithms", "Convolutional Layers").
2. Standardize synonymous topics (e.g., "Paging Intro" and "Intro to Paging" should both be "Virtual Memory - Paging").
3. Detect slide type: "content", "title_slide", "outline", "review", or "qa".
4. Assign a confidence score between 0.0 and 1.0.
5. Return strictly structured JSON matching the requested schema.`;

    const userPrompt = `Classify the following ${slides.length} lecture slides:

${slides
  .map(
    (s: { id: string; filename: string; pageNumber: number; rawOcr: string }) => `
<slide id="${s.id}" file="${s.filename}" page="${s.pageNumber}">
${s.rawOcr}
</slide>`
  )
  .join("\n\n")}`;

    const response = await ai.models.generateContent({
      model: "gemini-3.7-flash",
      contents: userPrompt,
      config: {
        systemInstruction,
        temperature: 0.1,
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.ARRAY,
          description: "List of tagged slides",
          items: {
            type: Type.OBJECT,
            properties: {
              slideId: { type: Type.STRING, description: "Matches the id attribute of the slide" },
              topic: { type: Type.STRING, description: "Normalized primary topic name" },
              subtopic: { type: Type.STRING, description: "Optional subtopic or section focus" },
              keywords: {
                type: Type.ARRAY,
                items: { type: Type.STRING },
                description: "Key concepts mentioned in slide",
              },
              slideType: {
                type: Type.STRING,
                description: "content, title_slide, outline, review, or qa",
              },
              confidence: { type: Type.NUMBER, description: "Confidence score 0.0 to 1.0" },
            },
            required: ["slideId", "topic", "keywords", "slideType", "confidence"],
          },
        },
      },
    });

    const parsed = JSON.parse(response.text || "[]");
    return res.json({ tags: parsed });
  } catch (error: any) {
    console.error("Error in /api/pipeline/tag:", error);
    return res.status(500).json({ error: error.message || "Failed to tag slides" });
  }
});

// 3. Topic Summarization Endpoint
app.post("/api/pipeline/summarize", async (req, res) => {
  try {
    const { topicName, slides } = req.body;
    if (!topicName || !slides || !Array.isArray(slides)) {
      return res.status(400).json({ error: "topicName and slides array are required" });
    }

    if (!ai) {
      return res.status(503).json({
        error: "Gemini API key is not configured on server.",
      });
    }

    const systemInstruction = `You are StudyLens, an expert academic synthesizer that transforms messy, noisy OCR text extracted from lecture slides, screenshots, and PDFs into clean, structured revision notes for university exams.

Your objective is to produce high-density, accurate revision notes strictly adhering to the specified Markdown format.

### CORE TRANSFORMATION RULES:
1. **OCR Cleanup & Repair:**
   - Strip OCR artifacts, line break hyphenations, garbled punctuation, page footers, repeated slide headers, professor names, and slide numbers.
   - Fix obvious OCR character misrecognitions (e.g., '0' instead of 'O', '1' instead of 'l', 'rn' instead of 'm', 'vv' instead of 'w', 'f(x) — \int' into 'f(x) = \\int') ONLY when the academic context makes the correction 100% unambiguous.
   - Never alter domain-specific jargon, variable names, or chemical/mathematical notations.

2. **Preservation of Technical Entities:**
   - Formulas and equations MUST be preserved in exact LaTeX syntax enclosed in '$...$' (inline) or '$$...$$' (block).
   - Code snippets and pseudocode MUST be formatted in standard fenced code blocks with language identifiers.
   - Technical parameter names, constants, and asymptotic complexities (e.g., $O(n \\log n)$, $\\alpha = 0.05$) must be kept verbatim.

3. **Strict Anti-Hallucination & Uncertainty Flagging:**
   - NEVER invent, infer, or extrapolate information not directly stated or implied in the source slides.
   - If OCR text is partially cut off or illegible in a critical formula or concept, DO NOT guess. Flag it explicitly:
     \`[⚠️ Unclear OCR: <flagged text fragment>]\`
   - Synthesize content across overlapping/duplicate slides into a single cohesive explanation without repetition.

4. **Exam-Focused Revision Density:**
   - Write concise, bulleted explanations with strong conceptual clarity.
   - Prioritize definitions, mechanistic trade-offs, edge cases, formulas, and common exam pitfalls.

5. **Mandatory Output Schema:**
   You MUST structure your response ONLY in the following Markdown format (do NOT wrap in JSON or extra commentary):

# ${topicName}
## Overview
- Concise 2-3 bullet high-level summary of the topic's core thesis and role.
## Important Concepts
- In-depth bulleted explanation of mechanisms, workflows, algorithms, or theories.
## Definitions
- **Term:** Clear, rigorous definition extracted directly from the text.
## Key Points
- Core facts, properties, trade-offs, advantages/disadvantages, or theorems.
## Exam Revision
- High-priority exam pointers, common pitfalls, tricky edge cases, and formula reminders.
## Sources
- List every contributing source slide in the format: <Filename>, Page <PageNumber>`;

    const userPrompt = `Synthesize the following OCR slides for the topic cluster: "${topicName}"

### SLIDE SOURCE MANIFEST:
${slides.map((s: { filename: string; pageNumber: number }) => `- ${s.filename}, Page ${s.pageNumber}`).join("\n")}

### RAW OCR SLIDE CONTENT:
${slides
  .map(
    (s: { filename: string; pageNumber: number; rawOcr: string }) => `
--- SLIDE START: ${s.filename} [Page ${s.pageNumber}] ---
${s.rawOcr}
--- SLIDE END ---`
  )
  .join("\n\n")}

Generate the complete revision note section in the exact Markdown template.`;

    const response = await ai.models.generateContent({
      model: "gemini-3.7-flash",
      contents: userPrompt,
      config: {
        systemInstruction,
        temperature: 0.2,
        topP: 0.95,
      },
    });

    return res.json({ markdown: response.text || "" });
  } catch (error: any) {
    console.error("Error in /api/pipeline/summarize:", error);
    return res.status(500).json({ error: error.message || "Failed to summarize topic" });
  }
});

// Vite middleware / static serving
async function start() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`StudyLens server running on http://0.0.0.0:${PORT}`);
  });
}

start();
