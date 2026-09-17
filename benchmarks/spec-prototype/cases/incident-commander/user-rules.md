<!-- NOT FOR SKILL SESSION -->
# User Rules: Incident Commander

> 本文件模拟用户持有的事实、偏好与禁区，**不向被测会话暴露**。仅当 Skill 主动提问时，按当前问题从下文取用对应事实回应。

## Held Facts
- 基线类型：Baseline 1 (Dense Operational Console & Engineering Workbench)。
- 使用者：主备指挥官（SRE / 平台工程师），值守中需要单手快速操作。
- 现状：3 个区域跨区雪崩，受影响服务按 P0/P1 分级，事件生命周期为 探测 -> 隔离 -> 排空 -> 恢复 -> 复盘。

## Preferences
- 审美：暗色冷硬工业风（`warm-graphite-lime` 或 `titanium-amber`），背景纯粹深沉，文字对比度极高；排斥低对比灰与刺眼纯白大底。
- 排版：所有指标启用等宽数字（`tabular-nums`），监控面板使用 1px 细边框机械刻度感。
- 交互：键盘驱动（`/` 聚焦搜索，`Esc` 关闭模态，`j/k` 行间导航），按压反馈 `scale(0.97)`。

## Decision Answers（被问到才给出）
- 色彩方案：选方案 B（`titanium-amber`），主强调色 `#f59e0b`，背景 `#0a0c10`。
- 破坏性操作：必须二次警示模态配合键入或长按确认；完成后右下角轻量 Toast 广播全局状态。

## Forbidden
- 严禁宣传型营销卡片、浮夸 Banner 或轮播图。
- 严禁无参照基线的裸数字：吞吐、延时、容量必须带单位、趋势差值或基准 Sparkline。
- 排空 `Drain Node` / 流量切断不得做成无阶段确认、不可撤销的单击动作。
