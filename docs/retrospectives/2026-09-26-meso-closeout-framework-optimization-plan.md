# Loom 交付框架系统性瓶颈根因复盘与长效优化方案

> **文件路径**：`docs/retrospectives/2026-09-26-meso-closeout-framework-optimization-plan.md`  
> **报告日期**：2026-09-26  
> **标的 Change**：`2026-09-26-meso-closeout-hardening` (T-01 / T-02 / T-03)  
> **核心议题**：消除导致任务执行从预期 ≤10 分钟膨胀至 ~85 分钟的框架摩擦根因，建立高韧性、确定性的交付底座。

---

## 1. 交付全景与耗时指标拆解

本次交付的核心目标是对 `spec-prototype` 落地三项中观收尾硬化：
1. **T-01**：`core-workflow.md` 退役存根与基准套件 `REQUIRED_SKILL_ENTRIES` 白名单解耦；
2. **T-02**：`assemble_envelope.py` 动态抽取 Canonical IR 视口契约，并补充回归测试；
3. **T-03**：`spec-prototype-critic.md` 注入 L1/L2/L3 分级降级证据链协议。

### 1.1 耗时对比：实际 vs 理想

| 关键执行环节 | 实际耗时 | 耗时占比 | 优化后期望耗时 | 节约时间 | 核心耗时属性 |
|---|---|---|---|---|---|
| **Authoring 制宪与准备** | 8.0 min | 9.4% | **1.0 min** | -7.0 min | 格式兼容与语法试错摩擦 |
| **Generation 1 / Attempt 1 并行** | 29.6 min | 34.8% | **2.5 min** | -27.1 min | **T-02 遭遇写作用域截断陷阱** |
| **Finding 归因与人工介入决策** | 7.0 min | 8.2% | **0.0 min** | -7.0 min | 调度层误判归因导致的空转 |
| **Generation 2 重新制宪与审批** | 7.0 min | 8.2% | **0.0 min** | -7.0 min | 跨世代推翻重来的重协商成本 |
| **Generation 2 重跑 (含 T-03 重复)** | 22.0 min | 25.9% | **0.0 min** | -22.0 min | 缺乏跨世代 CAS 继承导致的冗余计算 |
| **基线测试破损修复 (T-01)** | 6.2 min | 7.3% | **0.0 min** | -6.2 min | 历史基线与候选规则时空破损 |
| **终态全量复验与 CAS 发布** | 5.2 min | 6.1% | **1.5 min** | -3.7 min | 机械执行与网络推送 |
| **全生命周期总计** | **~85.0 min** | **100%** | **≤ 5.0 min** | **-80.0 min (降幅 94%)** | **非业务摩擦占 94%** |

### 1.2 工业级效能指标

- **有效代码增量**：3 个核心文件，净增约 120 行代码；
- **真实验证开销**：全量 363 项单元测试仅需 4.5 秒；
- **有效编码时间**：约 5 分钟；
- **无效摩擦损耗**：约 80 分钟（占总耗时 94%）；
- **一次性交付通过率 (FTRR)**：0%（Gen 1 失败，经 Gen 2 才最终闭环）。

---

## 2. 五大系统性根因深度剖析

### 根因 1 (语法层 - P0)：OpenSpec Parser 语法解析脆弱，折行截断破坏 Write Scope

- **现象**：  
  在 `tasks.md` 中，当 `Write scope` 声明多个文件并使用多行缩进书写时：
  ```markdown
  - Write scope: 
    skills/spec-prototype/scripts/assemble_envelope.py,
    tests/test_lean_builder_payload.py
  ```
  底层正则/单行解析器仅提取了第一行甚至将字段视为空，导致生成 Leaf Dispatch 描述符时，`scope` 数组仅包含首个文件，甚至丢失了测试文件。
- **后果**：  
  Leaf Agent 在修改 `tests/test_lean_builder_payload.py` 时被沙箱 Hook 判定为 `MUTATION_SCOPE_OUTSIDE_ATTEMPT` 并物理拦截。由于缺乏测试写权限，T-02 既无法建立失败用例基线，也无法保存测试，在沙箱中苦苦挣扎 29.6 分钟、耗费 71 次工具调用后被迫超时。

---

### 根因 2 (调度层 - P0)：Host 归因状态机反转，将规范缺陷 (Spec-Blocker) 降级为代码缺陷 (Code-Error)

- **现象**：  
  当 Leaf Agent 因写作用域不足多次受阻后，其生成的最终观察中已明确给出提示（缺少测试文件写入权限）。此时本质上属于 **L1 制宪阶段的声明不足（`spec-blocker`）**。
- **后果**：  
  Host 调度器没有将其识别为“需要原位修复 Task 规范并就地升级”，而是降级判定为 Leaf Agent 的普通代码实现失败（`code-error`），直接重试 Attempt。在 Attempt 上限耗尽后，强制作废整个 Generation 1，引发了长达 14 分钟的人工排查、重新制宪（Gen 2）与重新审批。

---

