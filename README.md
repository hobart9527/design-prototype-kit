# Design Prototype Kit (v10.2)

> **AI Product Design Operating Harness** — An industrial-grade framework for high-craft experience design decisions, sealed contract specifications, and empirical prototype validation.  
> **工业级 AI 产品体验设计决策与原型验证线束** — 贯穿真实物理世界锚点、九柱设计本体、五轴知觉校准、机器契约无损编译与多视口客观评测的现代设计交付流水线。

---

[中文说明](#中文说明) | [English Documentation](#english-documentation)

---

<a name="中文说明"></a>
# 中文说明

## 1. 核心设计哲学 (Core Philosophy)

`design-prototype-kit` 不是一套简单的“生成界面用的 Prompt”，而是一套面向大模型时代、具备现代 P9+ 资深设计专家裁决水准的**产品设计操作系统（Design Operating Harness）**。其底层遵循三大不可动摇的因果律：

1. **规约即持久权威，原型即耗材凭据 (Spec as Durable Contract, Prototype as Disposable Proof)**
   - 设计决策必须沉淀为具备法律级确定性的契约文件（`product.md`, `m1.md`, `f1.md`, `t1.json`, `c1.md`, `r1.md`）；
   - 代码原型不是资产终点，而是验证关键假设、暴露交互死角与视口应力的低成本耗材。
2. **物理因果推导自然结果，拒绝套路标签 (Physical Grounding over Rigid Archetypes)**
   - 杜绝“为了做阅读器就必须找现成套路”的模板化病灶；
   - 沿 **现实世界物理锚点 ──► 介质物性 ──► 九柱解构 ──► 双钻收敛 ──► 自然样式** 推导。通过排版测度（Measure）、视网膜对比、容器亲疏度（Container Proximity）自然导出界面，而不是生搬硬套死板的组件框架。
3. **知觉后果先于绝对数值 (Perceptual Consequences over Rigid Recipes)**
   - 彻底废除“密 = 4px，静 = 150ms”的死板配方；
   - 将五轴寄存器（密度/能量/材质/节奏/性格）作为感官知觉意图传导给 Builder，由其结合真实视口上下文行使专业设计裁决权。

---

## 2. 核心架构模型 (Canonical Design Operating Model)

系统由 **1 个设计本体 + 3 个辅助模型 + 1 套证据治理协议** 构成：

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 1. Nine Pillars (WHAT WE DESIGN — 唯一设计本体)                                   │
│    Value · Research · Object · Journey · Topology · Attention · Expression ·    │
│    Interaction · Resilience                                                      │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. Double Diamond (HOW WE DECIDE — 决策发散与收敛)                                │
│    Problem Space (Discover ──► Define) ──► Solution Space (Develop ──► Deliver)  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. Five Axes (HOW IT FEELS — 知觉坐标寄存器)                                      │
│    Density (密/疏) · Energy (动/静) · Materiality (质感底噪) · Rhythm · Character │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 4. Craft Library (HOW WE CRAFT — 专业工法库)                                     │
│    OOUX 实体生命周期 · 容器亲疏阶梯 · 认知借贷收支账本 · 4-Phase 动词状态机 ·      │
│    四维破坏协议 (The Break Protocol)                                             │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 5. Evidence Protocol (横向防伪造治理)                                            │
│    显式标注来源与确信度 (`explicit` | `derived` | `hypothesis`)，彻底绝罚臆造      │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 五阶工序状态机 (Canonical 5-Stage Workflow)

流水线严格依照五阶状态机演进，杜绝未经思考直接跳向写代码的平庸倾向：

```text
[Stage 1: 破 - Understand & Frame]
 └─ 解构核心张力 (Core Tension)，确立 OOUX 实体，推导表面拓扑，OKLab 编译 DTCG tokens，物化 Sealed Provisional Spec 契约。
     │
     ▼ (门禁质检：lint_spec_contracts.py 拦截张力污染与空壳)
[Stage 2: 立 - Proposition & Hero Probe]
 └─ 自动装配确定性机器信封 (envelope.json)，派发 Builder 单道物化最高风险 Hero Anchor 页面，真实 Headless 走查。
     │
     ▼
[Stage 3: 拓 - Walking Skeleton Rollout]
 └─ 依据拓扑展开为端到端全链路闭环骨架，保证跨页面相对链接与状态机（如书库断点续读、参数协同）完全贯通。
     │
     ▼
[Stage 4: 验 - Holistic Review & Multi-Viewport Verification]
 └─ 独立 Critic 代理在多视口 (320px, 390px, 768px, 1280px, 1600px) 下运行静态断言与破坏压测，捕获真实视觉证据。
     │
     ▼
[Stage 5: 冻 - Silent Packaging & Handoff]
 └─ 生成交互式全景评审看板 (review-portal.html) 与 SHA-256 签名清册 (handoff-manifest.json)，封版为 Frozen Approved 交付。
```

---

## 4. 消除三轨断层：双信封契约编译架构 (Dual-Envelope Protocol)

为了杜绝“思考是一套、契约写一套、大模型代码瞎编一套”的传统弊端，系统实现了绝对单向无损的编译传导：

- **L0 讨论层 (`discussion.md`)**：人类与 AI 探讨高阶价值冲突、现实隐喻与张力取舍。
- **L1 契约物化 (`materialize_contracts.py`)**：格式化沉淀为包含真实实体表、专属断言与语种锁定的 6 根契约支柱。
- **L1.5 防逃逸门禁 (`lint_spec_contracts.py`)**：硬核校验张力真实性、现实因果、语种锁与断言完备性。
- **L2 机器信封 (`assemble_envelope.py`)**：单向编译为单一事实源 `envelope.json`，严格解耦为：
  - `constraint_envelope` (MUST)：业务边界、实体基数、语种硬锁定、无障碍底线。
  - `creative_envelope` (DESIGN FREEDOM)：五轴知觉坐标、排版节奏、视线引导层级。
- **L3 终端执行 (`spec-prototype-builder`)**：Builder 仅读单一权威信封，不再翻阅散文文档，执行转译零摩擦。

---

## 5. Golden Benchmark 自动化评测线束

仓库内置工业级自动化基准评测矩阵（`benchmarks/`），在 4 个完全正交的领域用例上实施无先验盲测：

| 用例名称 (Case ID) | 领域定位与物理张力 | 核心考量与防退化断言 |
|---|---|---|
| `approval-workflow` | B 端高密企业采购审批台 | 防重复审批、金额敏感防误操作、标准表单与审计轨迹 |
| `editorial-reader` | C 端万字沉浸长文阅读器 | 65-72ch 纸墨测度、暖米纸底色、零弹窗阻断、划词边注、断点续读 |
| `incident-commander` | 专业级 SRE 集群故障控制台 | 秒级排空防误杀、时序遥测微火花线、不可逆操作确认、高频键盘工效 |
| `mobile-booking` | 移动触控消费级上门预约 | 44px 拇指区、时段并发冲突处理、低认知负荷单手流 |

### 三维客观评判系统 (Judges)
- **Runtime Judge**：100% 审查真实 DOM：Token 继承、行内 Hex 零污染检测、语种文本守恒、相对链接物理连通性。
- **Visual Manifest**：基于 Headless 浏览器采集真实的 320/390/1280 视口多状态渲染截图。
- **Semantic Judge**：LLM 裁判盲审，严防功能虚构（Fabricated Capabilities）与越权封版（Authority Escape）。

---

## 6. 目录结构

```text
design-prototype-kit/
├── agents/                       # Builder 建造者与 Critic 评审者提示词契约
├── benchmarks/                   # 自动化基准评测系统
│   ├── cases/golden/             # 4 个正交领域的金标测试案例与反事实规则
│   ├── judges/                   # 运行时机制、语义防逃逸、视觉证据裁判器
│   └── runners/                  # 矩阵运行器、会话驱动器与基线冻结工具
├── skills/spec-prototype/        # Canonical 5-Stage 核心设计引擎
│   ├── references/               # 01基础 / 02工法 / 03质检 / 04治理 规范库
│   ├── templates/                # 契约模版 (product, surface, foundation, tokens, slice, spec)
│   └── scripts/                  # 核心编译器 (materialize, compile_tokens, assemble, lint)
└── tests/                        # 完整的自动化测试套件 (59+ passed)
```

---

## 7. 快速开始与命令指引

### 运行全量测试
```bash
python3 -m pytest tests/ -v
```

### 契约物化与自动化信封组装
```bash
# 物化当前 slice 契约并自动装配 baseline envelope.json
python3 skills/spec-prototype/scripts/materialize_contracts.py --slice <slice_id>

# 编译 OKLab DTCG 设计系统 Token 样式表与 JSON
python3 skills/spec-prototype/scripts/compile_tokens.py --slice <slice_id>
```

### 执行 Stage 1 契约完整性防逃逸质检 (Linter)
```bash
python3 skills/spec-prototype/scripts/lint_spec_contracts.py --slice <slice_id>
```

### 执行 Golden Benchmark 评测
```bash
# 针对单一案例跑 candidate_skill 与稳定基线对比
python3 benchmarks/runners/run_case.py --case editorial-reader --variant candidate_skill --repeat 1 --matrix-dir benchmarks/results/golden-run

# 跑整套日常/全量评测矩阵
python3 benchmarks/runners/run_matrix.py --suite golden --repeats 1 --visual
```

---

<a name="english-documentation"></a>
# English Documentation

## 1. Core Philosophy

`design-prototype-kit` is not a loose set of UI generation prompts. It is an **AI Product Design Operating Harness** engineered to match the discernment, rigor, and craft of a Principal Experience Designer (P9+). Its foundation rests on three immutable principles:

1. **Spec as Durable Contract, Prototype as Disposable Proof**
   - Design convictions must be crystallized into unambiguous, sealed contract files (`product.md`, `m1.md`, `f1.md`, `t1.json`, `c1.md`, `r1.md`).
   - Code prototypes are not precious final assets; they are disposable, low-cost instruments for falsifying hypotheses and exposing interaction stress under real viewports.
2. **Physical Grounding over Rigid Archetypes**
   - Reject dogmatic classification silos (e.g., forcing products into artificial "archetype boxes").
   - Follow the causal derivation: **Reality Anchors ──► Physical Substrate ──► Nine Pillars ──► Double Diamond ──► Natural Outcomes**. Typography measure, contrast ratios, and container proximity emerge organically from the domain's physical realities.
3. **Perceptual Consequences over Rigid Recipes**
   - Eliminate robotic rules like "density must be 4px" or "quiet motion must be <=150ms".
   - Treat the Five Axes (Density, Energy, Materiality, Rhythm, Character) as sensory intentions, granting the Builder agent professional judgment to synthesize styles appropriate to the viewport and medium.

---

## 2. Canonical Design Operating Model

The architecture unites **1 Core Ontology + 3 Auxiliary Frameworks + 1 Transverse Governance Protocol**:

- **Nine Pillars (WHAT WE DESIGN)**: Value · Research · Object · Journey · Topology · Attention · Expression · Interaction · Resilience.
- **Double Diamond (HOW WE DECIDE)**: Divergent exploration and convergent decision-making across Problem and Solution spaces.
- **Five Axes (HOW IT FEELS)**: Perceptual coordinate calibration: Density, Energy, Materiality, Rhythm, and Character.
- **Craft Library (HOW WE CRAFT)**: Decoupled general experience invariants (OOUX lifecycle, Container Proximity Ladder, Cognitive Ledger, The Break Protocol) and candidate craft techniques.
- **Evidence Protocol (GOVERNANCE)**: Universal authority provenance (`explicit` | `derived` | `hypothesis`), eradicating speculative hallucinations.

---

## 3. Canonical 5-Stage Workflow

The delivery engine advances through an adaptive, 5-stage state machine:

- **Stage 1: 破 (Understand & Frame)**: Unpack the Core Tension, map genuine OOUX domain entities, derive surface topology, project OKLab DTCG tokens, and seal provisional baseline contracts.
- **Stage 2: 立 (Proposition & Hero Probe)**: Compile the deterministic machine envelope (`envelope.json`) and dispatch a bounded Builder to materialize the highest-risk Hero Anchor surface.
- **Stage 3: 拓 (Walking Skeleton Rollout)**: Expand the probe into an interconnected multi-surface walking skeleton, proving end-to-end task continuity and anchor restoration.
- **Stage 4: 验 (Holistic Review & Verification)**: Run independent Critic verification across 5 standard viewports (320px to 1600px) against domain assertions and The Break Protocol stress vectors.
- **Stage 5: 冻 (Silent Packaging & Handoff)**: Render the multi-viewport review portal (`review-portal.html`), sign the SHA-256 integrity manifest (`handoff-manifest.json`), and freeze the approved delivery.

---

## 4. Seam Elimination: The Dual-Envelope Protocol (v2.0)

To resolve traditional handoff friction between high-level reasoning and terminal agent execution, the harness implements a zero-loss compilation pipeline:

- **L0 Discussion (`discussion.md`)**: Free-form cognitive negotiation between human and AI on tradeoffs and domain tensions.
- **L1 Spec Contracts (`materialize_contracts.py`)**: Structured Markdown and YAML frontmatter capturing domain entities, language locks, and test assertions.
- **L1.5 Contract Linter (`lint_spec_contracts.py`)**: Strict gate checking for authentic tensions, reality anchors, language locks, and break protocol coverage.
- **L2 Machine Envelope (`assemble_envelope.py`)**: Deterministic projection into `envelope.json`, strictly separated into:
  - `constraint_envelope` (MUST): Non-negotiable boundaries, state machines, entity tables, and a11y floors.
  - `creative_envelope` (DESIGN FREEDOM): Five-Axis sensory coordinates, attention routing, and visual rhythm.
- **L3 Terminal Execution (`spec-prototype-builder`)**: Builder reads only the single-source envelope, completely unburdened by multi-file prose interpretation.

---

## 5. Automated Golden Benchmark Harness

The repository includes a comprehensive, empirical benchmark harness (`benchmarks/`) featuring 4 orthogonal domain golden cases:

- **`approval-workflow`**: High-density enterprise SaaS procurement; idempotent commits, duplicate-approval prevention, audit trails.
- **`editorial-reader`**: Immersive long-form sanctuary; 65-72ch measure, warm paper substrate, zero modal interruptions, margin annotations, scroll-detent resumption.
- **`incident-commander`**: High-frequency SRE cluster console; safe drain confirmations, telemetry micro-sparklines, keyboard ergonomics.
- **`mobile-booking`**: Consumer mobile touchflow; 44px thumb-zone detents, optimistic conflict recovery, low-cognitive burden.

### Three-Dimensional Evaluation Judges
- **Runtime Judge**: Validates CSS token inheritance, zero inline hex violations, content-language fidelity, and physical relative-link resolution.
- **Visual Manifest**: Headless browser captures cross-viewport screenshots at 320px, 390px, and 1280px.
- **Semantic Judge**: Blind LLM evaluation enforcing anti-fabrication gates and blocking unauthorized status promotions.

---

## 6. Repository Layout

```text
design-prototype-kit/
├── agents/                       # Builder and Critic agent prompt contracts
├── benchmarks/                   # Automated benchmarking harness
│   ├── cases/golden/             # 4 orthogonal golden cases and counterfactual events
│   ├── judges/                   # Runtime, semantic, task, and visual judges
│   └── runners/                  # Suite orchestrator and session runners
├── skills/spec-prototype/        # Canonical 5-Stage design delivery skill
│   ├── references/               # 01-foundations, 02-craft, 03-verification, 04-governance
│   ├── templates/                # Contract templates (product, m1, f1, t1, c1, r1)
│   └── scripts/                  # materialize, compile_tokens, assemble, lint_spec
└── tests/                        # Full regression and integrity suite (59+ tests)
```

---

## 7. Quickstart

```bash
# Run all automated tests
python3 -m pytest tests/ -v

# Materialize Stage 1 contracts and auto-assemble envelope
python3 skills/spec-prototype/scripts/materialize_contracts.py --slice <slice_id>

# Run contract completeness linter
python3 skills/spec-prototype/scripts/lint_spec_contracts.py --slice <slice_id>

# Run a single Golden Benchmark case
python3 benchmarks/runners/run_case.py --case editorial-reader --variant candidate_skill --repeat 1 --matrix-dir benchmarks/results/golden-run
```

---

## License

MIT License. Copyright (c) 2026 design-prototype-kit authors.
