# Discussion: project-workspace
- Energy: 3
- Finish: machined-industrial
- Density: sparse
- Weight: regular
- Seriousness: 3

## Ground Truth Facts & User Responses
# User Simulated Responses: Project Workspace

## 真实偏好与事实边界 (Ground Truth Facts)
- **基线类型**：Baseline 2 (SaaS Business Canvas & Operational Workspace)。
- **审美氛围**：倾向自然现代生产力风格（`monochrome-pure` 或 `warm-graphite-lime`），支持工作空间清晰层级。
- **确认决策**：
  - 询问任务状态变更时：支持拖拽或直接点击状态徽章触发 Action Verb 快速切换，配撤销（Undo）动作。
  - 询问多表面拓扑时：主看板必须包含回到 Overview 与 Milestones 的有效拓扑链接。

## Product Context & Tension Synthesis
# Benchmark Case 2: 项目协作空间 (Project Workspace)

## 原始需求 (Brief)
构建面向跨职能产品研发团队的项目协作工作台（Project Workspace）。
支撑从需求规划（Backlog）、敏捷迭代看板（Sprint Board）到发布里程碑（Milestones）的流转与协同。

## 关键业务与张力 (Tension)
- **核心张力**：项目宏观全局掌控 vs 微观任务详情与卡片状态沉浸式处理。
- **签名关系**：产研团队成员与任务卡片流转、优先级调整之间的流体响应。

## 材质边界与克制不变量
1. 严禁无边界弹出深层嵌套的 Modal 循环（所有任务详情采用平滑 Drawer 或内嵌展开处理）。
2. 支持跨视图导航（看板、表格、甘特），切换时必须持久化保留选中的过滤条件。

## Confirmed Decisions
- bg-void: #0f172a
- accent-primary: #10b981
