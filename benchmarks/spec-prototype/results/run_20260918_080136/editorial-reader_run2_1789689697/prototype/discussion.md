# Discussion: editorial-reader
- Energy: 2
- Finish: editorial-paper
- Density: sparse
- Weight: regular
- Seriousness: 3

## Ground Truth Facts & User Responses
# User Simulated Responses: Editorial Reader

## 真实偏好与事实边界 (Ground Truth Facts)
- **基线类型**：Baseline 3 (Editorial Reading & Digital Publication)。
- **审美氛围**：纸本出版物触感，浅色模式（`#faf8f3`），字体优先衬线（Charter / Georgia），文字 `#18181b`。
- **排版要求**：正文列宽限制在 65-75ch 之间，段落留白自然，行距 1.6-1.75。
- **确认决策**：
  - 询问色彩方案时：选择浅色出版物纸张质感方案（`editorial-paper`，bg `#faf8f3`，文字 `#18181b`，强调色天青蓝 `#0284c7`）。
  - 询问交互细节时：收藏操作只需按钮状态即时切换 + 底部淡入淡出状态胶囊，不弹确认弹窗。

## Product Context & Tension Synthesis
# Benchmark Case 3: 深度长文阅读产品 (Editorial Reader)

## 原始需求 (Brief)
打造一款注重专注阅读、排版韵律与深度思辨的数字出版长文阅读器（Editorial Reader）。
读者在此阅读万字深度专栏、进行学术高亮引注、并保存到个人离线书库。

## 关键业务与张力 (Tension)
- **核心张力**：沉浸式专注阅读 vs 快捷发现、引注与收藏的低干扰呼出。
- **签名关系**：读者与高质量文本行间距、字体衬线呼吸感之间的精神共鸣。

## 材质边界与克制不变量
1. 绝对严禁强塞仪表盘式监控图表或高频跳动的数字指示器。
2. 浅色模式背景（`#faf8f3` 纸质暖白）必须保证正文对比度达到 WCAG AAA 级别（> 7:1），严禁不可读的灰白混杂。
3. 收藏（Bookmark）动作必须轻量（无侵入提示），严禁跳出“是否确定收藏”这类阻断式弹窗。

## Confirmed Decisions
- bg-void: #faf8f3
- accent-primary: #0284c7
