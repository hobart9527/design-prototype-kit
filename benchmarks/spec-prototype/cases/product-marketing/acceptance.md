# Acceptance Criteria: Product Marketing Showcase

## 结构化验收 (Structured Acceptance)

### automated
- **marketing_structure** — 方法：断言 Hero、特性矩阵、实时演示、定价与主 CTA 区块节点均存在且顺序合理。
- **primary_cta** — 方法：断言存在明确的主行动点，触发后产生表单或模态反馈。
- **no_false_block** — 方法：断言反营销规则未拦截或降级营销内容，区块与文案完整渲染。
- **design_tokens** — 方法：断言样式消费设计系统 Token，色彩与排版变量一致。

### human
- **视觉说服力** — 评价维度：首屏构图与信息密度是否具备官网级质感。
- **转化路径清晰度** — 评价维度：从价值主张到主 CTA 的动线是否顺畅。

## legacy

### 验收断言
1. 页面必须呈现高质量的营销官网架构（Hero、特性矩阵 Bento、实时演示、定价/转化 CTA）。
2. 绝对不能因为“反营销”规则而拦截或破坏营销页面的有效产出。
3. 包含明确的主行动点（Primary CTA）及表单或模态反馈。
4. 正确消费设计系统 Token，保持色彩与排版的一致性。
