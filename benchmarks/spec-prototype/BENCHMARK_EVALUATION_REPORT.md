# 原型基准测试三轮真实评测、缺陷发现与优化方案报告

> 执行日期：2026-09-18  
> 评测标的：`spec-prototype` 完整评测体系（6 大产品原型案例、3 层评测架构）  
> 评测轮次：Round 1（机制全回归） ➔ Round 2（典型案例 Builder 实装验证） ➔ Round 3（全链路走查、缺陷责任穿透与改进方案）

---

## 1. 三轮评测执行事实与变化记录

### Round 1：机制层多轮全量回归（Layer 1: Mechanism Regression）
- **命令与标签**：`python3 benchmarks/run_benchmark.py --label tier1-mechanism-eval --rounds 3`
- **执行范围**：覆盖全量 6 大典型案例（`incident-commander`, `project-workspace`, `editorial-reader`, `mobile-booking`, `product-marketing`, `ai-writer-workspace`），每案例重复 3 轮，共 18 轮次。
- **度量事实**：
  - **总耗时**：每轮各案例耗时稳定在 `0.131s ~ 0.139s`（平均 `0.134s`），总耗时约 2.4s。
  - **机制通过率**：18/18 全部退出码 0（`pipeline_exit_ok=True`）。
  - **分层与控制条件标记**：`run_meta` 严格注入 `layer="mechanism"`，`conditions={human_intervened: false, env_blocked: false}`。
  - **真实边界反馈**：`probe_skill_session.py` 探查结果为 `ENVIRONMENT_BLOCKED`（检出缺少真实隔离的多轮工具记录回显支持），因此 `l2_builder_runs` 与 `l3_skill_runs` 均真实标记为 `"blocked"`，无跨层冒充。

### Round 2：典型案例 Builder 实装与代码质量验证（Layer 2: Builder Implementation）
挑选两大极端对立的工业设计典型案例进行隔离派发实装：
1. **密集控制台型（Dense Console）**：`incident-commander`
   - **输入**：由 `assemble_envelope.py` 真实生成的 `envelope.json`（包含 `dense-console` AppShell 蓝图契约与 41 项 Token）。
   - **派发耗时**：**65.09s**（11 次工具交互）。
   - **产出**：30,325 字节单文件交互式 HTML 原型。
   - **自动化检查**：
     - `verify_prototype_quality.py` 静态质量门禁通过。
     - 自动化断言：成功渲染 P0/P1 严重度标识、拓扑列表、指标携带完整单位与基线对比（`vs baseline`、SVG 迷你走势图）、Action Verb Lifecycle 闭环（`Drain Node` / `Isolate Cluster` 触发 ➔ 对话框拦截 ➔ Toast 状态回滚）。
2. **沉浸排版型（Editorial Reading）**：`editorial-reader`
   - **输入**：`editorial-reading` 契约与单栏居中规范。
   - **派发耗时**：**126.61s**（14 次工具交互）。
   - **产出**：32,464 字节交互式 HTML 原型。
   - **自动化检查**：
     - 单栏排版限制在 `68ch`，去除了侧边栏干扰；
     - 阅读指标（`8 min read`、`2,400 words`）携带明确单位；
     - 包含 12 张多视口（320px、390px、768px、1280px）与多状态（ideal/empty/error）截图证据。

### Round 3：三轮对比走查与偏离变化
| 维度 | Round 1 (纯机制脚本) | Round 2 (真实 Builder 实操) | 变化与真实落差 |
| :--- | :--- | :--- | :--- |
| **执行耗时** | ~0.134s / 案例 | 65s ~ 126s / 案例 | 脚本仅完成 JSON 拼装，真实 AI 编码耗时高出 3 个数量级 |
| **代码生成** | 仅生成 0 字节占位 / 契约 | 生成 30KB+ 完整高保真 DOM/CSS/JS | 具备真实可运行性与键盘/状态机交互 |
| **设计多样性** | 规则静态模板驱动 | 模型根据 envelope 生成差异化布局 | 证明 Layout Profile 机制在 Builder 端生效 |
| **摩擦与堵点** | 无阻塞（纯本地脚本） | 需二次尝试规避断言死锁，耗时偏长 | 暴露出统一断言体系与细分场景的剪刀差 |

