<!-- NOT FOR SKILL SESSION -->
# User Rules: Project Workspace

> 本文件模拟用户持有的事实、偏好与禁区，**不向被测会话暴露**。仅当 Skill 主动提问时，按当前问题从下文取用对应事实回应。

## Held Facts
- 基线类型：Baseline 2 (SaaS Business Canvas & Operational Workspace)。
- 使用者：跨职能产品研发团队，流转路径为 Backlog -> Sprint Board -> Milestones。
- 现状：团队已有多视图（看板、表格、甘特）与既有过滤条件，不希望每次切换重设。

## Preferences
- 审美：自然现代生产力风格（`monochrome-pure` 或 `warm-graphite-lime`），层级清晰、留白充足。
- 信息：任务卡片数量、燃尽统计必须带单位与进度参照。
- 布局：任务详情以平滑 Drawer 或内嵌展开承载，保持上下文不丢失。

## Decision Answers（被问到才给出）
- 任务状态变更：支持拖拽或直接点击状态徽章触发 Action Verb 快速切换，并提供撤销（Undo）。
- 多表面拓扑：主看板必须包含回到 Overview 与 Milestones 的有效拓扑链接。

## Forbidden
- 严禁无边界弹出深层嵌套的 Modal 循环。
- 严禁跨视图切换时丢弃已选过滤条件。
- 严禁硬编码内联 hex 颜色，必须继承 tokens.css。
