# Counterfactual Events: Product Marketing Showcase

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — Anti-marketing rule misfires
- trigger_condition: 产物 Hero 被削减为低表现力的信息列表或缺少主 CTA
- inject: 「这是营销官网，不是内部工具页，Hero 要能打动人，主 CTA 必须显眼可用。」
- expected_effect: 恢复营销表现力与转化路径，反营销约束不误伤本案例。

## Event 2 — Claims challenged
- trigger_condition: 产物出现无依据参数或占位文案
- inject: 「参数得写真实的，比如 12 小时续航、IP68，别放 Lorem 占位图。」
- expected_effect: 内容约束收敛到真实可核的产品参数与可信演示。