### 根因 3 (沙箱层 - P1)：Leaf 缺乏变异拦截感知与 3-Strike 快速熔断机制

- **现象**：  
  当 Leaf 在隔离 Worktree 中调用 `Edit` 或 `Write` 触碰未授权路径时，沙箱 Hook 仅返回权限错误。但 LLM 缺乏全局系统视野，往往误以为是自己的 patch 格式有误、文件路径相对关系不对或代码逻辑未跑通，进而不断调整 prompt、转换工具方式尝试绕过。
- **后果**：  
  Leaf 陷入防御性自我解释循环，单次 Attempt 疯狂空转几十轮，白白吞噬 180 秒硬性超时与巨量 Token 配额，加剧了执行时间延宕。

---

### 根因 4 (演进层 - P1)：历史基线不可变性与候选套件演进时空破损 (Time-Space Bleed)

- **现象**：  
  T-01 将 `REQUIRED_SKILL_ENTRIES` 改为 `core-kernel.md`。当基准套件运行 `ensure_baseline()` 恢复历史只读控制组 `v10.2.1-stable` 时，基准加载器强行用候选套件最新的条目规范去校验历史版本。而历史版本在设计上根本不存在 `core-kernel.md`，导致基准断言瞬间崩溃（`BenchBlocked: missing references/core-kernel.md`）。
- **后果**：  
  Leaf Agent 被迫在业务目标之外花费 11.8 分钟去排查基准测试的历史基线代码，迫使引入 `REQUIRED_BASELINE_ENTRIES` 进行热修。

---

### 根因 5 (存储层 - P2)：跨世代 (Generation) 交付缺乏 CAS 内容寻址继承协议

- **现象**：  
  在 Generation 1 中，T-03（Critic 降级协议）已经以满分通过验证并落盘。但由于 T-02 的 `tasks.md` 语法问题导致 Generation 1 被作废，进入 Generation 2 后，系统将所有 Task 状态置为未执行。
- **后果**：  
  T-03 被迫在 Generation 2 中从头重新派发、重新检出、重新跑单测，无谓空耗 22 分钟的宝贵资源。

---

## 3. 五项长效工程解决方案

```text
[L1 规范层]                                    [L2 调度层]                                 [L3 沙箱层]
┌─────────────────────────┐                  ┌────────────────────────┐                  ┌─────────────────────────┐
│ 方案 1: 多行语法容错    │                  │ 方案 2: Fast-Track     │                  │ 方案 3: 3-Strike 熔断   │
│ & 覆盖率静态预检 (P0)   │ ──(合法契约)───► │ 规范缺陷自愈通道 (P0)  │ ──(定向派发)───► │ 防御性循环快速退出 (P1) │
└─────────────────────────┘                  └────────────────────────┘                  └─────────────────────────┘
            ▲                                             │                                           │
            │                                             ▼                                           ▼
┌─────────────────────────┐                  ┌────────────────────────┐                  ┌─────────────────────────┐
│ 方案 4: 历史/候选双轨   │                  │ 方案 5: CAS 内容寻址   │                  │ 零摩擦交付终态          │
│ 基线架构解耦 (P1)       │                  │ 跨世代增量继承 (P2)    │                  │ 全流程 ≤ 6 分钟         │
└─────────────────────────┘                  └────────────────────────┘                  └─────────────────────────┘
```

### 方案 1 (P0)：OpenSpec Parser 语法容错引擎与静态覆盖率预检

#### 1. 语法容错扩展
重构 `tasks.md` 解析器，支持标准的行尾折行、缩进列表以及逗号混合语法：
```python
# 核心逻辑示意：多行 Write scope 解析器
def parse_write_scope(raw_block: str) -> list[str]:
    lines = raw_block.strip().splitlines()
    scope = []
    for line in lines:
        cleaned = re.sub(r"^[-*]\s*", "", line.strip())
        parts = [p.strip() for p in cleaned.split(",") if p.strip()]
        scope.extend(parts)
    return sorted(set(scope))
```

#### 2. 前置静态覆盖率断言（Pre-flight Scope Coverage Probe）
在 `loom spec prepare` 生成 Candidate 时，执行语义交叉静态检查：
- 规则：若 `Verify with` 字段中显式包含某个测试文件（如 `tests/test_foo.py`），且该 Task 的描述中包含“Add tests”或“Extend tests”关键字，则该测试文件必须出现在 `Write scope` 中；
- 违规处理：直接在 `prepare` 阶段报错阻断，禁止带病进入 Leaf 执行。

---

### 方案 2 (P0)：Host 归因状态机与 Fast-Track 规范自愈通道

#### 1. 拦截错误语义升级
当 Leaf 发生 `MUTATION_SCOPE_OUTSIDE_ATTEMPT` 时，Hook 返回带自解释的分类信息：
```json
{
  "error": "MUTATION_SCOPE_OUTSIDE_ATTEMPT",
  "path": "tests/test_lean_builder_payload.py",
  "finding_class": "spec-blocker",
  "remedy": "EXTEND_TASK_WRITE_SCOPE"
}
```

