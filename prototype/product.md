# Product Understanding: Agent Detent Cockpit (AI 自动编排流协同决策台)

> Project-scoped, revisable design synthesis. Cite current product sources.

## Identity and sources

- Product / project: Agent Detent Cockpit (AI 协同决策中控)
- Version / date: v1.0.0 / 2026-09-16
- Scope represented here: 高并发、高危金融/风控 Agent 编排流运行态接管中控
- Primary product sources and revisions: Scenario 1 - AI 自动编排流之协同决策台
- Evidence status vocabulary: `explicit | observed | derived | hypothesis | unknown`

## Product Thesis

- Intended actor and consequential context: 资深风控/量化操盘专家（Risk Officer & Quant Lead），负责监控并兜底 100+ 并发运行的高危自主 Agent 编排流水线。
- Job/progress the product enables: 在零停顿、全速推进的 Agent 自主决策流中，提供亚秒级、原位触感可感知的隐式与显式干预能力。
- Observable user outcome: 专家在 100ms 内感知风险点，使用物理键盘热键与阻尼滑杆完成微调，系统无缝合流，无任何模态打断。
- Product/business outcome and how it could be observed: 规避异常交易/高危决策事故，同时消除 95% 以上因弹窗阻塞造成的流水线空转与吞吐衰减。
- Distinctive value or mechanism: **电传操纵与磁吸阻尼（Fly-by-wire & Magnetic Detent）**。流水线自主巡航，系统在低置信度（<85%）与关键资金转移节点自动生成“重力阻尼井”；操作员拨动时间轴自动被吸附定位，空格键瞬态冻结参数分支。
- Central design tension/risk: 吞吐量与终局责任（Throughput vs Liability）。
- Hidden tension addressed: 极致流动感（Flow） vs 绝对确定性（Certainty）。传统审批流通过“阻断流”换取安全，造成注意力瓦解；本系统通过“阻尼场”将安全内化为手感。
- Principal designer conviction & conscious cost:
  - **Core Stance**: 严禁一切全局阻塞式 Modal 弹窗与机械连线图。所有干预收敛至时间轴重力井与热键滑轨。
  - **Strongest Counter-argument**: 初级操作人员可能习惯被动等待弹窗通知，主动式阻尼滑轨需要学习成本与专注度。
  - **Conscious Cost**: 放弃新手引导式平平无奇的表单与低信息密度卡片，换取极高的数据密度与专家肌肉记忆。
- Current-release boundary and non-goals:
  - Non-goal: 不做工作流开发期连线编辑器（那是 Studio/IDE 的工作，决策台专注 Runtime）。
  - Non-goal: 不做全量底层纯文本 Log 倾倒（仅保留十六进制动作特征码与关键状态差分）。

## Source-supported jobs and outcomes

| Actor | Trigger/context | Job and first-class object/content | Decision/action | User outcome | Product outcome | Source/evidence status |
|---|---|---|---|---|---|---|
| 风控操盘专家 | Agent 置信度突降至 78% 或触发大额调仓 | 实时评估 Pipeline Step 并决定是否干预 | 空格冻结当前 Step，滑杆原位修正 Delta，松手恢复巡航 | 500ms 内完成参数修正且不造成链路阻塞 | 杜绝风险敞口，流水线吞吐无损 | `explicit` |
| 应急响应指挥官 | 突发宏观黑天鹅事件，全流水线需批量调低滑点容差 | 批量应用全局阻尼约束（Global Detent Override） | 开启电传总控杆限制最高风险系数 | 一键压制所有并发流水线风险上限 | 体系级防御生效 | `derived` |

## Object and Content Model

| Object/content type | Purpose and key attributes | Relationships/cardinality | Lifecycle | Owner/authority | User actions | Source or unknown |
|---|---|---|---|---|---|---|
| **Pipeline Run** | 并发执行的智能体流水线实例（ID, 状态, 吞吐速率, 综合置信度） | 1:N 包含 Waypoint Step | 队列中 -> 巡航中 -> 阻尼吸附 -> 终局交割 | 编排引擎 | 过滤、巡视、全局降速 | `explicit` |
| **Waypoint Step** | 单步决策航路点（时间戳, 动作类型, 置信分, 资金影响额, 参数 Payload） | N:1 归属 Pipeline | 生成 -> 推进 -> 归档 | 执行智能体 | 聚焦、差分预览、原位重写 | `explicit` |
| **Detent Well (阻尼井)** | 依风险算法在时间轴上生成的空间引力场（阻尼系数, 阈值, 吸引半径） | 1:1 附着于低置信度/高风险 Step | 动态计算 -> 磁吸捕获 -> 确认解除 | 风控策略中控 | 拨动滑吸、强制越过、原位微调 | `explicit` |
| **Fork Preview (分支预测)** | 人工微调后与 Agent 原始决策并行的瞬态阴影预测流（Delta, 预估损益, 胜率修正） | 0:1 伴随人工干预触发 | 暂态生成 -> 合流接管 / 放弃 | 协同决策引擎 | 对比试算、确认合流 | `explicit` |

## Actors, roles and service relationships

| Actor/system | Goal or responsibility | What they may see/change | Handoff or backstage dependency | Evidence/limit |
|---|---|---|---|---|
| **Human Pilot** (风控专家) | 终局质量把控与异常接管 | 实时拓扑、阻尼井定位、参数实时干预、分支合流 | 依赖毫秒级 WebSocket 状态推流与电传仿真引擎 | `explicit` |
| **Agent Orchestrator** | 自动化高吞吐推进决策流 | 状态推流、执行原子动作、接收阻尼反作用力 | 接收人类微调注入后自动完成航向校正 | `explicit` |

## Representative contexts

| Context | Actor and trigger | Environment/device | Frequency/stakes | Information and emotional need | Outcome/recipient | Evidence status |
|---|---|---|---|---|---|---|
| 黄金交易高频穿梭流 | 波动率指数异动触发连环调仓 | 桌面多屏 / 极速机械键盘+触控板 | 亚秒级连续决策 / 百万美元级风险 | 极高信噪比，拒绝任何视线遮挡，瞬时掌控各流航向 | 快速微调并平滑继续 | `explicit` |
