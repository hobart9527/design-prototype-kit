# Product Understanding: Autonomous Agent Pipeline Orchestrator

## Identity and sources

- Product / project: Agent Pipeline Console (智能体高并发管线实时调度台)
- Version / date: v3.1.0 / 2026-09-17 (Authentic Skill Execution Run)
- Baseline Selection: **Baseline 1: Dense Data & Engineering Workbench** (主基调) + 局部借鉴 **Baseline 2: Modern SaaS Drawer Ergonomics**
- Reality Benchmark Anchors:
  - **Datadog APM & Pipeline Graph**: 非线性拓扑管线、扇入扇出并发追踪、高警报色彩编码、时序 Sparkline。
  - **Temporal Web UI / Airflow DAGs**: 确定性状态机流转、分支隔离旁路（Bypass to Shadow）、因果审计。
- Evidence status vocabulary: `explicit | observed | derived | hypothesis | unknown`

## Product Thesis

- Intended actor and consequential context: 平台可靠性工程师与生产值班员（SRE / Agent Ops），实时管控 12,000+ RPS 自主 Agent 形成的并发执行 DAG。
- Job/progress the product enables: 在高吞吐非线性智能体任务流中，提供秒级拓扑态势感知、异常分支影子隔离（Bypass to Shadow Sandbox）与回压监测。
- Observable user outcome: 运维者在 3 秒内识别异常节点与下游受阻链路，通过拓扑交互或快捷键一键挂起高风险 Agent，保障主干集群平稳运行。
- Distinctive value or mechanism: **非线性拓扑因果流与双通道确定性接管（Non-Linear Causal Stream & Dual-Channel Intervention）**。
- Central design tension: **12,000+ RPS 极限数据吞吐 vs 3 秒直觉异常识别与确定性处置**。
- Principle conviction: **专业欺骗感源自业务本体的极致推演（Verisimilitude via Domain Depth）**。以真实的非线性 DAG 分支、时序微线图与轻量数据流脉冲，实现兼具高信噪比与工业厚度的生产级体验。

## OOUX Entity Integrity

| Object/content type | Real Domain Meaning | Relationships | Lifecycle | User Actions |
|---|---|---|---|---|
| **Agent Pipeline** | 智能体调度执行管线 | 1:N 包含 Execution Node | 待机 -> 运行中 -> 降级 -> 恢复 | 暂停、流量调谐、一键旁路 |
| **Execution Node** | DAG 任务执行节点/算子 | N:1 归属 Pipeline | 队列中 -> 执行中 -> 漂移告警 -> 隔离 | 查看堆栈、隔离至影子环境、单步重跑 |
| **Drift Alert** | 置信度/输出漂移告警 | 1:1 附着于异常节点 | 触发 -> 隔离中 -> 已缓解 | 查看告警详情、时序比对 |
| **Shadow Branch** | 隔离后分流的影子沙箱环境 | 0:1 伴随人工干预产生 | 镜像分流 -> 仿真重跑 -> 合流上线 | 比对差分输出、排空死信队列 |

## Cognitive Energy Return & Budgeting

- **Positive Return on Kinetic Craft**:
  - **SVG 数据流动脉冲**：极低算力无声传递 12,000 RPS 实时通量，一眼辨识流水线畅通度。
  - **微型 Sparkline 趋势图**：为指标提供 60 秒历史基线对比，免除孤立数字的上下文缺失。
  - **非线性扇出汇聚拓扑**：忠实反映并行检查逻辑（情感分析 + 合规审计），还原本体真实结构。
  - **双通道安全接管**：显式红底 `[ISOLATE NODE TO SHADOW]` 大按钮 + `[Space]` 快捷键吸附，无障碍且零猜谜。
