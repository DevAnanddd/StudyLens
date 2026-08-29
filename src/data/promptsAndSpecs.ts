/**
 * StudyLens Prompt Specifications & System Design
 * Contains the exact prompt strings, user templates, schemas, and design guidelines.
 */

export const EXACT_SYSTEM_PROMPT = `You are StudyLens, an expert academic synthesizer that transforms messy, noisy OCR text extracted from lecture slides, screenshots, and PDFs into clean, structured revision notes for university exams.

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

# Topic Name
## Overview
- point
## Important Concepts
- concept
## Definitions
- **Term:** Definition
## Key Points
- point
## Exam Revision
- high-priority point
## Sources
- Lecture_1.pdf, Page 5`;

export const EXACT_TAGGING_SYSTEM_PROMPT = `You are a high-speed topic categorization engine for lecture slides.
Your task is to analyze a batch of raw, noisy OCR slides and assign a concise, standardized topic title and 1-3 key concept keywords for each slide.

Rules:
1. Normalize topic names into clean Title Case (e.g., "Virtual Memory", "Page Replacement Algorithms", "Convolutional Layers").
2. Standardize synonymous topics (e.g., "Paging Intro" and "Intro to Paging" should both be "Virtual Memory - Paging").
3. Detect slide type: "content", "title_slide", "outline", "review", or "qa".
4. Assign a confidence score between 0.0 and 1.0.
5. Return strictly structured JSON matching the requested schema.`;

export const USER_PROMPT_TAGGING_TEMPLATE = `Classify the following {{SLIDE_COUNT}} lecture slides:

{{SLIDES_BLOCK}}`;

export const SLIDE_ENVELOPE_TAGGING_EXAMPLE = `<slide id="s_01" file="OS_Lecture_04.pdf" page="12">
CS 240 -- Operating Systems -- Prof. Miller
PAGE REPLACEMENT -- FIFO VS LRU
Belady's Anomaly:
FIFO can suffer from more page fau1ts with more frames!
Examp1e: 3 frames vs 4 frames on string: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5
LRU does NOT suffer from Belady's anomaly (stack algorithm)
--- page 12 ---
</slide>`;

export const USER_PROMPT_SUMMARIZATION_TEMPLATE = `Synthesize the following OCR slides for the topic cluster: "{{TOPIC_NAME}}"

### SLIDE SOURCE MANIFEST:
{{SOURCES_LIST}}

### RAW OCR SLIDE CONTENT:
{{SLIDES_OCR_BLOCK}}

Generate the complete revision note section in the exact Markdown template.`;

export const WORKED_EXAMPLE_INPUT = [
  {
    id: "slide_01",
    filename: "CS301_OS_Lecture4.pdf",
    pageNumber: 14,
    rawOcr: `CS301 Principles of Operating Systems | Spring 2025
Prof. D. Vance | Lecture 04: Memory Mgmt
---
VIRTUAL MEMORY & PAGING
* Why Virtual Memory?
  - Physical RAM is 1imited (e.g. 16GB)
  - Processes need iso1ation and contiguous address space
  - Illusion of large memory: Address Space > Physical RAM
* Page vs Frame:
  - Page: Fixed-size block of virtua1 memory (typically 4 KB)
  - Frame (Page Frame): Fixed-size block of physica1 memory
* Address Translation:
  - Virtua1 Address = [ Virtual Page Number (VPN) | Offset (d) ]
  - Phys Address = [ Physical Frame Number (PFN) | Offset (d) ]
  - Offset size $d = \\log_2(\\text{Page Size})$
--- [CS301-P14] ---`,
  },
  {
    id: "slide_02",
    filename: "CS301_OS_Lecture4.pdf",
    pageNumber: 15,
    rawOcr: `CS301 Principles of Operating Systems
Prof. D. Vance
PAGE TABLES & TRANSLATION
* Page Table:
  - Per-process data structure mapping VPN -> PFN
  - Managed by OS, accessed by MMU (Memory Mgmt Unit)
* Page Table Entry (PTE) Flags:
  - Va1id bit: 1 if page in RAM, 0 if on disk (swapped)
  - Dirty (Modified) bit: 1 if page written to
  - Reference (Access) bit: 1 if page read/written recently
  - Read/Write/Exec permissions
* Formula:
  $\\text{Physical Address} = (\\text{PFN} \\times \\text{Page Size}) + \\text{Offset}$
  Page size = 4KB ($2^{12}$ bytes) -> offset is 12 bits.
--- slide 15 ---`,
  },
  {
    id: "slide_03",
    filename: "CS301_OS_Lecture4.pdf",
    pageNumber: 16,
    rawOcr: `CS301 Lecture 4: Memory Mgmt
PAGE FAULT HANDLING FLOW
What happens on invalid PTE access?
1. CPU tries to access virtual address -> MMU checks PTE
2. Valid bit is 0 -> MMU triggers Page Fault Trap (interrupt 14)
3. OS kernel page fault handler executes:
   a. Check if address is valid in process address space (if not: segfau1t!)
   b. Find a free physical frame (or evict dirty page via replacement algo)
   c. Issue disk I/O to read missing page into frame
   d. Update PTE: set PFN and Valid bit = 1
   e. Restart faulting instruction!
* Note: Disk I/O is slow (~5-10ms) vs RAM (~50-100ns).
--- slide 16 ---`,
  },
];

