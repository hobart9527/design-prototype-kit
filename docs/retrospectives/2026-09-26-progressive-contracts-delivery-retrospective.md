# Change 交付执行复盘报告

> 报告日期：2026-09-26  
> 标的 Change：`2026-09-25-progressive-contracts-consumer-alignment`  
> 涉及 Task：T-01 / T-02 / T-03 / T-04  
> 报告类型：未完成交付的过程复盘与根因分析  
> 参考文档：`docs/DELIVERY_FRAMEWORK_POSTMORTEM.md`（框架级上一次复盘）

---

## 1. 执行全景

### 1.1 Change 目标

本次 Change 涉及四个方向：

| Task | 核心目标 | 依赖 |
|---|---|---|
| T-01 | 渐进式 Schema Tier、meso slots、authored-only invariants、whole state identifier | 无 |
| T-02 | Tokens 单向派生、freshness fuse、lint E021 presence 语义修正 | T-01 |
| T-03 | Builder/Critic meso 消费、双维度评审、craft reference 重构 | T-01 |
| T-04 | L1/L2/L3 分级证据链、eval.yaml 路径修正 | 无 |

### 1.2 生命周期统计

| 维度 | 实际值 | 期望值 | 偏差 |
|---|---|---|---|
| 执行世代数 | 4（generation 1 → 4） | 1 | +300% |
| T-01 Attempt 次数 | 2（已达上限） | 1 | +100% |
| T-02 Attempt 次数 | 0 | 1 | 未执行 |
| T-03 Attempt 次数 | 0 | 1 | 未执行 |
| T-04 状态 | completed/inherited | completed | 一致 |
| 最终结果 | `completion_receipt: null` | `Complete` | **未完成** |
| 一次性交付成功率 | **0%** | ≥ 85% | 严重不合格 |

### 1.3 与上一次复盘的对比

上一次（`spec-prototype-benchmark-fidelity`）的结果是：最终 9/9 任务通过，只是中间经历了 4 个世代、FTRR=0%。

本次情况更严重：**T-01 在 Attempt 上限达到后进入 operator-decision，T-02 / T-03 完全未执行，Change 没有 Complete 收据**。

---

## 2. 核心事件时间线

### 阶段 1：制宪与 Write Scope 冲突

**发生事件：**

T-01 的 fixture `valid_ir` 使用 `execution_spec` 层级，`state_model` 已填充，`actions: []`（空数组）。  
T-02 当时的 `lint_spec_contracts.py` E021 逻辑将 `actions: []` 当成执行层 admission 失败。

**尝试修复路径（错误）：**

曾尝试将 `lint_spec_contracts.py` 纳入 T-01 Write Scope，被 Loom 正确拒绝：

```
SCHEDULING_UNDECLARED_ARTIFACT_DEPENDENCY:T-01:T-02:skills/spec-prototype/scripts/lint_spec_contracts.py
```

**最终正确路径：**

- 恢复单一写入所有权；
- 将 T-02 的正确语义（presence/null 判断，非 truthiness）明确写入 `tasks.md`；
- T-01 的验证范围调整为 `tests/test_contract_seam_fidelity.py`；
- T-02 独占 `lint_spec_contracts.py`。

**根因：** 跨 Task 的语义接缝在制宪阶段没有被完整预检，导致合流时才暴露冲突。

---

### 阶段 2：Successor parent 错误导致已接受 Task 丢失

**发生事件：**

Successor prepare 默认从 `main` HEAD 建立候选，而已完成 Task 存在于上一代 integration head 中，二者不同。

**后果：**

新 generation 丢失已接受 Task，需要重新执行不必要的工作。

**修复：**

通过手动指定 `--generation-parent` 解决：
- 使用 `d89e27cbebb4327ecb04f8c3c65f6cce7cd3dd9e`
- 再次使用 `2718a7e77e25c8c9bfbeb9c29bd771f10a671189`

