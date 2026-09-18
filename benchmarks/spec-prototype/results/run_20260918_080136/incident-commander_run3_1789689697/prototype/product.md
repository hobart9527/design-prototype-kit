# Product Thesis: incident-commander
- Dominant Baseline: Baseline 1 (Dense Data & Engineering Workbench)
- Authentic Brief:
# Benchmark Case 1: 运维事件处置台 (Incident Commander)

## 原始需求 (Brief)
构建一个专为 SRE 和平台工程师设计的高并发分布式集群事件协同处置控制台（Incident Commander）。
系统需在单屏高密度信息流下，帮助主备指挥官快速诊断跨区域集群雪崩、异常节点下发排空并协调救灾。

## 关键业务与张力 (Tension)
- **核心张力**：高密度遥测信息吞吐 vs 极端破坏性操作下的确定性安全防误触。
- **签名关系 (Signature Relationship)**：工程师与事故生命周期（探测 -> 隔离 -> 排空 -> 恢复 -> 复盘）之间的低延时控制感。

## 材质边界与克制不变量
1. 严禁使用任何宣传型营销卡片、浮夸 Banner 或轮播图。
2. 严禁无参照基线的纯裸数字（所有吞吐、延时与容量必须附带单位、趋势差值或基准 Sparkline）。
3. 破坏性操作（如节点排空 `Drain Node`、流量切断）必须具备明确的阶段确认与可撤销/紧急终止机制。
