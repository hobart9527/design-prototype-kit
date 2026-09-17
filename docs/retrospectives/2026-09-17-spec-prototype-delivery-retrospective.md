# spec-prototype 优化交付：执行链路与 Harness 复盘

日期：2026-09-17
对象：`repair-spec-prototype-design-loop`
性质：事后分析与优化建议；不是新的批准规格，也不表示优化方案已经实施。

## 1. 结论与证据边界

核心问题不是 SDD、EventKernel、subagent 或 worktree 的存在，而是已明确的 Task 在派发、执行、验证和恢复之间没有始终保持同一份契约与可关联的执行事实。协调者手工转译派发、启动故障诊断丢失、局部修复提前返回、测试归属错误，共同放大了执行往返。

必须同时保留另一个事实：Host 独立验证成功拦截过 Leaf 的错误成功声明，最终产生 Complete 和发布回执。不能把正确拦截误判成“门禁导致失败”，也不能根据晚到的进程通知推翻持久化完成事实。

证据等级：
- **直接记录**：当前会话保留的工具调用、工具返回、Loom 回执与 Agent 用量报告。
- **历史摘要**：压缩前的用户意图、初期实现与批准过程；不能冒充逐条原始审计。
- **源码调查**：只读调查返回的安装版本代码位置；可解释机制，不保证等同历史故障时刻版本。
- **待查**：没有对应执行输出或历史快照支持的具体原因。

本轮已获授权读取本次 transcript。实际提取未形成完整的事件时间戳账本，故以下给出全过程的顺序与因果，不虚构分钟级时间线或整个数小时的耗时占比。此限制不影响已保留的派发、Finding、重试、Complete 事实。

## 2. 原始目标与范围

用户要求修复 Skill 的通用能力缺陷，而非美化某一个 GPU 页面；明确拒绝擅自增加四类业务母版，也拒绝用堆叠门禁代替构建能力。

确认的优化方向：
1. 按探索、新增表面、局部优化、正式交付选择路线，不强制所有请求走完整冻结流程。
2. 解除单次生成与全局八步限制，允许定向读取、构建、渲染检查、修复和复验。
3. 工单传递项目决定与真实约束，不注入固定样式、交互命名或母版。
4. 清除通用脚本里的 GPU 领域硬编码、静默审美兜底及预填通过结果。
5. 区分静态检查、运行行为、视觉检查与人工确认，正式交付再冻结。

本次不要求重渲染 GPU 原型、不修改 Loom Runtime、不新增通用母版。用户授权限定基线提交 `4770012`；这不等于授权任意未来修订或绕过完整性校验。

## 3. Task 分工与实际依赖

| Task | 目标及主要所有者 | 依赖 | 原验证安排 |
|---|---|---|---|
| T-01 | SKILL.md、core-workflow.md、interpretation-rules.md 的意图路由 | 无 | pipeline 中两项文档/路由测试 |
| T-02 | Builder、Critic、capture.mjs 的自适应执行约束 | T-01 | pipeline 中参考规范测试 |
| T-03 | assemble_envelope.py、handoff.py 的探索/正式分流 | T-02 | handoff 测试及旧 lean-envelope 测试 |
| T-04 | compile_tokens.py 去静默预设，并更新 test_tokens.py | T-01 | test_tokens.py |
| T-05 | verify_prototype_quality.py、materialize_contracts.py、generate_review_portal.py，并更新 test_pipeline.py | T-03、T-04 | test_pipeline.py |

编制缺陷：T-02/T-04 改变了旧 lean-envelope 测试依赖的行为，但该测试的修改权在后置 T-05；T-03 却必须先通过它。这是可验证行为闭包被拆开，并非 SDD 必然要求如此。

## 4. 全过程：顺序、分支与结果

下表为事件顺序，不代表连续执行，也不将用户讨论或等待计入机器耗时。