成功生成 candidate：
- commit: `b298223a2be4a6b35c2ffa4bb4f111f0a932947f`
- revision: `5d68faa2bca4118e1c69e4e108f9ee5ea21b34313117a0a21e7518d992e8f93c`

**根因：** Successor 没有自动绑定上一代最新 integration head，依赖操作方手动识别。

---

### 阶段 3：Host Hook 环境缺失

**发生事件：**

第一次实际执行时，Host PreToolUse Hook 无法找到：
```
LOOM_RUNTIME_HOME=（空）
LOOM_EVENT_STORE=（空）
```

导致 Agent 还未进入 Attempt 就被拦截：
```
WORKSPACE_AUTHORITY_UNRESOLVED
```

**后续：**

该问题暂时被绕过，T-01 最终能够进入 Attempt，但框架未根治。

**根因：** Host Hook 没有默认 runtime 自动发现，也没有和 Loom Kernel 共享统一故障总线，环境缺失表现为普通 Agent 任务失败而非 Host prerequisite。

---

### 阶段 4：Delivery ref 误用

**发生事件：**

第一次 settlement 使用了：
```
change:2026-09-25-progressive-contracts-consumer-alignment:generation-3
```

实际应使用：
```
change:d58db23a9a60e563d92362e731582b71f671bc4f07d092b13c92aaeceb98983f:generation-3
```

导致：
```
TASK_RUN_NOT_FOUND
```

**根因：** Delivery ref 没有被作为不可变协调上下文持续保留，上下文压缩后误用 Change ID 代替运行引用。

---

### 阶段 5：T-01 Attempt 1 — EMPTY_MUTATION

**发生事件：**

Agent 判断 T-01 的生产实现在 integration baseline 中已经存在，冻结验证器可通过，不需要产生文件变更。

Host 记录：
```json
{
  "changed_files": [],
  "failure_kind": "implementation",
  "reason": "EMPTY_MUTATION",
  "failure_summary": "Task declared write scope but produced 0 file changes; author the required changes in scope."
}
```

**后果：**

Host 消耗了 Attempt 1，创建 recovery Attempt 2。

**根因：** 当前 Host 把 `changed_files: []` 直接判定为失败，不支持 **"基线已满足 Task，verifier 通过"** 的合法 no-op 路径。

---

### 阶段 6：T-01 Attempt 2 — VerificationFailed

**发生事件：**

Agent 在授权范围内修改了 `tests/test_contract_seam_fidelity.py`，增加约 79 行测试，涵盖：
- `intent_spec` 编译
- 无 authored invariant → `invariants` 为空
- `interaction/inspecting` 完整透传
- 三个 meso slots
- massing fallback
- authored invariant 保留
- Stage-1-only IR 请求 `execution_spec` 时失败

Agent 报告：
```
基线：2 passed
修改后：3 passed
```

Host 最终结算结果：
```json
{
  "category": "operator",
  "failure_family": "VerificationFailed",
  "reason": "attempt-limit-reached",
  "required_action": "operator-decision"
}
```

**关键矛盾：**

Leaf 报告局部验证通过 ≠ Host 完成结算。Host 的完整验证链包含：
1. scope admission（changed_files 是否在 Write Scope 内）
2. 冻结 Verify with 执行
3. commit + integration
4. immutable head 持久化

任何一个环节失败都不会产生 accepted receipt。但 Host 返回的错误信息仅有 `VerificationFailed`，没有披露具体是哪个环节失败、哪条断言失败、使用的是哪个 tree。

**根因：** 
1. Host 验证失败的诊断证据不足，无法从外部还原失败链；
2. Leaf 的局部验证与 Host 的全链路验证之间没有充分的校准机制。

---

### 阶段 7：Attempt 上限 → operator-decision

**发生事件：**

T-01 达到 Attempt 上限（2次），进入：
```
category: operator
reason: attempt-limit-reached
required_action: operator-decision
```

