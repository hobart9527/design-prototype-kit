## Context

见 proposal.md — Why。旧版基线已冻结于本地 commit `5af898b`，包含 benchmarks/、compile_tokens.py、capture.mjs、tests/test_pipeline.py。此设计解决的是实验协议与执行边界问题，不修改设计引擎行为。

已确认的约束：当前平台不存在可供自动逐轮模拟的真实 Skill 会话入口（`eval.yaml` 无实现，`AskUserQuestion` 不可编程驱动）。因此完整 Skill 实验 Layer 3 目前为环境阻断，设计必须正视此边界，不伪造替代方案。

## Goals / Non-Goals

**Goals:**
- 将机制检查（Layer 1）、Builder 定合同测试（Layer 2）、完整 Skill 实验（Layer 3）三者产物和结论严格分离，防止跨层声明。
- 修正 benchmarks/run_benchmark.py 的层定义和输出标签，使其只声称实际执行的内容。
- 建立六案例的独立验收结构：brief（被测方可见）+ 模拟用户规则（测试器持有）+ 独立 acceptance（评估方持有）+ 反事实事件（按条件触发）四件套。
- 明确阻断：L3 无法执行时返回 `ENVIRONMENT_BLOCKED` 而非静默回退脚本。
- 基线提交 `5af898b` 作为旧版参照，不 push，所有对比须在同层、同控制条件下进行。

**Non-Goals:**
- 修改 Skill 设计引擎行为、提示词或任何设计约束（此类修复须由真实失败归因后另立 Change）。
- 实现自动化逐轮会话注入（平台能力缺失，不在本 Change 范围内）。
- 建立人工盲评调度系统（人工评审流程由人完成，工具只提供待评审槽位和记录格式）。
- 修改 openspec/specs/design-engine/ 下的现有规格（无 MODIFIED Requirement）。

## Decisions

**D1：runner 只改层标签，不扩建为完整 Skill 执行器。**
- 理由：Layer 2/3 需要真实 Agent dispatch，强行在 runner 里模拟会污染被测边界，且当前无法解决 AskUserQuestion 注入问题。
- 备选：扩建 runner → 拒绝，因为它会把测试器变成被测能力的替代者。

**D2：acceptance.md 升级为结构化验收，分为自动行为检查 + 人工评审两部分。**
- 理由：现有 acceptance.md 是自由文本，无任何消费方；必须先有可执行的检查描述，才能在结果里标注"未测"而非静默通过。
- 格式：YAML frontmatter 或 markdown section，每条验收项含类型（`automated|human`）、方法和通过依据。

**D3：六案例结构分文件，不合并。**
- `brief.md`：被测方在首轮可见的唯一输入。
- `user-rules.md`：模拟用户/真实用户持有的事实、偏好、禁区，仅按轮次回应问题，不主动给出完整设计。
- `events.md`：反事实事件列表，含触发条件（轮次、Skill 状态）和注入内容。
- `acceptance.md`：重写为结构化验收，评估方持有，不向被测会话暴露。

**D4：对比必须记录控制条件，不等条件结果拒绝合并。**
- 结果文件新增 `run_meta.json` 字段：layer、case、model、skill_version、script_versions、conditions（human_intervened、env_blocked 等）。
- 跨层或条件不匹配的两条记录禁止出现在同一对比表格中。

## Risks / Trade-offs

- [L3 永久阻断] → 当前只能做 L1/L2；接受，明确记录，不伪造。
- [Acceptance 结构化迁移破坏现有内容] → 保留旧 acceptance 文本作为 legacy section，新增 structured 区块，脚本只消费后者。
- [六案例 user-rules.md 被测方意外读到] → 通过工具隔离（生产环境用不同目录权限），当前本地实验须手工注意分层。