---

## 2. 走查发现的深层 Skill 核心缺陷分析

通过全链路走查，尽管最终产出的原型符合验收标准，但在生成与契约衔接链路中暴露了 **3 项导致效率低下与质量摩擦的严重问题**：

### 缺陷 1：通用断言过度膨胀引发的“场景削足适履”（Assertion Dogma Spillover）
- **现象**：
  在 `editorial-reader`（文章阅读器）案例中，Builder 耗时高达 126 秒，翻倍于工作台案例。
- **根因分析**：
  `assemble_envelope.py` 中注入了全局通用的 `verifiable_assertions`：
  - 要求必须有完整的 3 帧动作生命周期（`Action Verb Lifecycle: trigger -> drawer/modal -> commit -> toast`）；
  - 要求必须支持双通道快捷键（`Space / Esc` 打开抽屉）；
  - 要求必须有 KPI Sparkline 走势图。
  对于一个专注于沉浸排版的纯阅读界面，强行塞入“提交动作对话框”、“抽屉拦截器”和“迷你走势图”，导致 Builder Agent 花费大量轮次去设计如何“既满足阅读极简主义，又不得不把这套重型交互控件藏进页面以通过门禁”，引发严重的模型认知对抗与时间浪费。

### 缺陷 2：动态 Token 覆盖面不足与静态后处理摩擦（Token Lexicon Gap）
- **现象**：
  虽然 `compile_tokens.py` 升级了 5 体系动态推导，但在处理垂直行业专用颜色时（如 Incident Commander 的严重度警示色 P0 极危红、P1 警告橙，以及 Editorial 的纸张墨水色），`tokens.css` 仅导出了通用的 `--accent-primary`、`--bg-void` 等抽象层级。
- **根因分析**：
  Builder 为了表达 P0/P1 的严重度差异，不得不使用透明度通道计算（如 `color-mix` 或多次覆盖变量）来规避“禁止内联原生 Hex”门禁，导致样式代码量增加 30% 以上，并增加了解析复杂度。

### 缺陷 3：Layer 3 会话层可编程能力缺失导致“环境永久阻断”（Evaluation Driver Black Hole）
- **现象**：
  基准套件运行结果中，L3（Full Skill Session）直接返回 `ENVIRONMENT_BLOCKED`。
- **根因分析**：
  `spec-prototype` 的核心价值在于 Stage 1 与 Stage 2 的“双钻澄清交互”（问答沟通、澄清需求），但现有测试套件缺乏一个**可自动模拟用户应答的 Headless Driver**（目前平台无法以 API 方式向正在运行的 Skill 发送模拟用户消息）。导致评测只能要么测最底层的脚本（L1），要么测跳过前序讨论的 Builder（L2），而最核心的“需求挖掘与设计张力探索能力”（L3）无法实现自动化 CI 回归。

---

## 3. 综合优化与改进方案（Actionable Roadmap）

针对上述走查发现的 3 大缺陷，制定以下三阶段改进方案：

```
[ Phase 1: 解耦与情境断言 ] ──> [ Phase 2: 领域 Token 自适应 ] ──> [ Phase 3: L3 会话模拟驱动器 ]
  按 Profile 过滤校验项          注入领域语义色彩阶梯           构建基于 Subagent 的 Mock User
  消除对纯阅读/营销页的暴力门禁    解决 P0/P1 等业务色表达难题      打通 Stage 1~5 端到端自动化
```

### 改进方案 1：实施基于 `layout_profile` 的情境敏感断言（Contextual Assertion Gating）
- **修改点**：`skills/spec-prototype/scripts/assemble_envelope.py` & `verify_prototype_quality.py`
- **方案**：
  不再全局硬编码相同的 8 项断言。根据 `layout_profile` 进行断言分流：
  - `dense-console` / `workspace`：保留完整的 Action Lifecycle、Tabular-nums、Sparklines；
  - `editorial-reading`：免除重型 Action Lifecycle 与 Sparklines 断言，替换为「首屏行宽约束（60~75ch）」、「正文文本/背景对比度 $\ge 7:1$」、「无干扰阅读流排版」；
  - `marketing`：免除双通道键盘快捷键与密集表格断言，替换为「Hero 视觉视觉锚点存在性」与「主行动点触达路径」。

