# Discussion: mobile-booking
- Energy: 3
- Finish: somatic-touch
- Density: sparse
- Weight: regular
- Seriousness: 3

## Ground Truth Facts & User Responses
# User Simulated Responses: Mobile Booking

## 真实偏好与事实边界 (Ground Truth Facts)
- **基线类型**：Baseline 4 (Somatic Touchflow & Mobile Consumer App)。
- **审美氛围**：圆润、亲和、有弹性触控质感（`somatic-touch`，卡片圆角 16px，胶囊按钮）。
- **确认决策**：
  - 询问布局时：选择底部固定的 Sticky Action Bar，顶部卡片左右滑动吸附。
  - 询问时段选择时：选中时段具备明确的高亮与震动感反馈（视觉上的微放大），提交订单进入下一步。

## Product Context & Tension Synthesis
# Benchmark Case 4: 移动端服务预约流程 (Mobile Booking)

## 原始需求 (Brief)
构建一个专为智能手机移动端设计的专业服务即时预约流（Mobile Booking Touchflow）。
用户在单手握持状态下，顺畅完成技师选择、日历时段确认、定金支付和行程日历写入。

## 关键业务与张力 (Tension)
- **核心张力**：受限屏幕空间下的高效表单输入 vs 预约时间冲突时的无缝错误恢复。
- **签名关系**：指尖轻触与时段卡片弹性吸附（Somatic Touch Feedback）之间的确定感。

## 材质边界与克制不变量
1. 触控热区绝对不小于 44x44px，严禁密集低像素点选。
2. 按钮触按具有微动效（`:active transform` / `opacity`），底部固定主操作栏。
3. 必须具备时段已被占用的冲突提示与快速切换替代方案。

## Confirmed Decisions
- bg-void: #0f172a
- accent-primary: #10b981
