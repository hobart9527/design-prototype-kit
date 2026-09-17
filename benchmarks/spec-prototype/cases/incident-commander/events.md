# Counterfactual Events: Incident Commander

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — Blast radius widens
- trigger_condition: Skill 首轮询问影响范围或严重度分级
- inject: 「不止单区域——三个区域同时雪崩，P0 已持续 12 分钟，影响 7 个下游服务。」
- expected_effect: 需求由单点处置升级为跨区影响面与 P0/P1 分级视图。

## Event 2 — Unsafe drain attempt
- trigger_condition: 产物出现 `Drain Node` 或流量切断，且未见阶段确认
- inject: 「刚有工程师一键排空了生产节点，我需要能紧急终止并回滚这次操作。」
- expected_effect: 引入可撤销/紧急终止的恢复路径，破坏性操作闭环具备回滚能力。
