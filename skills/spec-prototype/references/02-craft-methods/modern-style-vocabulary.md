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

### F. Magazine Spread / Editorial Rhythm (杂志跨页)
- **Purpose**: Pace attention across a surface the way a spread paces a reader: entry, rest, payoff.
- **Techniques**:
  - Scale jumps (a very large display element against small running text) with a deliberate empty field around it.
  - Captions, running heads and pull quotes as navigation, not decoration.
  - Asymmetric columns where one column carries the argument and the other the evidence.
- **QUALITY BAR**: a reader can say where to start and where the surface rests. Large type
  that does not mark an entry point, or a pull quote that repeats nearby text, fails the bar.
- **Failure Mode**: Display type applied to data-heavy surfaces that need scanning, not pacing.

### G. Instrument Label / Industrial Marking (工业标签)
- **Purpose**: Make state and ownership legible at a glance through the conventions of labelled hardware.
- **Techniques**:
  - Stencil-like or condensed uppercase labels, ruled legends, numbered positions.
  - One signal colour per meaning, always paired with a text or shape cue.
  - Physical states named as hardware names them (armed, locked, seated).
- **QUALITY BAR**: every label names something that exists in the product. Decorative
  hazard stripes, serial-number texture or fake barcodes fail the bar.
- **Failure Mode**: Costume hardware on a product with no real physical referent.

### H. Drafting Sheet / Architectural Plan (图纸)
- **Purpose**: Show structure and relationship by drawing it, with dimensions and annotation as first-class content.
- **Techniques**:
  - Hairline construction lines, callouts with leader lines, title-block metadata.
  - Orthogonal geometry; scale and unit shown rather than implied.
  - Monochrome with a single revision colour.
- **QUALITY BAR**: the drawing explains something the prose does not. Grid lines or
  callouts that restate visible labels fail the bar.
- **Failure Mode**: Technical-drawing texture over content that has no spatial structure.

### I. Title Sequence / Cinematic Frame (影像字幕)
- **Purpose**: Use time and framing to stage a single decisive moment.
- **Techniques**:
  - Letterboxed or full-bleed frames, one subject per frame, deliberate reveal order.
  - Timing as hierarchy: what appears first is what matters first.
  - Restrained motion with a clear hold, never continuous loops.
- **QUALITY BAR**: removing the motion would lose information (order, causality, emphasis).
  Motion that only adds energy fails the bar; `prefers-reduced-motion` keeps the order.
- **Failure Mode**: Cinematic staging on task flows where speed is the value.

### J. Letterpress / Print Craft (活版印刷)
- **Purpose**: Convey care and permanence through the evidence of a made, inked surface.
- **Techniques**:
  - Impression and ink-spread cues limited to a single material layer; rule lines and ornaments from a fixed set.
  - Paper-toned neutrals, two inks at most, tight tracked small caps.
  - Figures and indices set as tables with real rules.
- **QUALITY BAR**: the material cue is applied to one layer and is consistent with how
  the content is used. Texture across every surface, or noise filters on text, fails the bar.
- **Failure Mode**: Nostalgia pastiche that lowers legibility and contrast.

### K. Physical Material Behavior / Haptic Surface (物性响应)
- **Purpose**: Let controls behave like what they are made of, so state is felt in the motion.
- **Techniques**:
  - Resistance, snap and settle curves chosen per material (detent, spring, damped slide).
  - Pressed, seated and locked states that differ in travel and shadow, not only colour.
  - Sound or haptic cues named in the spec when the platform supports them.
- **QUALITY BAR**: two different controls never share one generic transition; each
  material has a stated reason. Uniform ease-in-out on everything fails the bar.
- **Failure Mode**: Springy motion on safety-critical confirmations that need to feel deliberate.

### Sampling rule
Draw challengers without replacement (`draw_seed.py`); when drawing by hand, pick the
entry least compatible with the candidate's lifeworld rather than the nearest, then fuse
only its *technique*. A challenger that makes the candidate look like its own category's
default has failed and is refused with the reason recorded.

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
