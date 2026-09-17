# Acceptance Criteria: Incident Commander (独立验证规范，不泄露给 Builder)

## 结构化验收 (Structured Acceptance)

### automated
- **topology_board** — 方法：查询页面 DOM，断言主遥测拓扑看板与受影响服务列表节点存在且渲染非空内容。
- **severity_labels** — 方法：断言存在 P0/P1 严重度标识文本节点。
- **metric_units** — 方法：正则匹配指标文本，断言延迟、QPS、丢包率均携带单位或基线对照文本。
- **action_lifecycle** — 方法：断言存在 Drain Node / Isolate Cluster 触发控件；点击后出现确认 Dialog 或 Drawer；确认后出现 Toast 状态反馈且可回滚或关闭。
- **design_tokens** — 方法：断言样式表引入并消费标准 Token 变量，未出现内联 hex 色值。

### human
- **语义真实度** — 评价维度：页面是否为真正的事件作战指挥台，而非营销着陆页或简单看板。
- **信息层级清晰度** — 评价维度：严重度、影响面与处置动作的视觉优先级是否合理。
- **操作安全感** — 评价维度：二次确认与回滚反馈是否令操作者放心。

## legacy

### 契约与质量断言 (Pass / Fail Criteria)
1. **语义架构与真实性**：
   - 页面必须是真正的事件作战指挥台，严禁退化为云厂商营销着陆页或简单看板。
   - 包含主遥测拓扑看板、事件严重度标识（P0/P1）、影响服务列表及实时排空流控操作。
2. **Zero Naked Metrics 验证**：
   - 任何出现的延迟（ms）、QPS、丢包率等核心指标必须附带单位、基线对比（如 vs normal 15ms）或 SVG 走势迷你图。
3. **Action Verb Lifecycle 闭环**：
   - 存在触发控制项（`Drain Node` 或 `Isolate Cluster`）；
   - 具备二次防误触拦截（Dialog / Drawer），且承诺操作按钮文案明确；
   - 完成后具备即时状态变更与 Toast 提示，且支持状态回滚或关闭。
4. **代码工艺与设计系统继承**：
   - 必须引入并消费 `--bg-void`、`--accent-primary` 等标准 Token，杜绝随意内联 hex 色值。
   - 必须通过 `verify_prototype_quality.py` 静态质量门禁与多视口浏览器截图检查。