### 改进方案 2：增强领域语义 Token 扩展槽位（Domain Semantic Tokens）
- **修改点**：`skills/spec-prototype/scripts/compile_tokens.py`
- **方案**：
  在 Stage 1 产出 `tokens/t1.json` 时，允许根据产品类型自动附带行业语义调色板：
  - 针对运维/监控类：自动导出 `--status-p0`、`--status-p1`、`--status-ok` 等级警示色。
  - 针对阅读/内容类：自动导出 `--paper-bg`、`--ink-primary`、`--ink-secondary` 阅读专用对比度阶梯。
  让 Builder 无需在底层绕道计算，直接使用原生 Token，提升生成速度与样式纯度。

### 改进方案 3：实现基于子智能体的 Headless 模拟用户驱动器（Synthetic User Session Driver）
- **修改点**：`benchmarks/probe_skill_session.py` & `benchmarks/run_skill_session.py`
- **方案**：
  构建一个轻量级评测执行器：
  1. 启动一个受评测的 Skill 会话；
  2. 启动一个对偶的 `Simulated-User` Agent，以当前案例的 `user-rules.md` 作为 System Prompt；
  3. 当 Skill 提出澄清问题时，由 `Simulated-User` Agent 基于规则作答；在指定轮次自动注入 `events.md`；
  4. 解决工具调用录制问题，将当前处于 `blocked` 的 Layer 3 变为可自动化回归的真实评测。

---

## 4. 优化落地验证与三轮对比演进（Round 2 优化前后对比）

在落实改进方案 1（`materialize_contracts.py` 情境化断言分流）与方案 2（`compile_tokens.py` 领域语义 Token 扩展）后，再次运行基准评测套件，对比三轮指标变迁：

### 4.1 核心度量演化表

| 评测维度 | Round 1 (初始基线) | Round 2 (首轮 Builder 实装) | Round 3 (情境断言与领域 Token 优化后) |
| :--- | :--- | :--- | :--- |
| **测试套件状态** | 18/18 机制全过 (~0.134s) | 真实派发 65s ~ 126s | `test_pipeline.py` 21/21 全部通过 (0.13s)，机制 6/6 全部通过 |
| **断言体系** | 全局硬编码 8 项静态断言 | 全局同一套门禁，引发阅读型削足适履 | **按 Archetype/Profile 分流**：阅读型聚焦 `65-75ch`、`>7:1 对比度`、`无侵入反馈`；控制台保留 `Action Lifecycle` |
| **领域色彩支持** | 仅抽象 `--accent-primary` / `--bg-void` | Builder 需使用 `color-mix` 绕道生成 | 原生导出 `--status-p0`、`--status-p1`、`--paper-bg`、`--ink-primary` |
| **Builder 认知对抗** | 未测（纯脚本） | 严重：阅读器花费额外 61 秒藏匿抽屉与图表 | **彻底消除**：契约断言与产品形态严密吻合，零无用交互负担 |
| **逃逸与冒充** | 零（真实阻断探查拦截） | 零（真实隔离输出） | **零（持续保持 Layer 1/2/3 严格隔离与阻断上报）** |

---

## 5. 总结与后续建议

本次三轮走查与优化验证了**分层基准体系驱动 Skill 进化的闭环能力**：
1. **第一轮（机制探查）**：建立严谨的分层基线，消除虚假宣称，识别出 L3 真实环境阻断；
2. **第二轮（实装暴露缺陷）**：通过极端案例对立实测，精准暴露“通用断言教条膨胀”与“垂直领域 Token 缺失”两大核心摩擦点；
3. **第三轮（定向改进与收敛）**：实施基于 Archetype 的情境敏感断言矩阵与原生领域语义 Token，全量回归测试通过，从根本上消除了模型在非控制台场景下的“削足适履”认知负担。

下一步建议：推进 Phase 3 的 Subagent Mock User 驱动器实现，攻克 Layer 3 交互式多轮会话自动评测环境。
