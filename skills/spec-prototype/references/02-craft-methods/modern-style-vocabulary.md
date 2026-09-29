# Modern Style Vocabulary (现代设计风格语汇与反向推导)

**This is a challenger source, not a direction menu.** Directions are generated from
the domain's own lifeworld by the Divergence Generator
([`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md) §4).
This file is read at step 4 of that generator — to fuse a technique into a
domain-sourced candidate — and never at step 2 to supply the candidate itself.
Selecting a style from this list as a direction's identity is the failure this file
is arranged to prevent: five options read as five directions, but two draws from
five options is a coin flip, not a divergence.

Read each entry for its *techniques* and its *quality bar* — the bar is what makes a
fused technique land instead of reading as a reskin.

## 1. Scene Reverse-Derivation (场景反向推导器)

Use as a **cross-check after step 5**, not as the generator. Once two candidates have
passed the two-axis verdict, confirm the pair is not a disguised draw from this table.
If the pair maps cleanly onto two rows below, the directions were sourced from the
catalog rather than the domain — return to step 2.

| Operational Context & User Need | Vocabulary | Core Tension Resolved |
|---|---|---|
| **High-concurrency monitoring, heavy telemetry, domain operations** | Dense Telemetry / Instrument | Scanning speed vs. visual noise |
| **Long-form reading, governance, legal/compliance, technical docs** | Swiss Editorial Grid | Cognitive fatigue vs. structural hierarchy |
| **Consumer tool, creative workspace, collaborative canvas** | Tactile Neo-Skeuomorphic | Intuitiveness vs. screen real-estate |
| **Developer utility, infrastructure control, terminal/CLI hybrid** | Brutalist Code / Monospace | Raw clarity vs. complex state disclosure |
| **Executive analytics, portfolio overview, strategic reporting** | Bento Grid Modular | Summary density vs. presentation polish |

---

## 2. Style Vocabularies, Techniques & Quality Bars

Each entry carries **techniques** (what to fuse) and a **QUALITY BAR** (what separates
a fused technique that lands from one that reads as a costume). The bar is the
load-bearing half: the techniques alone are the reskin.

### A. Dense Telemetry / Instrument (高密仪表)
- **Purpose**: Maximize information throughput and situational awareness for expert operators.
- **Techniques**:
  - Monospace or tabular figures (`font-variant-numeric: tabular-nums`).
  - Micro-grid rhythm (4px/8px baselines, 1px hairline borders).
  - High-contrast status pips (e.g. emerald/amber/crimson against dark or crisp slate voids).
- **QUALITY BAR**: every visible mark is a datum or a boundary between data. A hairline
  that separates nothing, or a pip whose colour encodes no state, fails the bar — it is
  noise wearing the vocabulary. Density is earned by *removing* chrome, not by shrinking type.
- **Failure Mode**: Cramped, illegible label truncation; lack of visual rest zones.

### B. Swiss Editorial Grid (瑞士/编辑网格)
- **Purpose**: Elevate textual authority and narrative coherence through rigorous typography and asymmetric margins.
- **Techniques**:
  - Clear typographic ladder with strong contrast between title measure and body running text.
  - Generous whitespace as functional divider rather than decorative container boxes.
  - Subdued, warm paper background tones with rich ink typography.
- **QUALITY BAR**: the grid is legible in the result — a reader can see the columns even
  where nothing is drawn on them. Whitespace that would survive a different type scale is
  decoration; whitespace that exists because *this* measure needs it is the vocabulary.
- **Failure Mode**: Rigid refusal to handle dynamic data; text overflowing fixed grid containers.

### C. Tactile Neo-Skeuomorphic (温和触感)
- **Purpose**: Create immediate physical affordance and sensory delight in interactive controls.
- **Techniques**:
  - Realistic `:active` press detents and micro-elevations.
  - Concentric radii ($R_{in} = \max(0, R_{out} - P)$) for natural nested containment.
  - Multi-stop soft ambient drop shadows without harsh neon glow.
- **QUALITY BAR**: every depth cue answers a real question — what is above what, what is
  pressable, what is inset. Depth that only makes a surface look richer fails the bar;
  skeuomorphism is a claim about *behaviour* (this moves, this resists, this seats), not a finish.
- **Failure Mode**: Visual bloat, excessive gradients distracting from content.

### D. Bento Grid Modular (Bento 模块化)
- **Purpose**: Organize heterogeneous capabilities into clear, digestible, glanceable modules.
- **Techniques**:
  - Distinct aspect-ratio containers arranged in an asymmetrical, balanced mosaic.
  - Strong visual containment with subtle border-radius and inner padding harmony.
  - Focus cards with dedicated micro-interactions.
- **QUALITY BAR**: the mosaic encodes a real grouping — modules adjacent because they are
  related, sized because of what they carry. A bento whose tiles would work in any
  arrangement is a card grid with variable spans, and fails the bar.
- **Failure Mode**: Rote layout cloning where content does not naturally fit card boundaries.

### E. Brutalist Code / Monospace (粗野主义/代码原语)
- **Purpose**: Unfiltered, direct communication of system state and data models.
- **Techniques**:
  - Heavy borders (2px solid), stark monochrome palettes with singular utility accents.
  - Monospaced typography for both labels and data.
  - Zero decorative shadows or rounded corners.
- **QUALITY BAR**: the rawness is *systematic* — one border weight, one accent, applied
  without exception. Brutalism that is raw in some places and soft in others is
  unfinished, not brutalist; the vocabulary is a discipline, and the discipline is what
  the reader reads as confidence.
- **Failure Mode**: Deliberate user hostility or unreadable density.

---

## 3. Multi-Direction Physical Slots (探索期槽位)

During Stage 2 exploration, author competing directions into independent physical slots:
```text
prototype/experiments/<slice>/dirs/
├── a/index.html   # Direction A (e.g. Swiss Editorial)
├── b/index.html   # Direction B (e.g. Dense Telemetry)
└── c/index.html   # Direction C (e.g. Bento Modular)
```
Upon human review and selection, promote the chosen direction to `prototype/experiments/<slice>/anchor/index.html`.
