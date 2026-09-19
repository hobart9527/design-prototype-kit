<!-- HIDDEN: never copied into a run workspace. Injected only when the trigger fires. -->
# Counterfactual Events: Incident Commander

## Event 1 — Blast radius widens
- trigger: 影响范围|严重度|分级|P0|区域
- inject: 补充一下：不止一个区域，三个区域同时在雪崩，P0 已经持续 12 分钟，影响 7 个下游服务。

## Event 2 — Unsafe drain attempt
- trigger: 排空|Drain|下线|隔离
- inject: 刚有同事一键排空了生产节点，我需要能紧急终止并回滚这次操作。

## Event 3 — Mobile check only
- trigger: 手机|移动端|响应式
- inject: 手机上只要能看到当前事故状态就够了，破坏性操作只在电脑上做。