后续尝试 `loom delivery settle --unobserved` 进行客观恢复结算，返回：
```
category: repair
reason: workspace-authority-conflict
required_action: delivery.ensure
```

再次 `step`/`ensure` 仍返回 Attempt 上限。

**当前状态：**

| Task | 状态 |
|---|---|
| T-01 | Attempt limit 达到，operator-decision 中 |
| T-02 | 未执行 |
| T-03 | 未执行 |
| T-04 | completed/inherited |
| completion_receipt | null |
| terminal | null |

**根因：** Attempt 上限超出后没有合法的自动恢复路径，只能进入 operator decision 或正式 abandon。

---

## 3. 已有效修复的问题

### 3.1 T-01 核心生产语义

局部 Agent 验证（非 Host 结算事实）显示以下语义已实现：

- `intent_spec` / `execution_spec` 渐进式 tier；
- `layout_directives.massing_pattern`；
- `interaction_spec.kinematics`；
- `visual_directives.data_syntax`；
- authored-only invariants（无 authored 源时不注入 telemetry/GPU 模板）；
- `interaction/inspecting` 作为完整 ID 透传，不被空格拆分；
- massing fallback（未声明 massing 时不阻止编译）。

⚠️ **注意：** 以上均基于 Agent 局部报告，尚无 Host 接受收据，不能作为 Loom 账本事实。

### 3.2 Task 文件所有权冲突已解决

- T-01 不再触碰 `lint_spec_contracts.py`；
- T-02 独占该文件；
- tasks.md 明确记录 E021 presence 规则的目标语义；
- 两个 Task 的 Write Scope 不再重叠。

### 3.3 跨 Task 接缝已显式化

`tests/test_contract_seam_fidelity.py` 新增测试覆盖了 T-01/T-02 边界：
- Schema tier admission；
- authored invariant 行为；
- whole state identifier；
- meso slots；
- Stage 1 边界。

### 3.4 Successor 正确父节点的原则已确认

明确了：successor 必须从上一代 integration head 继承，而非 stale branch HEAD。

---

## 4. 尚未完成的问题

| 类别 | 具体内容 |
|---|---|
| **T-01 Host 接受** | 2次 Attempt 均未产生 accepted receipt，operator-decision 中 |
| **T-02** | `lint_spec_contracts.py` E021 语义未修复；tokens 单向派生未实现；freshness fuse 未实现；`out_of_sync` 检测未实现 |
| **T-03** | Builder meso 消费未实现；Critic 双维度评审未实现；craft references 未重构 |
| **Change 级验证** | immutable integration head 全量验证未执行 |
| **Complete receipt** | null |

---

## 5. 根因分析

### 根因 1：Host 不支持 Baseline-Satisfied No-op

**描述：**

当任务语义已在 integration baseline 中满足时，正确行为是：
```
run verifier on baseline → pass → emit accepted receipt
```

当前行为是：
```
changed_files: [] → EMPTY_MUTATION → consume Attempt → require recovery
```

**影响：**

- 消耗不必要的 Attempt 额度；
- 迫使 Agent 制造 dummy mutation（添加冗余测试）以满足 mutation obligation；
- 破坏"收据可信"原则（dummy mutation 的收据不能证明任务完成）。

**建议修复：**

Host 在 `changed_files: []` 时按顺序判断：
1. Write Scope 是否已声明；
2. 冻结 Verify with 是否通过；
3. 已通过 → emit `VERIFIED_NOOP` accepted receipt；
4. 未通过 → emit `IMPLEMENTATION_REQUIRED` 失败。

---

### 根因 2：跨 Task 语义接缝发现过晚

**描述：**

T-01 的 `valid_ir` fixture 与 T-02 的 E021 逻辑存在隐含冲突，直到集成阶段才爆红。

**影响：**

- 浪费 generation；
- 消耗 Attempt；
- 产生不必要的 finding；
- 增加操作方工作量。

**建议修复：**

