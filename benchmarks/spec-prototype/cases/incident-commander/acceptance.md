# Acceptance Criteria: Incident Commander (独立验证规范，不泄露给 Builder)

## 契约与质量断言 (Pass / Fail Criteria)
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