| 阶段 | 实际动作 | 结果与影响 |
|---|---|---|
| 需求澄清 | 用户追问原型无实际改进、要求通用能力修复 | 从单例视觉补丁转向 Skill/脚本能力修复 |
| 方向纠偏 | 用户拒绝擅自引入四类母版及大量门禁 | 确定去处方化、真实反馈与证据边界 |
| 基线准备 | 用户授权限定基线提交 | 形成 `4770012` |
| 规格准备 | 建立 Change、T-01 至 T-05、验证命令与 Write scope | 进入受治理 delivery |
| generation-1 | T-01、T-02、T-04 完成并集成 | 回执记录通过；集成提交见第 11 节 |
| 启动异常 | Agent 调用收到 `BOUND_RELEASE_UNAVAILABLE:ReleaseRoutingError` | 属于启动前 Hook 拒绝，不是 Leaf 代码执行失败 |
| 协调偏离 | 更换 Agent 类型，后续省略类型并重写派发 Prompt | 原始派发身份及完整元数据未始终保留 |
| 工具入口偏离 | release 完整性问题后直接使用内部 Python CLI | 绕过外层路由，不是合法修复的证明 |
| generation-1 T-03 | 代码修改后，旧测试依赖 T-02/T-04 已改变的行为 | 因测试在 T-05 scope，提交 Finding；T-05 尚未启动 |
| 恢复读取 | delivery status/step 返回 T-03 Finding | T-01/02/04 completed，T-03 running，T-05 pending，terminal finding |
| 规格调整 | T-03 Verify with 收窄为单独 handoff 测试 | 解除跨任务验证阻塞，但不独立证明全部新行为 |
| 再准备 | spec prepare 产生 candidate `ecbd35d` | 新 revision 为 `582edd52…` |
| 批准调用 | actor-type=user 被拒；改成 human 后命令通过 | CLI 接受事实与真实用户对该 revision 的批准证据必须分开 |
| generation-2 T-03 | 第一次实际 Leaf 执行约 345.706 秒 | 返回失败：测试未成功完成、存在重复赋值 |
| T-03 同 Agent 恢复 | Coordinator 要求删除重复赋值并运行原测试 | 返回 1 passed、8 deselected；Host 接受并集成 `89a0e2e` |
| generation-2 T-05 attempt 1 | 实现及 pipeline 测试调整，执行约 508.170 秒 | 返回两项失败，并自述工作区干净、改动未保留 |
| T-05 同 Agent 恢复 | Coordinator 再要求修输入及旧断言、保留改动 | Leaf 自报 9 passed |
| Host 独立验证 | 收到 success observation 后运行冻结命令 | exit code 1，拒绝成功结算并创建修复 Attempt |
| T-05 attempt 2 | 新工作区带入失败 Attempt 快照；运行并修复旧措辞断言 | 约 277.629 秒；Leaf 报 pipeline 9 passed、tokens 5 passed |
| 最终结算 | Host 验证、关闭及发布 | terminal_yield outcome=complete，closure `7d85bef`，发布至本地 main |
| 晚到通知 | 旧的恢复 Agent 随后收到 stopped 通知 | 只说明进程/通知记录问题，不推翻 Complete 回执 |
| 复盘纠错 | 早先将耗时归因 SDD、模型冲突及虚构比例 | 撤回，改为按实际链路证据分析 |

### generation-1 Finding 的具体内容

旧 `test_spec_first_contract_formulation_and_lean_envelope` 仍断言 `≤ 8 tool turns`，并在编译 Token 时没有提供 T-04 已要求的显式 palette；`tests/test_pipeline.py` 只在 T-05 Write scope。Finding 的证据引用为当时测试文件第 322、341 行，不能直接套用当前已修改文件的行号。

T-03 修订后的命令：

```bash
python3 -m pytest tests/test_pipeline.py -k "test_handoff_packet_without_preexisting_html_and_template_surface_map"
```

### T-05 重试所获得的诊断

