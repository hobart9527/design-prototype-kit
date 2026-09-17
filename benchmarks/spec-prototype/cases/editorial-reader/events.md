# Counterfactual Events: Editorial Reader

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — Paper tone rejected
- trigger_condition: Skill 首轮给出深色或高对比冷调阅读底色
- inject: 「夜里读长文眼睛疼，我要纸张暖白底 `#faf8f3`，正文字号也别再压缩。」
- expected_effect: 色彩需求收敛到浅色纸本方案，正文对比度需达 AAA。

## Event 2 — Bookmark blocked the reading
- trigger_condition: 产物中收藏动作出现阻塞式确认
- inject: 「收藏怎么还弹窗问确定，打断阅读了，改成无感反馈。」
- expected_effect: 恢复路径为轻量无阻塞反馈，收藏动作不中断阅读。
