# 交付框架执行链路与一次性交付率根因复盘

> 报告日期：2026-09-18  
> 标的对象：`spec-prototype-benchmark-fidelity` 交付生命周期（Loom 调度管辖 + OpenSpec + Leaf Agent 空气隔离执行体系）  
> 目的：剖析从意图提出、基线治理、分代交付（Generation 1 ~ 4）至最终合入的全链路摩擦与故障，定位导致“一次性交付成功率（First-Time-Right Rate）”低下的系统性缺陷，并给出可落地的架构治理方案。

---

## 1. 执行全景与关键指标复盘

在本次交付中，目标是将存在“Skill 模拟逃逸”的基准评测套件重构为具备真实证据边界、分层度量、案例四件套隔离与阻断感知的可信基准体系。任务规划共 9 项（T-01 至 T-09）。

### 1.1 生命周期统计

| 维度 | 实际消耗 / 统计值 | 工业级期望基线 | 偏差度 |
| :--- | :--- | :--- | :--- |
| **交付世代数 (Generations)** | 4 代（Gen 1 -> Gen 2 -> Gen 3 -> Gen 4） | 1 代（直接通过） | +300% |
| **Leaf Agent 派发总次数** | 14 次（多次重派、跨代补偿） | 9 次（每任务 1 次） | +55.6% |
| **人工审批轮次** | 4 次（每代候选准备均需一次显式授权） | 1 次（终态准入） | +300% |
| **一次性交付成功率 (FTRR)** | **0%**（未能在 Generation 1 单轮收敛关闭） | $\ge 85\%$ | 严重不合格 |
| **最终结果** | 9/9 任务通过，Commit `2b564dd` 完整合入 | 闭环交付 | 一致 |

---

## 2. 一次性交付失败的四大核心归因分析

通过对本次 4 个世代、数十次调度日志、Git 拓扑演化及中间拦截事件的逐行回溯，一次性交付率低下的核心原因并非底层代码编写能力不足，而是**执行框架在“状态对齐”、“契约边界”、“验证隔离”和“调度协议”四个维度存在严重摩擦**。

### 根因 1：基线血统断裂与工作区“幽灵基线”认知冲突（Lineage Split Trap）

- **现象**：
  在 Generation 1 派发 T-01 和 T-04 时，Leaf Agent 频频报错 `Anchor file absent: benchmarks/run_benchmark.py`，直接导致第一代交付中断。
- **根因分析**：
  1. 用户在前期会话中要求“冻结基线”，形成了本地未推送的基线 Commit `5af898b`（包含了 `benchmarks/` 目录源码）。
  2. 但主仓库工作区处于分支 `main`（HEAD 为 `58cc457`），该提交点上 `benchmarks/` 处于未跟踪或未合并状态。
  3. Loom 的工作区分离引擎在创建工作树时，严格基于绑定 Commit（以主干为祖先）拉取分支，导致隔离工作树中根本不存在该被测文件。
  4. **系统性缺陷**：框架缺乏“交付前工作区前置断言（Workspace Pre-flight Assertion）”。调度层在没有验证 Target Commit 是否包含 Anchors 文件的情况下就盲目签署交付绑定，将一个确定性会失败的环境推给了 Leaf Agent。

### 根因 2：验证命令副作用引发工作区自污染（Verifier Self-Pollution Loop）

- **现象**：
  在 Generation 2 与 Generation 3 中，所有 9 项任务均已在 Leaf Agent 中成功跑通并提交了 Observation，但在最终 Host 终审（Final Settlement）时，框架连续抛出 `FINAL_VERIFICATION_MUTATED_WORKSPACE`，阻断交付关闭，迫使回退并开启下一代。
- **根因分析**：
  1. `tasks.md` 中为 T-08 编写的验证命令为：
     ```bash
     python3 benchmarks/run_benchmark.py --label baseline-check --rounds 1 && python3 -c "..."
     ```
  2. 该命令并非纯粹的**只读断言（Read-Only Probe）**，而是触发了完整的基准执行，在工作树下动态生成了 `benchmarks/spec-prototype/results/run_20260918_xxxxxx/` 目录。
  3. Loom 的安全铁律要求：交付终审时工作区必须完全纯净，任何未被声明在 Write Scope 内或在验证期间新生的未跟踪文件都被视为非预期副作用（Mutated Workspace）。
  4. **系统性缺陷**：
     - **验证契约语义混淆**：把“生产行为（Run benchmark to generate data）”与“验证断言（Assert data exists）”耦合在同一个 `Verify with` 字段中。
     - **终审防护机制僵硬**：Host 在执行全量回归检查时，在当前工作区直接重放所有命令，却未对验证期间允许产生的临时目录提供沙箱隔离（Scratchpad Isolation）或自动回滚机制。

### 根因 3：任务测试所有权与前置依赖闭包错位（Test Ownership Inversion）

- **现象**：
  在早期生成任务中，任务被分解为过细的单点切片，导致某些任务的“行为实现”与“验证检查”被割裂在两个不同的 Task 中。
- **根因分析**：
  1. 某个前置任务 T-A 改变了运行时数据结构（增加了 `run_meta` 字段），但断言此字段的测试用例文件所有权被分配在后置任务 T-B 的 Write Scope 中。
  2. 结果导致 T-A 在隔离工作区中无法修改测试，如果运行现有测试则由于测试未更新而挂掉；若跳过测试则无法给出证明。
  3. **系统性缺陷**：任务分解过度碎片化，违背了“**每个 Task 必须是一个垂直可独立交付切片（Vertical Executable Slice）**”的原则。契约闭包设计不严密，导致人为制造了执行阻塞。