Host 返回 `TASK_VERIFICATION_FAILED`、exit code 1，并创建带失败快照的修复工作区；这一恢复能力确实存在。
但派发中的 `failure_site` 是 `unknown`，`diagnostic_traceback` 只有 `evidence://sha256/...` 引用。引用有助于完整性核对，却不等同于直接可用的失败测试名和 traceback。应改善诊断送达，而不是宣称框架没有证据或没有恢复功能。

## 5. 真正可量化的耗时

| 执行调用 | Agent ID | 工具报告 duration | 工具调用 | subagent_tokens |
|---|---|---:|---:|---:|
| generation-2 T-03 初次调用 | aaf568d3930478fca | 345706 ms | 35 | 52392 |
| generation-2 T-05 attempt 1 初次调用 | aedb5e24a1b6d10d4 | 508170 ms | 41 | 50816 |
| generation-2 T-05 attempt 2 | a923a54d813c1f712 | 277629 ms | 19 | 39481 |
| 上述三次合计 | — | 1131505 ms，即 18 分 51.505 秒 | 95 | 不作独立输出 token 合计 |

这些 duration 是三个 Agent 工具报告的执行区间，不是整个任务的总耗时。未覆盖恢复调用、其他 Task、初期设计讨论与部分协调过程；也不能从 duration 内部剥离模型等待、工具运行和环境等待。

最终 Host 输出中的 pytest 测试时间：pipeline 9 项为 0.13 秒，tokens 5 项为 0.33 秒。它们不包含全部解释器启动和 Host 包装耗时；只能证明测试主体很短，不能据此计算整个框架的效率倍数。

可以确认的放大点：启动失败后试探派发、局部失败往返主会话、错误成功声明后的重新定位、测试所有权错误触发规格恢复。
不能确认：95 次工具调用里多少是重复读取、整个数小时各环节占比、每次恢复是否发生完整上下文重建。

撤回此前无依据的结论：70% 时间用于治理、30x/50x/100x 膨胀、直接修改必定两三分钟完成、哈希/Git 是主要耗时源、sonnet 与 gpt 冲突导致本错误。

## 6. BOUND_RELEASE_UNAVAILABLE 的准确解释

只读调查定位的安装版本：`4.6.0-5fe8d7500c8eccca`。
源码根目录：`~/.claude/.loom-framework/releases/4.6.0-5fe8d7500c8eccca/claude-home/loom_runtime/source/loom_runtime/`。

| 代码位置 | 作用 |
|---|---|
| hook_router.py:75-157 | 根据 workspace、Run、lease、dispatch 选择 release |
| hook_router.py:191-196 | 捕获异常，返回 permissionDecision=deny，以及错误前缀加异常类名 |
| release_router.py:90-120 | 解析 Run 的 release 绑定 |
| release_router.py:154-185 | 校验 release manifest、组件 digest、源文件与 Python 环境 |

对外包装相当于：

```python
"BOUND_RELEASE_UNAVAILABLE:" + type(error).__name__
```

因此该报错表示 PreToolUse 在派发前拒绝工具调用。可能原因包括状态读取、绑定缺失、lease/release 错配、dispatch 不匹配、release 完整性不满足。这里只列源码分支，不推定本次命中了哪一项。

当前源码能够解释错误形态，但历史具体底层 reason 尚未取证。曾另见 component-mismatch 的摘要，不能未经关联便认定它与所有 Agent 拒绝是同一个故障。

`model: sonnet` 是绑定执行身份的一部分，并不能证明模型 API 路由故障；更换类型后成功也不是原路径已修复的证据。

## 7. 逃逸与根因：事实、推断、未知分开

