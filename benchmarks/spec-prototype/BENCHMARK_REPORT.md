# spec-prototype v10.1 全生命周期基准评测报告 (Evidence & Benchmark Report)

## 一、评测综述 (Executive Summary)

- **基准套件版本**：v10.1 (Evidence-Driven Design Harness)
- **评测模式与分层**：
  - **Layer A (Pipeline & Compiler)**: 100% 跑通。编译、Token 生成、Dual-Envelope 组装与 headless 截图链路全绿。
  - **Layer B (Static Signal Coverage)**: 静态 Linter 规则覆盖度。
  - **Layer C (Browser & DOM Tracing)**: 真实 Chromium 截图生成（320px, 390px, 1280px）。
  - **Layer D (Visual & Human Review)**: 显式标记为 `pending_review`，不以机器打分假冒设计验收。
- **覆盖案例**：6 大基准案例（`incident-commander`, `editorial-reader`, `mobile-booking`, `project-workspace`, `product-marketing`, `ai-writer-workspace`）。
- **自动化测试回归**：`pytest tests/` **59/59 passed** (100%)。逐字快照见文末「测试快照」段。
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

---

## 五、证据边界（Evidence Boundary）

上表全部 PASS 来自无头环境下的机器断言，其证据范围止于**结构与 Token 层**，不构成对成品质感的担保。

### 已测（In Scope）
- **Pipeline / 契约固化 / Token 编译**：上表各列 PASS 覆盖，重复 3 轮。
- **静态信号覆盖度**：物理工法规范、Token 继承、Tabular 格式的 Linter 规则命中率。
- **截图生成**：真实 Chromium 渲染产出 PNG，320 / 390 / 1280px 三档视口。
- **WCAG AAA 对比度**：以 Token 数值计算，非渲染采样。

### 未测（Out of Scope / 未测）
- **未测**人工可用性与视觉评审：无设计师或目标用户参与，`视觉与设计评定` 一列全部为 `pending_review`。
- **未测**响应式断点与交互时序：截图覆盖三种视口宽度，但不含交互状态与转场时序验证。
- **未测**跨浏览器与跨平台差异：单一沙箱环境，无 Safari / Firefox / Windows 对照。
- **未测**性能上界：流水线耗时不含渲染、网络与冷启动。
- **未测**生成物语义正确性：编译链只保证结构合规，不判断文案、信息架构或产品意图是否恰当。

### 截图证据边界
- `renderer: captured` 仅证明浏览器成功渲染并落盘 PNG，**不**证明设计质量通过。
- 视觉与设计评定在独立 Critic 与设计师完成评审前，一律保持 `pending_review`。
- 不得以截图张数声明设计质量达标。

---

## 六、测试快照

- **命令**：`python3 -m pytest tests/ -q`
- **执行日期**：2026-09-19
- **环境**：单沙箱，无浏览器，无 Skill 会话入口。
- **实际输出**（逐字摘录，未改写、未补跑）：

```text
59 passed, 1 warning in 0.71s
```

- stderr 同时出现 `RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.6.0)/charset_normalizer (3.4.7) doesn't match a supported version!`，属解释器依赖噪声，与本测试结果无关。
- **快照边界**：`59 passed` 是**契约与机制层断言**的成功计数，全部为脚本产物与夹具输入的机器比对；不含 Builder 派发、浏览器任务操作、页面交互或人工设计评分。该快照**不得**读作「spec-prototype 交付能力通过」。
- 本快照为一次性采集。测试文件后续被修改时，本段不追溯更新，须另立快照。

### 历史快照对照（已失效，仅存档）

- **命令**：`python3 -m pytest tests/test_pipeline.py -q`
- **执行日期**：2026-09-18，输出 `21 passed in 0.23s`。
- **状态**：**已失效**。该数字对应已归档的机制层驱动时代；测试集此后扩容至 59 项，本报告不再以 `21 passed` 或早期误写的 `32/32` 作为当前回归证据。

---

## 七、首期缺陷责任归因矩阵

矩阵将探查已确认的事实逐项落到**首次责任偏离层**，避免把跨层症状归因到单一所有者。归因依据为交付复盘（`docs/retrospectives/2026-09-17-spec-prototype-delivery-retrospective.md`）与本轮只读调查；不含推测性比例。

| # | 已确认事实 | 首次责任偏离层 | 归因判定 | 证据边界 |
|---|---|---|---|---|
| 1 | 完整 `agent_tool_inputs` 被手工重写，指定执行器被替换 | Host 派发适配层 | Coordinator 越过适配边界，派发身份不是原样消费 | 直接记录；对耗时的贡献未计量 |
| 2 | 机制层全绿被当作交付成功 | 基准报告 / runner 层标签 | 缺少真实 Builder 派发，机制成功被跨层表述为交付成功 | 已由 L2/L3 `blocked` 修正 |
| 3 | 报告曾以「100% 通过率」作总体结论 | 基准报告作者层 | 虚报通过率：分母仅覆盖机制层，交付/交互/人工质量未测 | 已撤回，见上方证据边界 |
| 4 | `tests/test_pipeline.py` 断言与夹具字面值耦合 | 测试器层 | 硬编码断言：绿只证明夹具与实现自洽，不构成行为证据 | 见上方测试快照 |
| 5 | 审批调用 actor-type `user` 被拒、改 `human` 后通过 | 审批适配层 | 参数被接受不等于存在对应 revision 的真实人工批准 | 直接记录；授权覆盖面未取证 |
| 6 | Leaf 自述测试通过，Host 独立复验失败 | Leaf 结果报告层 | 局部修复提前上交，自述不能替代工具事实 | 失败快照已保留 |
| 7 | Hook 拒绝仅返回 `BOUND_RELEASE_UNAVAILABLE:<ErrorClass>` | Hook/release 路由层 | 启动诊断被压缩，底层 reason 未送达，无法按原因恢复 | 源码调查；历史 reason 未知 |
| 8 | 某 Task 的验证依赖后置 Task 才拥有的测试修改权 | OpenSpec 任务编制层 | 行为与测试闭包被拆开，Task 不可独立验证 | 已由验证命令收窄与测试所有权调整缓解 |

**矩阵使用约束**：以上归因只指向已观察到的首次偏离位置。任何修复须先对上表某一行的证据，不得据个案偏好新增全局设计禁令。跨层记录禁止并入同一对比表，不得由本矩阵推导整体通过率或提升百分比。
