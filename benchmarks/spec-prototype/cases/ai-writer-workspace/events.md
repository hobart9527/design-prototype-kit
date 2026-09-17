# Counterfactual Events: AI Writer Workspace

> 反事实触发事件。仅当 `trigger_condition:` 满足时按 `inject:` 注入；未满足的事件不得提前透露或由测试器主动补写为已讨论事实。

## Event 1 — AI edit accepted by mistake
- trigger_condition: 产物已具备 `Accept` / `Reject` 动作
- inject: 「刚误点了 Accept，整段被替换掉了，我要一键撤销回原稿。」
- expected_effect: 引入采纳后的快捷撤销恢复路径，双轨协作具备回滚闭环。

## Event 2 — Generation stalled
- trigger_condition: Skill 询问 AI 交互状态处理
- inject: 「生成超过十秒时界面像死了，需要骨架态让我知道它还在跑。」
- expected_effect: 生成中等待状态必须具备优雅骨架/呼吸态反馈，不出现假死。