| 问题 | 已证实事实 | 判断及边界 |
|---|---|---|
| 派发契约被转译 | 完整 agent_tool_inputs 被手工重写，指定执行器被替换 | Coordinator 越过适配边界；对具体耗时的贡献尚未计量 |
| 拒绝后换入口 | 内部 CLI 被用于继续状态操作 | 恢复路径偏离；不建议复现，不以“执行成功”证明安全 |
| 审批来源混淆 | user 改 human 后批准成功 | 仅证明参数被接受；原授权是否覆盖新 revision 必须核对，不伪称新人工批准 |
| Task 不可独立验证 | 前序验证依赖后序拥有的测试修改 | 任务编制错误；应修复行为及测试所有权闭包 |
| 局部修复提前上交 | 重复赋值、palette 输入、旧断言经再次催促才完成 | 已授权的局部修复没有一次闭合，不是必须取消隔离 |
| 结果关联不足 | Leaf 自述 pass，Host exit 1 | 自述不能替代工具事实；尚未证明是 cwd、代码快照还是报告失真 |
| 启动诊断被压缩 | Hook 只返回异常类型 | 明确的可诊断性缺陷，导致协调者无法按原因恢复 |
| 迟到通知 | 已完成交付后出现旧 Agent stopped | 需要关联生命周期与结算，但未发现账本被覆盖的证据 |
| 重复阅读 | 多次调用耗时长、工具调用多 | 尚无逐工具统计，不能直接宣称重复阅读是主要耗时 |

### 已经正确工作的机制

- 冻结验证命令与 scope 使任务边界可观察。
- Finding 将真实规格问题显式暴露，而非伪装成功。
- Host 独立复验拒绝了 T-05 的错误成功声明。
- 修复 Attempt 带入了失败快照，而非要求从零重新实现。
- 最终验证、集成、归档、发布均有回执。

优化应保留这些能力，修正错误输入、事实传递和恢复路径，而非拆掉防护。

## 8. 目标执行链路

1. OpenSpec 定义需求与可验证 Task；批准来源可追溯。
2. Binding 固定 revision、Git basis 与执行身份。
3. Host 消费原始派发对象，启动时固定 cwd、identity 和 dispatch 关联。
4. Leaf 从 Task 锚点读取必要实现与直接测试，完成最小修改。
5. Scope 内实现/断言失败在同一有效 Attempt 内局部修复；上下文未变化时不重建调查。
6. Host 独立验证具体快照。若失败，向恢复者送达摘要、失败定位和完整证据引用。
7. 语义变更回 Spec Loop；环境/路由故障走公开恢复，不冒充代码重试。
8. EventKernel 记录结果并执行已有结算、集成与发布；进程通知不替代持久化事实。

此链路不新增第二份 Brief、不另造 DAG、不用固定读取次数或工具步数限制理解能力。

## 9. 优化方案与验收

以下均为建议，尚未实施。先检查既有实现是否已有能力，仅修缺口。

| 优先级 | 所有者 | 最小优化 | 可运行验收 |
|---|---|---|---|
| P0 | Host 派发适配层 | 原样消费 agent_tool_inputs；执行器不可用时返回明确故障，不由模型换身份 | 派发输入与实际启动参数逐字段一致；错误分支不偷偷启动替代执行器 |
| P0 | Hook/release 路由 | 保留具体 reason、失败阶段、安全诊断引用及合法恢复动作，继续 fail closed | 构造 token 错配、组件不一致等不同错误，输出可区分且不泄密 |
| P0 | 启动上下文 | 由 Host 绑定工作区，不只写在 Prompt；复用已有 attempt/fence | Leaf 工具实际 cwd 与绑定一致；不能误在主工作区执行 |
| P0 | 审批适配层 | 批准引用真实用户动作及相应 revision，不把 actor 字符串当证据 | 缺失批准来源时不能产生声称人工批准的记录 |
| P1 | OpenSpec 任务编制 | 实现与必要断言属于同一可验证行为单元；无法独立交付则合并 | 每个 ready Task 能在前置已完成的基线上独立验证，无后置测试依赖 |
| P1 | Leaf/Host 恢复 | Scope 内局部修复闭环；直接送达失败测试与 traceback，不只给 hash URI | 一次普通断言失败无需 Coordinator 复述 Task；语义冲突仍返回 Finding |
| P1 | 验证证据接口 | 关联实际工作区、代码快照、命令、退出码与输出，保留独立复验 | 自述 pass/Host fail 时能定位两次验证差异；不以文字 success 结算 |
| P1 | Leaf 上下文提供 | 锚点定向读取、按内容版本复用；变更后失效；具体依赖需要时再扩展 | 同一未变内容不无故重读；文件变化后能读取新内容；不设僵硬 read 上限 |
| P2 | 恢复/事件消费 | 关联旧 Agent 通知与原 dispatch；核验既有幂等能力 | Complete 后收到旧 stopped 不重新派发；未结算 Attempt 才进入恢复 |
| P2 | 现有指标链路 | 增加少量阶段时间戳和耗时归属，不建立独立治理体系 | 能区分排队、模型、工具、验证、恢复及用户等待；父子时间不重复相加 |

