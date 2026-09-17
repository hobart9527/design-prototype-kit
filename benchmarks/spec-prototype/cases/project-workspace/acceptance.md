# Acceptance Criteria: Project Workspace

## 结构化验收 (Structured Acceptance)

### automated
- **kanban_columns** — 方法：断言页面同时存在 To Do / In Progress / Done 三个列容器节点。
- **task_lifecycle** — 方法：断言任务创建入口可提交，且任务可从一列流转到另一列并更新计数。
- **metric_context** — 方法：断言任务计数与燃尽统计文本均携带单位或进度参照文本。
- **navigation_return** — 方法：断言存在多表面导航入口，可从子页面返回 Overview 页面。
- **design_tokens** — 方法：断言样式消费 tokens.css 变量，未出现内联 hex 色值。

### human
- **看板可读性** — 评价维度：列与卡片的信息密度、流转提示是否直观。
- **导航一致性** — 评价维度：多表面切换是否符合用户心智模型。

## legacy

### 验收断言
1. 页面必须呈现完整的看板拓扑（To Do / In Progress / Done），且包含任务创建与状态流转操作。
2. 任务卡片数量、燃尽统计必须带单位与进度参照（Zero Naked Metrics）。
3. 具备多表面导航能力，支持返回 Overview 页面。
4. 严格继承 tokens.css 尺寸与颜色定义，严禁内联写死 hex 颜色。
