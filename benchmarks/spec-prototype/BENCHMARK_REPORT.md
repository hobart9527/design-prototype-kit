# spec-prototype v10.1 全生命周期基准评测报告 (Evidence & Benchmark Report)

## 一、评测综述 (Executive Summary)

- **基准套件版本**：v10.1 (Evidence-Driven Design Harness)
- **评测模式与分层**：
  - **Layer A (Pipeline & Compiler)**: 100% 跑通。编译、Token 生成、Dual-Envelope 组装与 headless 截图链路全绿。
  - **Layer B (Static Signal Coverage)**: 静态 Linter 规则覆盖度。
  - **Layer C (Browser & DOM Tracing)**: 真实 Chromium 截图生成（320px, 390px, 1280px）。
  - **Layer D (Visual & Human Review)**: 显式标记为 `pending_review`，不以机器打分假冒设计验收。
- **覆盖案例**：6 大基准案例（`incident-commander`, `editorial-reader`, `mobile-booking`, `project-workspace`, `product-marketing`, `ai-writer-workspace`）。
- **自动化测试回归**：`pytest` **32/32 passed** (100%)。
- **设计品味评分（Taste Score）状态**：**已彻底废弃 (Deprecated in v10.1)**。拒绝将机器规则覆盖度伪称为设计质量总分。

---

## 二、评测分层与证据诚信状态 (Benchmark Layering & Evidence Protocol)

| 评估层级 (Layer) | 验证标的 | 验证手段 | 当前状态 | 证据诚信说明 |
|---|---|---|---|---|
| **Layer A: Pipeline Integration** | 编译器、信封组装、语法与断言执行 | 自动化 Pipeline 驱动 | **PASS** | 验证系统各环节无异常退出与断裂。 |
| **Layer B: Signal Coverage** | 物理工法规范、Token 继承、Tabular 格式 | `evaluate_design_signals.py` | **PASS (100%)** | 仅证明结构与 Token 约束被满足，不代表设计优秀。 |
| **Layer C: Browser Viewport Tracing** | 响应式断点 (320/390/1280px) 视觉抓取 | Headless Chromium (`capture.mjs`) | **CAPTURED** | 证明外观已真实渲染生成，截图存于 `prototype/evidence/`。 |
| **Layer D: Independent Visual & Critic** | 产品真实感、信息架构质量、交互流畅度 | 独立 Critic Agent / 人工评审 | **PENDING_REVIEW** | 严格区分机器抓取与设计评审，严禁自动声明 100% Verified。 |

---

## 三、各案例详细度量数据 (Benchmark Execution Data)

| 案例名称 | 产品类型 | Pipeline 状态 | Stage 1 契约固化 | Stage 2 原型构建 | 截图生成 (PNG) | 静态信号覆盖度 | 视觉与设计评定 |
|---|---|---|---|---|---|---|---|
| `incident-commander` | 运维事件处置台 (Dense Workbench) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |
| `editorial-reader` | 深度长文阅读 (Editorial Reading) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |
| `mobile-booking` | 移动服务预约 (Touchflow Mobile) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |
| `project-workspace` | 项目协作工作台 (Operational Canvas) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |
| `product-marketing` | 现代营销官网 (Marketing Showcase) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |
| `ai-writer-workspace` | AI 协同写作区 (Adaptive Workspace) | OK | PASS | PASS | 9 张 (320/390/1280px) | 100.0% | `pending_review` |

---

## 四、v10.1 核心演进与治理收敛 (Evolution & Governance)

1. **证据真实性 (Evidence Honesty)**：
   - 移除所有虚构的“品味分 100/100”与“视觉 100% Verified”盲目乐观声明；
   - 确立 `renderer: captured` 与 `visual: pending_review` 的解耦，把最终体验裁决权交还给独立 Critic 与设计师。
2. **解耦单一控制台基线偏见 (Composable Context)**：
   - 移除 `else: dense-console` 暴力兜底，写作与阅读类原型拥有专属的 `adaptive-workspace` 构图空间，避免被强加无关的运维指标微图。
3. **业务语义防伪造 (Product Meaning Safety)**：
   - 编译器对未在原始 Source 声明的操作行为统一归类为 `[Hypothesis]`，禁止根据关键词自动脑补支付、履约等硬性业务事实。
