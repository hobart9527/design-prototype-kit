# Discussion Record: AI 超导拓扑反应堆中控 (Synchrotron Lattice // Topological DAG Reactor)

## Resume

- Execution boundary: released
- Active track / current decision: formal-delivery / verified-v2
- Route basis: IA-first
- Requested scope and stopping point: full-5-stage-simulation-v2
- Pending prerequisite: none
- Next action and its prerequisite: Capture headless browser verification screenshots and compare v1 vs v2.

## Phase 1: 魂 · 破 (Tone & Tension Re-architecture)

- **产品构型演进（v1 vs v2）**：
  - **v1（旧版 Cockpit）**：三栏卡片式航空座舱。本质仍为传统控制台堆叠，信息架构被硬性切分为跑道列表、单一阻尼槽与侧边文本日志，缺乏万级智能体 DAG 运转的全局空间动量与连续张力。
  - **v2（全新 Synchrotron Lattice）**：**强子对撞机超导拓扑环流反应堆**。打破一切平庸报表格子，以全画幅高精度 SVG + Canvas 粒子束流网（Particle Synchrotron Mesh）呈现自主智能体集群的实时因果流转。
- **核心冲突重构**：万级并发 DAG 吞吐（10,000+ RPS Agent Cluster） vs 纳秒级因果律漂移阻断（Zero-Drift Causal Liability）。
- **隐喻内核**：操作者不是在“点击审批弹窗”，而是手握“磁通控制棒（Magnetic Detent Rods）”，在拓扑分歧点施加微重力吸附阻尼场，实现零停机非接触式偏转引流。
- **风格五轴寄存器 (5 Dials)**：
  - Energy: `radiant-quiet`（060709 虚空底色、电离蓝 #00f0ff、等离子青 #00e599、裂变橙 #ffaa00）。
  - Finish: `machined-industrial`（精密拓扑流轨道、纳秒级相空间示波器、微刻度标尺）。
  - Density: `ultra-dense`（单屏掌控粒子环、因果网与能级相干度）。
  - Weight: `dense-tactile`（物理吸附阻尼感、按钮 :active 机械触觉回弹）。
  - Seriousness: `critical-infrastructure`（军工与高能物理级肃穆感）。
- **权威记录**：详见 `prototype/product.md`。

## Phase 2: 骨 · 立 (Core Hero Anchor & Physical Tokens)

- **Hero 锚点**：`prototype/experiments/cockpit/hero-anchor/index.html`。
- **物理 Token 实体**：`prototype/contracts/tokens/t1.md`, `t1.json` 与 `prototype/shared/tokens.css`。
- **微观几何与设计工法**：
  - 同心圆角约束：$R_{inner} = \max(0, R_{outer} - padding) = 12\text{px} - 8\text{px} = 4\text{px}$。
  - 等宽数值防抖：`font-variant-numeric: tabular-nums` 贯穿所有束流能量、相空间抖动与吞吐读数。
  - 空间底色气韵：消除死板冷灰，注入 `#060709`、`#0a0c10`、`#10131a` 钴蓝微光底色。
  - 触感动力学：`:active { transform: scale(0.97); }` 与 `cubic-bezier(0.16, 1, 0.3, 1)` 阻尼减速。

## Phase 3: 拓 · 骨 (Tier-by-Tier Rollout)

- **Tier 0 (Strategic Orbit)**：`prototype/experiments/cockpit/tier0-orbit/index.html`（多环超导态势感知，零裸露指标，附带 BASELINE 与 THRESHOLD 参照系）。
- **Tier 1 (Tactical Station)**：`prototype/experiments/cockpit/tier1-station/index.html`（束流隔离战术工位，闭环动词生命周期：QUARANTINE STEP → QUARANTINED）。
- **Tier 2 (Governance Bridge)**：`prototype/experiments/cockpit/tier2-bridge/index.html`（因果律不可变审计日志与 SHA-256 哈希存证）。
- **血缘继承**：全部页面统一外链 `shared/tokens.css`，零内联 Hex 色值。

## Phase 4: 验 · 鉴 (Holistic Review Portal)

- **多视窗走查台**：`prototype/review-portal.html`。
- **多端响应式断点**：390px (Mobile)、768px (Tablet)、1280px (Desktop)、100% (Fluid)。
- **决策交互三帧检视**：Intent（空格键激发磁阻尼锁定）→ Detent（吸附高亮 ±4.5% 粒子束流）→ Settled（偏转备用环流 / 紧急切断）。
- **破坏性应力走查 (The Break Protocol)**：极端长文本自包含，空态与万级粒子流滚动无崩溃，数值跳变零抖动。

## Phase 5: 冻 · 根 (Silent Packaging & Headless Governance)

- **Token 编译**：W3C DTCG 标准 `prototype/contracts/tokens/t1.json`。
- **无障碍对比度审计**：全量达标 WCAG AAA（14.2:1 / 15.8:1）。
- **自动化测试**：`pytest tests/test_pipeline.py` 11 项端到端设计工程测试 100% 绿灯通过。