### 根因 4：主会话调度器越界代行与空气隔离失真（Coordinator Role Drift）

- **现象**：
  当遇到状态分歧时，主会话经常需要通过手动 `git commit-tree`、手工合成提交、强制 `git reset` 等底层 Git 破坏性手段来修补框架与工作区之间的分歧。
- **根因分析**：
  1. 根据 `CLAUDE.md` 规范，主会话作为 Coordinator 必须严格空气隔离，严禁直接篡改业务源码。但当 Loom Host 的发布通道被 `PUBLICATION_LOCAL_OVERLAP` 阻断时，系统没有提供标准的“干净接管协议”或“状态同步指令”。
  2. 框架抛出错误码后，缺少确定性的下一步指引（Next-Step Recipe），迫使 Coordinator 介入底层 Git Plumbing 操作来完成树拓扑缝合。
  3. **系统性缺陷**：Host 与 Coordinator 之间的协议缺乏**自愈原语（Self-Healing Primitives）**，把 Git 冲突和本地重叠的处理责任外溢给了大模型提示词工程。

---

## 3. 执行链路全景时序对照（As-Is vs. To-Be）

```
[ 当前现状 (As-Is): 多代震荡模型 ]
User Prompt ──> 缺少前置核验 ──> 绑定 Gen 1 ──> 发现基线缺失 (Fail)
                                 │
                                 ├──> 合并基线 ──> 重新审批 ──> 绑定 Gen 2
                                                     │
                                                     ├──> T-01..T-09 执行完毕
                                                     ├──> 终验副作用污染 (Fail)
                                                     │
                                                     ├──> 修复验证命令 ──> 重新审批 ──> 绑定 Gen 3/4
                                                                          │
                                                                          └──> 最终通过 (高耗时、低效率)

----------------------------------------------------------------------------------------------------

[ 目标模型 (To-Be): 零副作用确定性单代闭环 ]
User Prompt ──> Pre-flight Check (基线/锚点/依赖闭包) ──> 单次绑定 Gen 1
                                                             │
                                                             ├──> 垂直切片派发 (Leaf Agent 并行)
                                                             ├──> 沙箱隔离验证 (Scratchpad Execution)
                                                             └──> 纯净终审入库 (一次性成功 FTRR=100%)
```

---

## 4. 框架级系统性改进与落地行动建议

为彻底解决此类执行摩擦，消除“任务做对了却交付不进去”的死循环，建议从以下 4 个方面进行框架改造：

### 4.1 引入 `loom spec lint` 交付前静态走查（Pre-flight Linter）
在 `loom spec prepare` 或绑定之前，强制进行静态拓扑检查：
1. **Anchor 存在性断言**：自动检查每个 Task 声明的 `- Anchors:` 文件在当前的 base commit 中是否存在，缺失则直接拦截并阻断 candidate 准备，杜绝带病进入调度。
2. **验证命令无害性检查（Idempotency Lint）**：检查 `Verify with:` 是否包含潜在的写入操作（如 `--out`、重定向 `>`、未重定向运行 runner 等）。强约束验证命令必须是**纯只读检查**。

### 4.2 确立垂直切片原则，禁止“行为与验证跨 Task 分离”
重塑 OpenSpec 任务编写规范：
1. 单个 Task 必须包含“生产代码修改 + 对应专项验证或单测断言修改”。
2. 禁止建立“Task 1 写功能，Task 2 写测试”的水平分工；每一个 Task 必须自带完整的 Red-Green 证据闭环。

### 4.3 验证环境引入“写写重定向/临时沙箱（Ephemeral Verification Sandbox）”
Host 在终审执行 `verification_command` 时：
1. 默认在隔离的虚拟覆盖层或内存文件系统（Tmpfs）上执行，或者在验证前后自动执行 `git status --porcelain` 差异回滚。
2. 即使验证命令意外在 `benchmarks/results/` 下写入了日志或结果文件，Host 也能自动安全丢弃这些验证衍生品，而不是将合法完成的任务裁定为 `FINAL_VERIFICATION_MUTATED_WORKSPACE`。

### 4.4 提供结构化自愈命令，收口 Git 底层破坏性操作
针对 `PUBLICATION_LOCAL_OVERLAP` 或 `FINAL_VERIFICATION_MUTATED_WORKSPACE`：
1. CLI 应当直接输出受管命令（例如：`loom delivery reconcile --prune-artifacts` 或 `loom delivery adopt --force-clean`）。
2. 禁止让 Coordinator 编写底层 `git commit-tree`、`git mktree` 等脆弱的 shell 脚本，保证所有状态变迁全部由 Host 审计账本驱动。

---

## 5. 结论

本次交付在**业务与技术实质上完全达到了预期**：彻底拔除了虚假宣称的评测逃逸，建立了真实的证据分层、六案例四件套和阻断探查机制。

但**交付工程链路上的低效率暴露了当前调度框架在工程边界定义上的粗糙**。一次性交付率低不是因为模型能力不足，而是因为**验证副作用自污染**与**基线未预检**两道制度性漏洞。落实上述 4 项框架改进，将使后续类似的大规模原型与基准迭代从“4 代往复”回归到“单代闭环交付”。
