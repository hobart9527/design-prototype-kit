# Counterfactual Events: Mobile Booking

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — Slot already taken
- trigger_condition: 产物已呈现时段选择卡片
- inject: 「刚选的 14:00 被别人抢了，页面得立刻告诉我，并给我最近的替代时段。」
- expected_effect: 引入时段冲突提示与快速切换替代方案，作为预约流程的恢复路径。

## Event 2 — Payment interrupted
- trigger_condition: Skill 询问支付或订单确认细节
- inject: 「付定金时网络断了，返回后得能接着上次的时段继续，别让我重选。」
- expected_effect: 预约上下文在中断后保留，恢复路径承接既定时段。