在 generation binding 后，增加静态契约预检（cross-task seam preflight）：
- 收集各 Task 的 Verify with 冻结命令；
- 提取共享 fixture、Schema 字段、错误码；
- 识别 Task A 的 verifier 是否依赖 Task B 尚未实现的语义；
- 输出 finding，路由到 authoring 修正；
- 不修改任何 Task 的所有权。

---

### 根因 3：Successor 无法自动继承最新 integration head

**描述：**

Successor prepare 默认从 `main` HEAD 建立候选，而 integration head 可能领先于 `main`。

**影响：**

- 已接受 Task 丢失；
- 新 generation 重复执行旧任务；
- 增加 Attempt 消耗和错误风险。

**建议修复：**

```
loom spec prepare 自动查询：
  1. 当前 Change 最新 generation 的 integration head
  2. 以该 head 为 --generation-parent
  3. 在 Binding 中固化并记录
  4. Coordinator 不需要手动传递 hash
```

---

### 根因 4：Host 验证失败诊断证据不足

**描述：**

`VerificationFailed` 只是分类，不是完整诊断。外部无法还原：
- 使用的 tree hash；
- verifier 完整输出；
- 失败的具体断言；
- 是代码失败、环境失败还是接缝失败。

**影响：**

- Coordinator 无法精确修复 Host 真正看到的失败；
- Agent 只能根据 Leaf 本地工作区猜测，猜测结果可能与 Host 实际 tree 不一致；
- 每次 Attempt 都在黑箱中消耗，没有积累诊断价值。

**建议修复：**

Host 返回 `VerificationFailed` 时应附带：

```json
{
  "attempt_commit": "...",
  "integration_head": "...",
  "verify_command": "python3 -m pytest -q ...",
  "exit_code": 1,
  "stdout": "...",
  "stderr": "...",
  "failed_assertions": ["..."],
  "failure_kind": "code | environment | contract | integration",
  "scope_result": "admitted | rejected"
}
```

---

### 根因 5：Host Hook 缺少 runtime 自动发现

**描述：**

`LOOM_RUNTIME_HOME` 和 `LOOM_EVENT_STORE` 缺失时，Host Hook 直接阻断 Agent，表现形式与普通代码失败一致。

**影响：**

- 消耗 Attempt（或阻止 Attempt 启动）；
- 没有明确的 `Host prerequisite missing` 分类；
- Coordinator 无法区分"任务失败"和"环境未就绪"。

**建议修复：**

Host Hook 按优先级自动发现：
1. 显式环境变量；
2. repository-local `.loom/runtime`；
3. session 级 runtime；
4. 默认安装路径；
5. 以上都不存在 → emit `finalization_blocked: HOST_PREREQUISITE_MISSING`，不消耗 Attempt。

---

### 根因 6：Kernel 与 Host 缺少统一故障总线

**描述：**

故障分别出现在 EventKernel、Host Hook、Attempt workspace、Leaf Agent、verifier、settlement、integration、publication 各层，没有统一的故障事件模型。

**影响：**

- Coordinator 收到来自不同层的异构错误消息；
- 无法自动路由到正确的恢复机制；
- 每次 Attempt 失败都要人工分析原因并决定下一步。

**建议修复：**

建立统一 `FailureFact` 模型：

```
FailureFact {
  layer: kernel | host | leaf | verifier | integration | publication
  family: implementation | contract | environment | authority |
          observation | integration | publication
  retryable: boolean
  recovery: auto_repair | reconcile | new_attempt | successor | operator
  evidence: immutable CAS refs
}
```

由 Kernel 统一决定恢复策略，而不是让每一层各自返回异构错误。

---

## 6. 框架自愈缺口总结