### 实施顺序

1. 用历史失败样例确认启动路由具体 reason，并修复诊断传播及派发忠实性。
2. 校准 Task 的行为/测试闭包，贯通验证快照与局部失败现场。
3. 回放启动拒绝、自报与复验不一致、重启后迟到通知三个路径。
4. 对同类小任务作前后对照，比较首次修改时间、无增量读取、局部往返和总执行时间。

不预设节省百分比。没有分段证据前，不以模型速度或流程步骤数量替代性能测量。
不新增视觉、安装、部署门禁来解决本次 Harness 问题；这些仅在对应交付要求存在时验证。

## 10. 最终交付事实与限制

最终返回 `terminal_yield`，`outcome: complete`，包含 T-01 至 T-05。
- pipeline：9 passed。
- tokens：5 passed，另有 unknown pytest mark 警告。
- Host 输出另有 requests 依赖兼容性警告。
- 验证证明这两组测试通过，不等于全仓库测试全部通过。
- 未重新渲染 GPU 原型，未证明所有视觉问题消失。
- 未证明仓库修改已安装到所有运行环境。
- main 发布是本地 Git 目标分支更新，不能表述为远端推送或线上部署。

交付后工作区仍有原有及后续修改。本复盘不清理、不回滚、不根据当前文件反推历史 Attempt 内容。

## 11. 证据索引

Change：`repair-spec-prototype-design-loop`。
Delivery 前缀：`change:f8c2fe8ddb90cb2bf3ca0e8f9ca436a9eb0aa36cf6daac937e70126a7b4cfeb4`；世代分别为 `generation-1`、`generation-2`。

| 标识 | 意义 |
|---|---|
| 4770012 | 用户授权的限定基线 |
| ab74070 / d4eb670 / 2d10a08 | 历史摘要中的 T-01 / T-02 / T-04 集成提交 |
| dd88b738… | generation-1 revision |
| ecbd35d | 修订规格的 candidate 提交 |
| 582edd52… | generation-2 revision |
| 89a0e2e | T-03 集成提交 |
| 5f6e912 | T-05 集成提交 |
| 7d85bef01cb81788565db52804afd1ee534ffedd | closure 与发布 head，不是协议状态名称 |

归档路径：`openspec/changes/archive/2026-09-17-repair-spec-prototype-design-loop`。
授权历史来源：`/Users/hobart/.claude/projects/-Users-hobart-Codex-design-prototype-kit/6299c57f-b746-4755-bc3a-63b2d3c6bc0a.jsonl`。
本文件不复制完整历史、不包含凭据；历史摘要与直接工具返回的区别见第 1 节。

## 12. 仍需取证的问题

- 历史被拒绝派发的底层 ReleaseRoutingError reason，及其当时 release/lease/dispatch 对应关系。
- 所有 Attempt 的实际启动上下文、快照与验证输出，解释 T-05 自报/复验差异。
- 每次首次修改前的读取路径、重复读取内容版本及其必要性。
- 两代 Delivery 完整时间戳与暂停边界，拆开机器执行、模型等待和用户交互时间。
- 当前 Hook 源码与历史 release 是否一致；不得拿当前状态猜历史原因。

下一步应先完成上述定向取证与三个链路回放，再提出最小实现变更；不再凭无依据比例推导架构结论。
