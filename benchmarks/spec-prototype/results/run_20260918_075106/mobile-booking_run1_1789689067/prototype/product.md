# Product Thesis: mobile-booking
- Dominant Baseline: Baseline 4 (Consumer & Mobile Touch-First)
- Authentic Brief:
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
