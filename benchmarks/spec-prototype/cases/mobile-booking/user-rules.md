<!-- NOT FOR SKILL SESSION -->
# User Rules: Mobile Booking

> 本文件模拟用户持有的事实、偏好与禁区，**不向被测会话暴露**。仅当 Skill 主动提问时，按当前问题从下文取用对应事实回应。

## Held Facts
- 基线类型：Baseline 4 (Somatic Touchflow & Mobile Consumer App)。
- 使用者：单手握持的移动端用户，流程为 技师选择 -> 日历时段确认 -> 定金支付 -> 行程日历写入。
- 主容器：390px 移动视口。

## Preferences
- 审美：圆润亲和、有弹性触控质感（`somatic-touch`，卡片圆角 16px，胶囊按钮）。
- 交互：底部固定 Sticky Action Bar，顶部卡片左右滑动吸附；触按有 `:active` 微动效。
- 信息：价格与定金必须带货币符号或单位（如 `¥299 / 次`）。

## Decision Answers（被问到才给出）
- 布局：底部固定的 Sticky Action Bar，顶部卡片左右滑动吸附。
- 时段选择：选中时段具备明确高亮与视觉微放大反馈，提交订单进入下一步。

## Forbidden
- 触控热区绝对不小于 44x44px，严禁密集低像素点选。
- 严禁无冲突提示：时段被占用时必须给出替代时段。
- 严禁省略底部固定主操作栏。