| 缺口 | 当前状态 | 是否需要 operator 介入 |
|---|---|---|
| baseline-satisfied no-op | 不支持，消耗 Attempt | 是（当前无法绕过） |
| 跨 Task seam preflight | 不存在，合流时才发现 | 间接（需要 authoring 修正） |
| successor 自动继承 integration head | 不支持，需手动指定 | 是（当前需要手动传 hash） |
| Host 验证失败诊断 | 仅返回分类，无具体证据 | 是（无法精确修复） |
| Host Hook runtime 自动发现 | 不支持，环境缺失→普通失败 | 是（当前无法自愈） |
| 统一故障总线 | 不存在，各层异构错误 | 是（每次人工分析） |
| Attempt limit 后合法恢复 | 只有 operator-decision 或 abandon | 是（必须 operator 介入） |

---

## 7. 建议的后续执行步骤

### 第一步：处理 T-01 operator-decision

不能执行的操作：
- 重派已耗尽的 dispatch token；
- 手动修改 Host lease / worktree；
- 伪造 observation 或结算事实；
- 以局部 `3 passed` 报告代替 Host accepted receipt；
- 直接跳过 T-01 启动 T-02。

应执行的操作（二选一）：

**选项 A — 保留当前 generation，operator 授权额外 Attempt：**
如果框架支持 operator 授权超出默认 Attempt 上限的恢复执行，则保留当前 generation、补充 Attempt、重新执行 T-01。

**选项 B — 正式 abandon 当前 generation，创建 successor：**
```
loom delivery abandon \
  --delivery-ref change:d58db23a9a60e563d92362e731582b71f671bc4f07d092b13c92aaeceb98983f:generation-4 \
  --reason "T-01 attempt-limit-reached, no recovery path available" \
  --execution-stopped --leases-released
```

然后以 generation-4 的 integration head 为 parent 创建 successor，继续 T-01。

### 第二步：T-01 被 Host 接受后，执行 T-02

重点验证：
- `actions: []` + populated `state_model` → lint clean；
- `intent_spec` 不要求 execution 字段；
- `tokens.css` 手动修改 → `out_of_sync` → downstream 拒绝；
- palette-only 修改不能绕过 freshness fuse；
- `interaction/inspecting` 在 craft stack 中完整透传。

### 第三步：T-02 完成后，执行 T-03

重点验证：
- Builder 根据 `massing_pattern` 生成空间层级指导；
- Builder 不对 dense console 套用装饰性默认值；
- Critic 的 `display: none` 阻断规则；
- Critic 对 genericized flat UI 的认知维度阻断。

### 第四步：Change 级最终验证

- 在 immutable integration head 上执行全量 Change 级验证；
- 检查 OpenSpec closure diff；
- 处理 publication overlap；
- 等待 Loom 返回 `Complete` receipt。

---

## 8. 成功收据的唯一定义

本 Change 完成的充要条件是：

```
Complete receipt
  ├── T-01: accepted (Host commit + integration verified)
  ├── T-02: accepted (Host commit + integration verified)
  ├── T-03: accepted (Host commit + integration verified)
  ├── T-04: accepted/inherited (Host verified)
  ├── immutable integration head final verification: passed
  ├── closure diff: clean
  └── publication: committed
```

任何局部 Agent 测试通过报告、局部 pytest 输出、git log 或 checkbox 均不能替代以上事实。

---

## 9. 附录：关键标识符

| 标识符 | 值 |
|---|---|
| Change ID | `2026-09-25-progressive-contracts-consumer-alignment` |
| 当前 generation | 4 |
| Delivery ref | `change:d58db23a9a60e563d92362e731582b71f671bc4f07d092b13c92aaeceb98983f:generation-4` |
| T-01 Attempt 1 commit | `79f5a0745a76d5b5819cd8e37f3392eb1433467f` |
| T-01 Attempt 2 commit | `c7898c029e731f795f028abca697719ca81d5b59` |
| T-01 last integration head | `2718a7e77e25c8c9bfbeb9c29bd771f10a671189` |
| Candidate commit (gen-4) | `b298223a2be4a6b35c2ffa4bb4f111f0a932947f` |
| Revision hash | `5d68faa2bca4118e1c69e4e108f9ee5ea21b34313117a0a21e7518d992e8f93c` |
