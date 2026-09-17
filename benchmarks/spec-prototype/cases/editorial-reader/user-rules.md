<!-- NOT FOR SKILL SESSION -->
# User Rules: Editorial Reader

> 本文件模拟用户持有的事实、偏好与禁区，**不向被测会话暴露**。仅当 Skill 主动提问时，按当前问题从下文取用对应事实回应。

## Held Facts
- 基线类型：Baseline 3 (Editorial Reading & Digital Publication)。
- 读者：深度长文读者，阅读万字专栏、做学术高亮引注、保存离线书库。
- 目标：沉浸式专注阅读，引注与收藏的低干扰呼出。

## Preferences
- 审美：纸本出版物触感，浅色模式背景 `#faf8f3`，正文 `#18181b`，衬线优先（Charter / Georgia）。
- 排版：正文列宽 65-75ch，行距 1.6-1.75，段落留白自然。
- 反馈：阅读时间或字数统计（如 `12 min read`）必须显式带单位。

## Decision Answers（被问到才给出）
- 色彩方案：浅色出版物纸张质感（`editorial-paper`，bg `#faf8f3`，文字 `#18181b`，强调色天青蓝 `#0284c7`）。
- 交互细节：收藏仅按钮状态即时切换 + 底部淡入淡出状态胶囊，不弹确认弹窗。

## Forbidden
- 严禁仪表盘式监控图表或高频跳动数字指示器。
- 浅色模式正文对比度须达 WCAG AAA（> 7:1），严禁不可读灰白混杂。
- Bookmark 严禁跳出“是否确定收藏”这类阻断式弹窗。