#### 2. 原位协调修复（In-situ Task Scope Harmonization）
Host 调度器捕获到 `spec-blocker: scope_insufficient` 后，不作废 Generation，不触发重派重试，而是直接在协调层拉起快速补丁（Fast-Track Patch），更新当前 Task 的 `Write scope` 声明，重置 Attempt 计数器并就地恢复。

---

### 方案 3 (P1)：Leaf 沙箱 3-Strike 快速熔断与主动反思阻断机制

#### 1. 熔断计数器协议
在 `hooks_protocol.py` 中为当前 Attempt 维持变异失败直方图：
- 当同一路径或类似模式被越界拦截累计达 **3 次** 时，沙箱主动封锁写通道；
- 强制向 Leaf 注入终端中断信号：
  > `[CIRCUIT_BREAKER_TRIGGERED] You have violated mutation fence 3 times on path: {path}. This is an authoritative boundary failure, not a code defect. Cease further tool attempts and emit disposition: finding with class: spec-blocker immediately.`

#### 2. 收益
将 T-02 这类因外部配置缺失导致的死锁时间从 **30 分钟暴力截断至 45 秒内**，彻底消灭“LLM 循环防御性重试”。

---

### 方案 4 (P1)：基准套件历史基线与候选组物理双轨解耦架构

#### 1. 架构原则：时空不变性隔离
- **历史基线控制组 (`v10.2.1-stable`)**：由其自身版本库内的 `MANIFEST.json` 内容哈希完全自闭环，只校验该历史快照内存在的白名单项；
- **当前演进候选组 (`candidate`)**：遵循当前工作区最新的架构契约（如 `core-kernel.md`）。

#### 2. 接口重构落地
在 `benchmarks/runners/bench_lib.py` 中彻底解耦参数绑定：
```python
REQUIRED_SKILL_ENTRIES = ("SKILL.md", "CONTEXT.md", "references/core-kernel.md")
REQUIRED_BASELINE_ENTRIES = ("SKILL.md", "CONTEXT.md")

def require_complete_skill(skill_root, origin: str, entries=None) -> None:
    target_entries = entries or (REQUIRED_BASELINE_ENTRIES if "baseline" in origin else REQUIRED_SKILL_ENTRIES)
    gaps = skill_contract_gaps(skill_root, entries=target_entries)
    if gaps:
        raise BenchBlocked(f"{origin}: missing {', '.join(gaps)}")
```

---

### 方案 5 (P2)：基于 CAS 树拓扑的内容寻址跨世代任务继承协议

#### 1. 内容寻址收据（CAS Delivery Receipts）
每个完成的 Task 结算时，将其交付物生成独立 Git Tree OID 与结算凭证：
$$\text{ReceiptKey} = \text{SHA256}(\text{TaskSourceDigest} + \text{BaseTreeOID} + \text{WriteScope})$$

#### 2. 0-Token 跨代继承机制
当 Change 发生局部调整（如仅修改了 T-02 的配置）触发 Generation 升级时：
1. 调度器计算各 Task 的 `ReceiptKey`；
2. 检测到 T-03 的输入契约、依赖关系与基础代码库完全未变；
3. 直接将 Generation 1 的完成收据复写至 Generation 2 账本，跳过派发；
4. **收益**：T-03 耗时直接归零，达成完全确定性的增量交付。

---

## 4. 全流程时间极限收敛论证 (≤ 6 分钟)

### 4.1 稳态生命周期执行流水线模拟

当上述 5 项长效机制全部生效后，类似规模的 3 任务交付流转如下：

```text
T+0:00 ── [Authoring] 写入 proposal.md & tasks.md (语法自适应)
T+0:40 ── [Pre-flight] 静态覆盖率扫描通过，loom spec prepare & approve (1轮通过)
T+1:00 ── [Generation 1 并行派发]
           ├── Leaf T-01: 修改 bench_lib.py / 运行测试 ──► T+2:30 [Success]
           ├── Leaf T-02: 拥有完整 scope，一次性写完测试与实现 ──► T+3:30 [Success]
           └── Leaf T-03: 更新 Markdown 协议 / 单测通过 ──► T+2:00 [Success]
T+3:30 ── [Wave 1 完成] Sliding Window 即时入账
T+4:00 ── [Host 统一收敛] 运行全量回归 (363 tests / 4.5s)
T+4:30 ── [CAS 发布] 生成合并 commit 并推送至 origin/main
─────────────────────────────────────────────────────────────────
全生命周期总耗时：4 分 30 秒 (稳定收敛于 ≤ 6 分钟)
```

### 4.2 收益总结

1. **确定性消除 94% 的无效耗时**：将 85 分钟压缩至 4.5 ~ 6 分钟；
2. **根除 LLM 认知幻觉与重试死锁**：以沙箱熔断与静态预检替代盲目重试；
3. **保障历史基线纯洁性**：消除不同版本规约之间的时空污染；
4. **计算复用最大化**：CAS 内容寻址实现无损跨代继承。
