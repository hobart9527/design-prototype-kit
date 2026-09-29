# Modern Style Vocabulary (现代设计风格语汇与反向推导)

Read before proposing or exploring visual directions. This reference replaces rigid aesthetic prohibitions with purposeful, context-driven design vocabularies.

## 1. Scene Reverse-Derivation (场景反向推导器)

Select 2–3 divergent directions based on the authentic operational tension and user context, rather than random stylistic novelty:

| Operational Context & User Need | Primary Vocabulary | Secondary Alternative | Core Tension Resolved |
|---|---|---|---|
| **High-concurrency monitoring, heavy telemetry, domain operations** | Dense Telemetry / Instrument | Data-Ink Minimalist | Scanning speed vs. visual noise |
| **Long-form reading, governance, legal/compliance, technical docs** | Swiss Editorial Grid | Humanist Warm Monochrome | Cognitive fatigue vs. structural hierarchy |
| **Consumer tool, creative workspace, collaborative canvas** | Tactile Neo-Skeuomorphic | Spatial Glass / Ambient | Intuitiveness vs. screen real-estate |
| **Developer utility, infrastructure control, terminal/CLI hybrid** | Brutalist Code / Monospace | Bento Grid Modular | Raw clarity vs. complex state disclosure |
| **Executive analytics, portfolio overview, strategic reporting** | Bento Grid Modular | Swiss Editorial Grid | Summary density vs. presentation polish |

---

## 2. Style Vocabularies & Techniques

### A. Dense Telemetry / Instrument (高密仪表)
- **Purpose**: Maximize information throughput and situational awareness for expert operators.
- **Key Techniques**:
  - Monospace or tabular figures (`font-variant-numeric: tabular-nums`).
  - Micro-grid rhythm (4px/8px baselines, 1px hairline borders).
  - High-contrast status pips (e.g. emerald/amber/crimson against dark or crisp slate voids).
- **Failure Mode**: Cramped, illegible label truncation; lack of visual rest zones.

### B. Swiss Editorial Grid (瑞士/编辑网格)
- **Purpose**: Elevate textual authority and narrative coherence through rigorous typography and asymmetric margins.
- **Key Techniques**:
  - Clear typographic ladder with strong contrast between title measure and body running text.
  - Generous whitespace as functional divider rather than decorative container boxes.
  - Subdued, warm paper background tones with rich ink typography.
- **Failure Mode**: Rigid refusal to handle dynamic data; text overflowing fixed grid containers.

### C. Tactile Neo-Skeuomorphic (温和触感)
- **Purpose**: Create immediate physical affordance and sensory delight in interactive controls.
- **Key Techniques**:
  - Realistic `:active` press detents and micro-elevations.
  - Concentric radii ($R_{in} = \max(0, R_{out} - P)$) for natural nested containment.
  - Multi-stop soft ambient drop shadows without harsh neon glow.
- **Failure Mode**: Visual bloat, excessive gradients distracting from content.

### D. Bento Grid Modular (Bento 模块化)
- **Purpose**: Organize heterogeneous capabilities into clear, digestible, glanceable modules.
- **Key Techniques**:
  - Distinct aspect-ratio containers arranged in an asymmetrical, balanced mosaic.
  - Strong visual containment with subtle border-radius and inner padding harmony.
  - Focus cards with dedicated micro-interactions.
- **Failure Mode**: Rote layout cloning where content does not naturally fit card boundaries.

### E. Brutalist Code / Monospace (粗野主义/代码原语)
- **Purpose**: Unfiltered, direct communication of system state and data models.
- **Key Techniques**:
  - Heavy borders (2px solid), stark monochrome palettes with singular utility accents.
  - Monospaced typography for both labels and data.
  - Zero decorative shadows or rounded corners.
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
