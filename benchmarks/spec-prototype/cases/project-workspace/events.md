# Counterfactual Events: Project Workspace

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — Milestone pulled forward
- trigger_condition: Skill 询问时间线或视图优先级
- inject: 「发布里程碑提前两周，Milestones 视图现在要先于甘特排。」
- expected_effect: 需求顺序改变，Milestones 从附属视图升级为首要流转节点。

## Event 2 — Accidental bulk state change
- trigger_condition: 产物已具备状态切换动作
- inject: 「刚才一次拖拽误改了 30 张卡片状态，需要批量撤销回上一步。」
- expected_effect: 引入批量回滚恢复路径，状态流转具备 Undo 闭环。
