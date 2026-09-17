# Acceptance Criteria: Mobile Booking

## 结构化验收 (Structured Acceptance)

### automated
- **mobile_viewport** — 方法：以 brief 约定的移动断点视口加载，断言主容器宽度与该断点一致且无横向滚动。
- **touch_targets** — 方法：断言交互控件命中区域不小于移动端最小触控热区，且具备 `:active` 触控状态样式。
- **booking_flow** — 方法：断言时段选择卡片可选，预约确认 Action 流程可完成并产生确认反馈。
- **price_units** — 方法：断言价格与定金文本携带货币符号或计量单位。
- **snap_behavior** — 方法：断言滚动容器具备弹性吸附行为。

### human
- **触控手感** — 评价维度：吸附、回弹与过渡动画的流畅程度。
- **流程清晰度** — 评价维度：从时段选择到确认的步骤是否一目了然。

## legacy

### 验收断言
1. 页面视口以 390px 移动宽度为主容器，支持触摸区域与弹性吸附。
2. 存在明确的时段选择卡片与预约确认 Action Verb 流程。
3. 价格与定金必须携带货币符号或单位（如 `¥299 / 次`）。
4. 交互控件包含 `:active` 触控状态响应。