export const WORKED_EXAMPLE_TAGGED_OUTPUT = [
  {
    slideId: "slide_01",
    topic: "Virtual Memory and Paging",
    subtopic: "Virtual vs Physical Addressing",
    keywords: ["Virtual Memory", "Paging", "VPN", "PFN", "Page Offset"],
    slideType: "content",
    confidence: 0.98,
  },
  {
    slideId: "slide_02",
    topic: "Virtual Memory and Paging",
    subtopic: "Page Table Architecture & PTE Flags",
    keywords: ["Page Table Entry", "Valid Bit", "Dirty Bit", "MMU"],
    slideType: "content",
    confidence: 0.96,
  },
  {
    slideId: "slide_03",
    topic: "Virtual Memory and Paging",
    subtopic: "Page Fault Handling Mechanism",
    keywords: ["Page Fault", "Trap Handler", "Disk I/O", "PTE Update"],
    slideType: "content",
    confidence: 0.97,
  },
];

export const WORKED_EXAMPLE_FINAL_MARKDOWN = `# Virtual Memory and Paging

## Overview
- Virtual memory decouples process virtual address spaces from physical RAM, providing hardware isolation, simplified memory allocation, and the illusion of a contiguous address space larger than physical memory.
- Memory is split into uniform fixed-size chunks: virtual **pages** map directly into physical **frames** (typically 4 KB) via hardware-assisted address translation.

## Important Concepts
- **Address Translation Mechanism**: Virtual addresses are split into a Virtual Page Number (VPN) and an Offset ($d$). The Memory Management Unit (MMU) indexes the per-process Page Table using the VPN to locate the Physical Frame Number (PFN). The physical address is computed as:
  $$\\text{Physical Address} = (\\text{PFN} \\times \\text{Page Size}) + \\text{Offset}$$
- **PTE Control Bits**: Each Page Table Entry (PTE) contains status bits:
  - *Valid bit*: Indicates whether the page is resident in physical RAM ($1$) or stored on swap disk ($0$).
  - *Dirty bit*: Set to $1$ when the page has been modified; requires writeback to disk upon eviction.
  - *Reference bit*: Set when accessed, utilized by page replacement algorithms (e.g., Clock / NRU).
- **Page Fault Lifecycle**:
  1. MMU encounters a PTE with $\\text{Valid} = 0$, triggering a hardware Page Fault trap (Interrupt 14).
  2. OS handler validates memory bounds (terminates with \`SIGSEGV\` if invalid).
  3. OS locates a free physical frame (or executes a page eviction policy).
  4. Non-blocking disk I/O loads the required page into the frame.
  5. OS updates PTE with the new PFN, sets $\\text{Valid} = 1$, and restarts the faulting instruction transparently.

## Definitions
- **Page:** A fixed-size contiguous block of virtual memory (typically 4 KB / $2^{12}$ bytes).
- **Frame:** A fixed-size physical memory block in RAM that holds one virtual page.
- **MMU (Memory Management Unit):** Hardware component responsible for translating virtual addresses to physical addresses at runtime.
- **Page Fault:** An interrupt raised by the MMU when a program accesses a virtual page that is not currently mapped into physical RAM.

## Key Points
- The offset bits ($d$) remain unchanged between virtual and physical addresses; only the page number is translated. Offset bit-width equals $\\log_2(\\text{Page Size})$ (e.g., 12 bits for a 4 KB page).
- Disk I/O during page fault resolution creates a massive performance penalty (~5–10 ms disk latency vs ~50–100 ns RAM access).

## Exam Revision
- **Address Calculation Formula**: Given a 32-bit virtual address and 4 KB page size, 12 bits are allocated for Offset ($2^{12} = 4096$) and the upper 20 bits represent the VPN ($2^{20} = 1\\text{M pages}$).
- **Instruction Restartability**: Ensure you remember that after a page fault trap is serviced, the processor restarts the exact machine instruction that caused the fault, not the subsequent instruction.
- **Dirty Page Eviction**: Evicting a clean page costs 0 disk writes, whereas evicting a dirty page requires synchronous or asynchronous writeback to swap storage.

## Sources
- CS301_OS_Lecture4.pdf, Page 14
- CS301_OS_Lecture4.pdf, Page 15
- CS301_OS_Lecture4.pdf, Page 16`;
