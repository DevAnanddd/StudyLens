import { SlideOCRInput } from "../types";

export interface DeckPreset {
  id: string;
  name: string;
  course: string;
  description: string;
  slideCount: number;
  slides: SlideOCRInput[];
}

export const SAMPLE_DECKS: DeckPreset[] = [
  {
    id: "cs240_os",
    name: "CS 240: Virtual Memory & Page Replacement",
    course: "Computer Science / OS",
    description: "12 slides containing noisy OCR, broken tables, math formulas, repeated headers, and non-consecutive page replacement slides.",
    slideCount: 12,
    slides: [
      {
        id: "slide_01",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 1,
        rawOcr: `CS240 -- Operating Systems -- Spring 2025
Prof. Arthur Pendelton
Lecture 7: Memory Management & Virtual Memory Architecture
[Outline]
* Virtual Memory Motivation
* Paging & Address Translation
* Multi-Level Page Tables
* Translation Lookaside Buffers (TLB)
* Page Fault Hand1ing & Replacement
--- University of Tech -- Slide 1 ---`,
      },
      {
        id: "slide_02",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 2,
        rawOcr: `CS240: OS -- Prof. Pendelton
1. WHY VIRTUAL MEMORY?
Prob1em in ear1y systems:
- Uniprogramming: only 1 app in RAM
- Multiprogramming requires memory protection!
Benefits of Virtual Memory:
1. Protection / Isolation: Each process has its own private address space [0, 2^N - 1]
2. Transparancy: Programmers don't need to know where physical RAM begins
3. Resource Sharing: Shared libraries (libc) mapped read-only to multiple processes
4. Overcommitting: Total allocated virtual space can exceed physical RAM!
--- CS240 / Slide 2 ---`,
      },
      {
        id: "slide_03",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 3,
        rawOcr: `CS240: OS
PAGING BASICS: PAGES & FRAMES
* Virtual address space divided into fixed-size units: PAGES
* Physica1 memory (DRAM) divided into fixed-size units: FRAMES
* Page Size is always power of 2 (typically 4KB = 4096 bytes = 2^12)
Virtual Address = [ Virtual Page Number (VPN) | Offset (p) ]
Physical Address = [ Physical Frame Number (PFN) | Offset (p) ]
* Crucial Rule: Offset is UNCHANGED during address translation!
Bits for offset: $k = \\log_2(\\text{Page Size})$. For 4KB, $k = 12$ bits.
--- Page 3 ---`,
      },
      {
        id: "slide_04",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 4,
        rawOcr: `CS240 -- Memory Mgmt
PAGE TABLES & TRANSLATION
Page Table is an array in OS memory indexed by VPN.
Each entry is a PTE (Page Table Entry):
[ Valid(1) | Dirty(1) | Ref(1) | Prot(3) | Physical Frame Number (PFN) ]
Hardware MMU Translation steps:
1. Extract VPN = (Virtual_Addr >> 12)
2. Extract Offset = (Virtual_Addr & 0xFFF)
3. Lookup PTE at: Page_Table_Base_Reg + (VPN * sizeof(PTE))
4. If Valid bit == 0 -> TRAP: PAGE FAULT!
5. Else Phys_Addr = (PTE.PFN << 12) | Offset
--- CS240 Slide 4 ---`,
      },
      {
        id: "slide_05",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 5,
        rawOcr: `CS240: OS -- Prof. Pendelton
TRANSLATION LOOKASIDE BUFFER (TLB)
Issue: Every memory access requires 2 physical RAM accesses!
(1 to read Page Table in memory, 1 to read actual data)
Solution: TLB is a fast hardware cache inside the CPU MMU.
* TLB stores recent (VPN -> PFN + flags) mappings.
Effective Access Time (EAT):
$$\\text{EAT} = h \\times (t_{\\text{TLB}} + t_{\\text{RAM}}) + (1 - h) \\times (t_{\\text{TLB}} + 2 \\times t_{\\text{RAM}})$$
Where $h$ = TLB hit rate (typically 98-99%).
If $t_{\\text{TLB}} = 1\\text{ns}, t_{\\text{RAM}} = 100\\text{ns}, h = 0.99$:
$\\text{EAT} = 0.99(101) + 0.01(201) = 99.99 + 2.01 = 102\\text{ns}$ (vs 200ns without TLB!)
--- Slide 5 ---`,
      },
      {
        id: "slide_06",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 6,
        rawOcr: `CS240
MULTI-LEVEL PAGE TABLES
Problem: 32-bit address space, 4KB page -> $2^{20}$ pages = 1M entries!
4MB page table PER process. For 64-bit: astronomical.
Solution: Split VPN into hierarchical levels (e.g. 2-level paging):
VPN = [ Directory Index (10 bits) | Table Index (10 bits) | Offset (12 bits) ]
Benefit: Sparse allocation! Unused memory regions don't need level-2 page tables allocated.
Trade-off: TLB miss now incurs 3 RAM accesses instead of 2.
--- Page 6 ---`,
      },
      {
        id: "slide_07",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 7,
        rawOcr: `CS240: Operating Systems
PAGE REPLACEMENT: FIFO & BELADY'S ANOMALY
When RAM is full and a page fau1t occurs, which frame to evict?
Algorithm 1: First-In First-Out (FIFO)
- Evict the oldest page brought into memory.
- Easy to implement with queue.
BELADY'S ANOMALY:
- Giving MORE physical frames can sometimes CAUSE MORE page faults!
Example on reference string: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5
- 3 frames: 9 page faults
- 4 frames: 10 page faults!
Stack algorithms (like LRU, OPT) NEVER suffer from Belady's Anomaly.
--- Slide 7 ---`,
      },
      {
        id: "slide_08",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 8,
        rawOcr: `CS240
OPTIMAL (OPT / MIN) & LRU REPLACEMENT
Algorithm 2: Optimal (Belady's MIN)
- Evict the page that will NOT be used for the longest time in future.
- Impossible in practice (requires clairvoyant future knowledge).
- Serves as theoretical benchmark.
Algorithm 3: Least Recently Used (LRU)
- Evict page that has not been used for longest time in past.
- Approximates OPT using temporal locality.
- Heavy overhead: requires timestamp/doubly linked list on EVERY memory access.
--- Page 8 ---`,
      },
      {
        id: "slide_09",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 9,
        rawOcr: `CS240: OS
CLOCK ALGORITHM (SECOND CHANCE LRU)
Practical approximation of LRU using hardware Reference Bit:
* Arrange frames in circular buffer with a clock hand pointer.
Step 1: Check frame under hand.
Step 2: If Ref Bit == 1 -> set Ref Bit = 0, advance hand.
Step 3: If Ref Bit == 0 -> EVICT this frame! Advance hand.
* Enhanced Clock Algorithm: uses (Reference, Dirty) bits:
(0, 0) : best to evict (not recently used, clean - no I/O)
(0, 1) : second best (not recently used, dirty - requires disk write)
(1, 0) : recently used, clean
(1, 1) : recently used, dirty
--- Slide 9 ---`,
      },
      {
        id: "slide_10",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 10,
        rawOcr: `CS240: Operating Systems -- Prof. Pendelton
PAGE FAULT HANDLING LIFECYCLE SUMMARY
Summary of Kernel Sequence:
1. MMU encounters invalid PTE -> Interrupt 14 (Trap to Kernel)
2. Save user registers & state
3. Validate address against VMA structures (if illegal -> SIGSEGV)
4. Select replacement frame (Clock / LRU)
5. If victim page is dirty -> swap_write to disk
6. swap_read missing page from disk into frame
7. Update PTE: PFN assigned, Valid bit = 1
8. Invalidate TLB entry for this virtual page (TLB shootdown if SMP)
9. Restore registers, return from trap, RESTART FAULTING INSTRUCTION!
--- Slide 10 ---`,
      },
      {
        id: "slide_11",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 11,
        rawOcr: `CS240: OS
PAGE REPLACEMENT REVISITED: THRASHING
What happens when total Working Set Size (WSS) > Physical RAM?
- Every process page faults constantly!
- CPU utilization plummets because all processes wait for disk I/O.
- OS spends 99% of time swapping pages in/out -> THRASHING!
Working Set Model:
$$W(t, \\Delta) = \\text{set of pages referenced in time window } [t - \\Delta, t]$$
OS solution: If $\\sum |W_i| > \\text{Total Frames}$, suspend/swap-out entire processes to restore throughput.
--- Page 11 ---`,
      },
      {
        id: "slide_12",
        filename: "CS240_Lecture07_Memory.pdf",
        pageNumber: 12,
        rawOcr: `CS240 Lecture 7 Summary & Exam Tips
EXAM CHECKLIST:
* Remember: Offset never changes during translation ($k = \\log_2(\\text{size})$)
* EAT formula with TLB: memorize hit vs miss paths!
* FIFO has Belady's Anomaly; LRU and OPT do NOT.
* Clock Algorithm uses Reference bit clearing (second chance).
* Thrashing happens when $\\sum \\text{Working Sets} > \\text{Physical RAM}$.
* [⚠️ Unclear OCR: formula cutoff on page 12 margin: PageSize * 2^(...)]
Good luck on Midterm 2!
--- End of Lecture 7 ---`,
      },
    ],
  },
  {
    id: "ml401_cnn",
    name: "ML 401: Convolutional Neural Networks",
    course: "Machine Learning / AI",
    description: "8 slides covering Conv2D math, receptive fields, stride/padding formulas, pooling, and backpropagation trade-offs.",
    slideCount: 8,
    slides: [
      {
        id: "ml_01",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 1,
        rawOcr: `ML401 -- Deep Learning -- Fall 2025
Lecture 5: Convolutional Neural Networks (CNNs)
Why not Fully Connected (MLP) for images?
- Input 1000x1000 RGB image = 3,000,000 inputs!
- Hidden layer with 1000 neurons -> 3 BILLION parameters! Overfitting + memory explosion.
Key CNN Inductive Biases:
1. Local Connectivity: Neurons only connect to a small local receptive field.
2. Weight Sharing (Spatial Invariance): The same filter/kernel is slid across entire image.
3. Translation Equivariance: $f(g(x)) = g(f(x))$.
--- Slide 1 ---`,
      },
      {
        id: "ml_02",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 2,
        rawOcr: `ML401: Deep Learning
2D CONVOLUTION (CROSS-CORRELATION) MATH
For input feature map $X$ and kernel $K$ of size $k_h \\times k_w$:
$$Y(i, j) = (X * K)(i, j) = \\sum_{m=0}^{k_h-1} \\sum_{n=0}^{k_w-1} X(i+m, j+n) K(m, n) + b$$
With multiple input channels $C_{in}$ and output channels $C_{out}$:
$$Y_k(i, j) = \\sum_{c=1}^{C_{in}} (X_c * K_{k,c})(i, j) + b_k$$
Total parameters per layer: $(k_h \\times k_w \\times C_{in} + 1) \\times C_{out}$.
--- Page 2 ---`,
      },
      {
        id: "ml_03",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 3,
        rawOcr: `ML401
OUTPUT DIMENSION FORMULA (PADDING & STRIDE)
Input size: $W_{in} \\times H_{in}$, Kernel: $K$, Stride: $S$, Padding: $P$
$$W_{out} = \\left\\lfloor \\frac{W_{in} - K + 2P}{S} \\right\\rfloor + 1$$
$$H_{out} = \\left\\lfloor \\frac{H_{in} - K + 2P}{S} \\right\\rfloor + 1$$
Padding types:
* Valid (no padding, $P=0$): Output shrinks.
* Same padding ($S=1$): Choose $P = (K - 1) / 2$ so $W_{out} = W_{in}$.
--- Slide 3 ---`,
      },
      {
        id: "ml_04",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 4,
        rawOcr: `ML401: Deep Learning
POOLING LAYERS (DOWNSAMPLING)
Purpose: Reduce spatial resolution, increase receptive field, provide translation invariance.
1. Max Pooling: Selects maximum activation in $k \\times k$ window. (Most common)
2. Average Pooling: Computes arithmetic mean. Often used at very end (Global Avg Pooling).
Properties:
- Parameter-free! (No weights to learn, only hyperparams: window size $K$, stride $S$).
- Does NOT change number of channels ($C_{out} = C_{in}$).
--- Page 4 ---`,
      },
      {
        id: "ml_05",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 5,
        rawOcr: `ML401: Deep Learning
RECEPTIVE FIELD CALCULATION
Definition: Receptive field is the region in the input image that directly influences a particular feature unit.
Two $3\\times 3$ convolutions with stride 1 have the same receptive field ($5\\times 5$) as one $5\\times 5$ convolution!
Why prefer smaller filters (VGG principle):
- Two $3\\times 3$ filters: $2 \\times (3^2 \\times C^2) = 18 C^2$ parameters.
- One $5\\times 5$ filter: $5^2 \\times C^2 = 25 C^2$ parameters (28% more weights!).
- Plus: Two non-linearities (ReLU) instead of one!
--- Slide 5 ---`,
      },
      {
        id: "ml_06",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 6,
        rawOcr: `ML401
RESIDUAL NETWORKS (RESNET) & SKIP CONNECTIONS
Problem in very deep networks (e.g. 50+ layers): Vanishing/Exploding Gradients and Degradation problem.
He et al. (2015) Solution: Skip / Residual Connection:
$$\\mathcal{H}(x) = \\mathcal{F}(x) + x$$
Gradient backprop:
$$\\frac{\\partial \\mathcal{L}}{\\partial x} = \\frac{\\partial \\mathcal{L}}{\\partial \\mathcal{H}} \\left( \\frac{\\partial \\mathcal{F}}{\\partial x} + 1 \\right)$$
Notice the $+1$ term! Gradients can flow directly back without vanishing!
--- Page 6 ---`,
      },
      {
        id: "ml_07",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 7,
        rawOcr: `ML401: Deep Learning
CLASSIC CNN ARCHITECTURES SUMMARY
1. LeNet-5 (1998): 5x5 convs, avg pool, MNIST digits.
2. AlexNet (2012): 11x11, 5x5, 3x3 convs, ReLU, Dropout, GPU training.
3. VGG-16/19 (2014): Uniform 3x3 convs throughout, deeper network.
4. ResNet-50 (2015): Residual identity blocks, solved 100+ layer training.
--- Slide 7 ---`,
      },
      {
        id: "ml_08",
        filename: "ML401_CNN_Lecture.pdf",
        pageNumber: 8,
        rawOcr: `ML401 Exam Review Sheet
Formulas to memorize:
- Output dimension: $\\lfloor(W - K + 2P)/S\\rfloor + 1$
- Parameter count: $(K^2 \\times C_{in} + 1) \\times C_{out}$
- ResNet residual gradient flow formula
[⚠️ Unclear OCR: blurred footer notes on weight decay: lr * 0.95^epoch...]
--- End of ML401 Lecture 5 ---`,
      },
    ],
  },
];
