# Design Prototype Kit — Automated P9+ Benchmark Harness
## Claude Code 真实模拟执行与自动化评估实施方案

> 目标：为 `design-prototype-kit / spec-prototype` 建立一套可长期运行的自动化 Benchmark Harness，能够让 Claude Code 基于真实 Brief 自动执行完整设计流程，并对 **产品理解、方法选择、UX/UE、设计张力、现代设计表达、克制创新、高保真原型、Spec 质量、前端可实施性与回归稳定性** 做可重复、可对比、可追溯的评估。

---

# 1. Benchmark 的核心目标

Benchmark 不是为了证明：

- Skill 能启动；
- 文件能生成；
- 某些设计关键词出现；
- 页面能截图；
- CI 全绿。

而是要回答五个真正的问题：

1. **Semantic Fidelity**：是否正确理解产品，是否发生产品语义脑补；
2. **Design Quality**：是否产生符合真实业务、具有现代设计质量和产品特异性的方案；
3. **Experience Quality**：关键任务、状态、恢复、响应式和可访问性是否成立；
4. **Delivery Quality**：设计 Spec 是否足够完整，让前端 Agent 不需要重新做设计；
5. **Runtime Quality**：Method Router、Builder、Critic、Authority Gate 是否按预期工作，且没有模板化、逃逸或过度工程。

Benchmark 必须最终验证：

```text
Brief
→ Product Understanding
→ Method Selection
→ Spec
→ Prototype
→ Critic
→ Refinement
→ Frozen Approved Spec
→ Frontend Contract
→ Independent Frontend Implementation
→ Verification
```

而不是只验证其中某一层。

---

# 2. 总体架构

推荐建立以下自动化链路：

```text
                    BENCHMARK CASE
                         │
                         ▼
              ┌─────────────────────┐
              │ Case Orchestrator   │
              │ run_case.py         │
              └──────────┬──────────┘
                         │
         ┌───────────────┼────────────────┐
         │               │                │
         ▼               ▼                ▼
   No-Skill Run     Stable Skill     Candidate Skill
         │               │                │
         └───────────────┼────────────────┘
                         ▼
                Artifact Collection
                         │
          ┌──────────────┼───────────────┐
          ▼              ▼               ▼
     Semantic Judge   Task Runner    Visual Capture
          │              │               │
          └──────────────┼───────────────┘
                         ▼
                  Blind Pairwise Judge
                         │
                         ▼
              Frontend Reproduction Test
                         │
                         ▼
                   Aggregate Report
```

最终生成：

```text
benchmark-report.json
benchmark-report.md
pairwise-results.json
method-routing.json
task-traces/
screenshots/
frontend-reproduction/
```

---

# 3. Benchmark 目录结构

建议在现有 `benchmarks/` 下收敛为：

```text
benchmarks/
├── cases/
│   ├── golden/
│   │   ├── incident-commander/
│   │   │   ├── case.yaml
│   │   │   ├── brief.md
│   │   │   ├── ground-truth.yaml
│   │   │   ├── rubric.yaml
│   │   │   └── tasks.yaml
│   │   ├── ai-writer/
│   │   ├── editorial-reader/
│   │   ├── mobile-booking/
│   │   ├── approval-workflow/
│   │   ├── creation-tool/
│   │   ├── consumer-habit/
│   │   └── novel-coordination/
│   │
│   ├── daily/
│   ├── calibration/
│   └── holdout/
│
├── runners/
│   ├── run_case.py
│   ├── run_matrix.py
│   ├── run_claude_session.py
│   ├── run_task_trace.py
│   ├── run_frontend_reproduction.py
│   └── collect_artifacts.py
│
├── judges/
│   ├── semantic_judge.py
│   ├── runtime_judge.py
│   ├── task_judge.py
│   ├── visual_manifest.py
│   ├── pairwise_judge.py
│   ├── contract_judge.py
│   └── regression_judge.py
│
├── schemas/
│   ├── case.schema.json
│   ├── ground-truth.schema.json
│   ├── tasks.schema.json
│   ├── run-result.schema.json
│   └── benchmark-report.schema.json
│
├── prompts/
│   ├── no-skill.txt
│   ├── skill-run.txt
│   ├── critic-pairwise.txt
│   └── frontend-implementation.txt
│
├── baselines/
│   ├── v10.2.1-stable/
│   └── human-reference/
│
├── results/
└── reports/
```

原则：

> **Case、Runner、Judge、Baseline 分离。**

不要让 Skill 本身知道 hidden rubric 和 ground truth。

---

# 4. Case Schema

每个 Case 至少包含五份内容。

## 4.1 `case.yaml`

```yaml
id: incident-commander
category: enterprise
difficulty: hard

run_policy:
  repeats: 3
  timeout_seconds: 900
  max_turns: 30

variants:
  - no_skill
  - stable_skill
  - candidate_skill

surfaces:
  expected:
    - desktop
    - mobile

capabilities_under_test:
  - product_understanding
  - context_preservation
  - action_safety
  - dense_information
  - responsive
  - frontend_contract

evaluation:
  semantic: true
  task_trace: true
  visual_pairwise: true
  frontend_reproduction: true
```

---

# 5. Brief 与隐藏 Ground Truth 必须隔离

## 5.1 `brief.md`

这是唯一允许直接传给设计 Agent 的业务输入。

要求：

- 像真实用户输入；
- 信息不完整；
- 可以存在模糊和冲突；
- 不泄露评价规则；
- 不写期望 Method；
- 不写“应该使用某布局”。

例如：

```markdown
我们需要设计一个用于处理大规模计算集群异常的 Incident Commander。
主要用户是值班 SRE。

他们需要快速定位异常节点、理解影响范围，并在必要时安全处理问题。

核心矛盾是：
一方面需要非常快，另一方面错误操作可能扩大事故。

当前系统数据很多，用户通常在桌面端工作，但偶尔需要手机查看事故状态。
```

---

## 5.2 `ground-truth.yaml`

**绝不能传给设计 Agent。**

```yaml
supported_facts:
  - users_are_sre
  - users_can_inspect_worker_status
  - users_can_drain_workload

unsupported_assumptions:
  - user_can_restart_cluster
  - automatic_remediation_exists
  - payment_exists
  - calendar_integration_exists

required_objects:
  - incident
  - worker
  - workload
  - region

critical_risks:
  - accidental_destructive_action
  - context_loss_during_investigation

expected_unknowns:
  - exact_authorization_model
  - incident_severity_taxonomy
```

这个文件由 Semantic Judge 使用。

---

# 6. Task Trace Schema

每个 Case 应定义真实任务，而不是页面检查。

`tasks.yaml`：

```yaml
tasks:
  - id: inspect-overloaded-worker
    start:
      state: incident_active

    goal:
      description: Find the worker causing abnormal load and inspect its impact.

    required_outcomes:
      - worker_identified
      - impact_context_visible

    forbidden_outcomes:
      - context_reset
      - unrelated_destructive_action

  - id: safely-drain-worker
    goal:
      description: Safely initiate worker drain while understanding consequence.

    required_outcomes:
      - consequence_visible_before_commit
      - state_feedback_after_action
      - recovery_or_safe_exit_available
```

Runner 不应该要求固定 DOM selector。

优先使用：

```text
semantic target
role
accessible name
data-action
contract anchor
```

而不是：

```text
.button:nth-child(3)
```

---

# 7. Claude Code 自动调用架构

核心 Runner：

```text
run_case.py
```

负责创建隔离 workspace，然后真正调用 Claude Code CLI。

推荐流程：

```text
1. 创建临时 workspace
2. copy benchmark case brief
3. 安装/链接对应 Skill variant
4. 启动 Claude Code 非交互 session
5. 发送真实用户 prompt
6. 等待完整执行
7. 保存 transcript
8. 保存 prototype/**
9. 执行自动 verification
10. 执行 Critic
11. 生成 run-result.json
```

---

# 8. Claude Code 调用原则

实际 CLI 命令应封装在：

```text
run_claude_session.py
```

不要散落在各种 Benchmark 文件里。

伪代码：

```python
def run_claude_session(
    workspace,
    prompt,
    skill_path=None,
    model=None,
    timeout=900,
):
    env = prepare_isolated_env(
        workspace=workspace,
        skill_path=skill_path,
    )

    result = subprocess.run(
        [
            "claude",
            "--print",
            "--output-format", "stream-json",
            prompt,
        ],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    return parse_claude_result(result)
```

实际参数以你本机 Claude Code 当前 CLI 为准。

**Runner 不应依赖 Claude Code 输出自然语言判断成功。**

成功必须由工件与 Judge 判断。

---

# 9. 三类 Variant

每个 Case 至少运行：

## Variant A — No Skill

```text
base Claude Code
+ same brief
+ same environment
```

禁止使用 `spec-prototype`。

作用：

> 测 Skill 是否真正创造增量。

---

## Variant B — Stable Skill

```text
v10.2.1-stable
```

这是长期回归基准。

---

## Variant C — Candidate Skill

未来修改版。

例如：

```text
v10.2.2-dev
```

所有新优化首先和 Stable 比。

---

# 10. 运行环境必须固定

为避免模型随机性和环境污染：

```yaml
execution:
  model: fixed
  same_prompt: true
  same_repo_seed: true
  same_tool_permissions: true
  same_timeout: true
  same_max_turns: true
  clean_workspace: true
```

每轮必须使用新的 workspace：

```text
/tmp/design-bench/<case>/<variant>/<run-id>/
```

禁止复用上一轮生成物。

---

# 11. Cross-run Variance

每个 Case 不要只跑一次。

最低：

```text
3 runs / variant
```

核心 Case：

```text
5 runs / variant
```

记录：

```yaml
variance:
  semantic_errors:
  method_selection:
  task_success:
  layout_pattern:
  design_quality:
```

P9 替代不是：

> 偶尔生成一个很棒的页面。

而是：

> **大多数时候稳定做出正确判断。**

---

# 12. Runtime Judge

Runtime Judge 不评价美丑。

它检查：

```text
Method Router
Authority
Evidence
Builder boundary
Critic boundary
Spec lifecycle
```

例如：

```yaml
runtime_checks:
  method_registry_loaded: pass
  active_methods_count: 4
  irrelevant_method_selected: false

  authority:
    stage1: sealed_provisional
    stage4: validated
    stage5: frozen_approved

  builder:
    invented_undeclared_state: false
    invented_shortcut: false
    modified_spec: false

  critic:
    preference_blocked_build: false
```

---

# 13. Method Router 自动评估

每个 Ground Truth Case 可以定义：

```yaml
method_expectation:
  must_consider:
    - context-preservation
    - action-verb-lifecycle

  relevant:
    - progressive-disclosure

  should_not_select:
    - form-ergonomics
```

注意：

`must_consider` 不等于 `must use`。

评价：

```text
Method Recall
Method Precision
Negative Selection Accuracy
```

公式：

```text
precision =
relevant_selected / all_selected

recall =
expected_considered / expected_methods
```

但不要把它变成 Hard Design Score。

它只是 Runtime 健康指标。

---

# 14. Semantic Judge

这是硬门。

读取：

```text
ground-truth.yaml
product.md
specification
frontend-contract
prototype copy
```

检查：

### Fabrication

```text
unsupported product capability
invented permission
invented lifecycle
invented integration
invented user research
```

### Evidence Promotion

```text
hypothesis → fact
derived → explicit
```

输出：

```yaml
semantic:
  fabricated_capabilities: 0
  authority_promotions: 0
  unsupported_objects: 0
  status: pass
```

Hard Gate：

```text
fabricated_capabilities > 0
→ FAIL
```

---

# 15. Task Runner

使用 Playwright 或现有 headless browser harness。

流程：

```text
launch prototype
↓
load task
↓
inspect visible controls
↓
perform task
↓
record DOM/state/evidence
```

不要只运行预写 selector。

最好提供一个独立 Task Agent：

```text
task-runner-agent
```

只知道：

```text
任务目标
当前页面
允许操作
```

不知道 Skill 的内部设计意图。

这样更接近真实用户。

---

# 16. Task Trace 输出

统一：

```yaml
task_id: safely-drain-worker

trace:
  - observe: worker table
  - action: select worker-07
  - state: detail_open
  - observe: impact context
  - action: initiate drain
  - state: confirmation
  - action: commit
  - state: processing
  - state: settled

results:
  completed: true
  dead_end: false
  context_loss: false
  silent_noop: false
  recovery_available: true
```

---

# 17. Visual Capture

固定视口：

```text
320
390
768
1280
1600
```

不是每个 Case 都必须全部运行。

由 Case 决定：

```yaml
viewports:
  required:
    - 390
    - 1280
```

状态同理。

禁止统一要求：

```text
ideal / empty / error
```

而应该由 Contract 声明。

---

# 18. Blind Pairwise Judge

这是 Design Quality 核心。

输入：

```text
same brief
same representative content
Candidate Alpha screenshots
Candidate Beta screenshots
```

隐藏：

```text
Skill version
model identity
source path
previous score
```

Pairwise Judge 评价：

```text
1 Product Fit
2 Task Clarity
3 IA / Spatial Logic
4 Interaction Quality
5 Visual Hierarchy & Craft
6 Distinctiveness
7 Restraint
8 Trust / Accessibility
```

输出不要直接 8.7 分。

使用：

```yaml
dimension:
  preference: alpha | beta | tie
  confidence: low | medium | high
  reason: ...
```

最后：

```yaml
overall_preference: alpha
```

---

# 19. Judge 必须独立

设计 Agent 与 Judge 不应是同一 session。

至少做到：

```text
Generation Session
≠
Critic Session
≠
Pairwise Judge Session
```

更理想：

```text
不同 context
随机 candidate 顺序
不共享 rationale
```

不要把：

```text
product.md rationale
```

先给 Visual Judge 看。

先看实际结果，再看解释。

---

# 20. Pairwise Matrix

不用每轮全量两两比较。

推荐：

```text
Stable vs No-Skill
Candidate vs Stable
Candidate vs Human Reference
```

避免：

```text
N variants → N² comparisons
```

---

# 21. Human Reference

真正验证 P9+，最终必须加入 Human / Curated Reference。

不是所有 Case 都需要。

第一阶段 8 个 Golden Case 中选 4 个即可。

Reference 可来源：

```text
优秀真实产品设计
内部高级设计师作品
经过多人评审的设计
现有成熟系统的关键 slice
```

重点不是 pixel matching。

比较：

```text
Product judgment
Task model
IA
Interaction
Visual hierarchy
Signature
Restraint
```

---

# 22. Frontend Reproduction Test

这是最关键的差异化 Benchmark。

流程：

```text
Design Skill
↓
Frozen Approved Spec
↓
Frontend Contract
↓
Independent Frontend Agent
```

独立 Frontend Agent：

**不能看 prototype HTML/CSS 源码。**

只允许读取：

```text
frontend-contract.yaml
tokens
DESIGN-REF / component contract
frozen specification
```

然后自己实现。

---

# 23. Frontend Agent Prompt

核心边界：

```text
You are an implementation agent.

Do not redesign the product.
Do not invent missing interaction semantics.
Do not infer unspecified product capabilities.

Implement only the supplied frozen design contract.
If a consequential implementation decision is unspecified,
record it as CONTRACT_GAP instead of designing around it.
```

这样就能真实测：

> Spec 能不能指导实现。

---

# 24. Design Reinterpretation Rate

Frontend Agent 每次必须输出：

```yaml
implementation_receipt:
  contract_gaps:
    - ...
  inferred_design_decisions:
    - ...
  clarification_required:
    - ...
```

指标：

```text
Design Reinterpretation Rate =
frontend-added consequential design decisions
/
total consequential design decisions
```

建议长期目标：

```text
< 10%
```

成熟后争取：

```text
< 5%
```

---

# 25. Frontend Fidelity Judge

比较：

```text
Design prototype
vs
independent frontend implementation
```

分三层：

### T1 Semantic / Structural

```text
objects
regions
states
actions
```

### T2 Contract Fidelity

```text
tokens
component bindings
responsive behavior
accessibility
```

### T3 Visual

```text
composition
hierarchy
spacing
typography
```

T3 不应该做绝对 pixel-perfect。

除非：

> approved golden baseline vs same implementation family。

---

# 26. Anti-template Diversity Benchmark

每批 Benchmark 完成后自动分析所有 Candidate 输出。

检测：

```text
sidebar frequency
top-nav frequency
card-grid frequency
split-pane frequency
drawer frequency
palette similarity
radius similarity
typography similarity
layout topology similarity
```

重点不是：

> 这些东西不能重复。

而是：

> 不相关产品是否异常趋同。

可以输出：

```yaml
diversity:
  cross_case_layout_similarity: 0.41
  cross_case_token_similarity: 0.36
  suspicious_clusters:
    - incident-commander
    - editorial-reader
```

如果 Reader 和 SRE Console 高度相似：

> 是红旗。

---

# 27. Modern Design / Expression Stress Benchmark

专门验证 Five Axes。

同一基础产品建立不同 Expression Prompt：

```text
quiet
editorial
technical
premium
playful
human
expressive
neutral
```

保持：

```text
Objects
Journey
Tasks
```

不变。

只变化：

```text
Expression intent
```

然后测：

```text
视觉是否真的出现差异
交互规范是否仍稳定
是否所有方向最终仍长得一样
是否为了表达而破坏 usability
```

这是验证：

> Five Axes 是否真的是表达系统，而不是装饰参数。

---

# 28. Design Tension Benchmark

构建三类题。

## A — Low Innovation

例如：

```text
settings
approval
medical admin
reading
```

预期：

```text
high convention
low novelty
high clarity
```

## B — Signature Opportunity

例如：

```text
AI creative workspace
novel collaboration
professional creation tool
```

预期：

```text
clear product-specific signature
```

## C — Experimental

没有成熟产品 archetype。

预期：

```text
explore
probe
validate
```

而不是直接套 Pattern。

---

# 29. 摩擦 Benchmark

记录每轮：

```yaml
friction:
  user_questions_total:
  blocking_questions:
  material_questions:
  avoidable_questions:

  stages_executed:
  unnecessary_stage_reentry:

  full_rebuilds:
  targeted_repairs:

  tokens_consumed:
  elapsed_seconds:
```

核心指标：

```text
Question Efficiency =
material_questions / total_questions
```

以及：

```text
Targeted Repair Ratio =
targeted_repairs / all_repairs
```

---

# 30. Change Scope Benchmark

建立专门 Mutation Cases。

从一个已经 Frozen 的项目开始。

依次发：

### L0

```text
把 accent 稍微降饱和
```

期望：

```text
不重做 Product
不重跑 OOUX
```

### L1

```text
增加按钮 loading 状态
```

期望：

```text
component / state level
```

### L2

```text
重新排布这个 screen 的信息优先级
```

期望：

```text
screen-level reasoning
```

### L3

```text
新增跨页面审批流
```

期望：

```text
Journey review
```

### L4

```text
权限模型从 owner-only 改成 team roles
```

期望：

```text
re-anchor Object / Journey / permission
```

这样可以直接测摩擦和过度重推导。

---

# 31. Escape Tests

必须建立 Red-Team Cases。

## Product Meaning Escape

Brief 只写：

```text
用户需要预订服务
```

检测 Skill 是否自动发明：

```text
calendar sync
payment
SMS
```

---

## Technique Escape

Brief 是：

```text
minimal reader
```

检测是否自动生成：

```text
telemetry
tabular numerics
glass
industrial tactile
```

---

## Builder Escape

Contract 不包含：

```text
empty state
keyboard shortcuts
```

检测 Builder 是否自行添加。

---

## Authority Escape

`sealed_provisional`

检测：

```text
frontend delivery gate
```

是否阻止正式实现。

---

## Critic Escape

给 Critic 一个非常干净的 neutral gray 系统。

检测是否因为：

```text
“不够现代”
```

制造不存在的问题。

---

# 32. 自动 Report

每个 Case 输出：

```yaml
case:
variant:
run_id:

runtime:
semantic:
task:
visual:
contract:
frontend:
friction:
diversity:
```

最终 aggregate：

```text
reports/daily-2026-09-19.md
```

---

# 33. 核心指标只保留 7 个

避免 Dashboard 过载。

## Hard Metrics

```text
1. Semantic Error Rate
2. Critical Task Success Rate
3. Authority Escape Rate
```

## Quality Metrics

```text
4. Blind Pairwise Preference
5. Method Precision / Recall
6. Design Reinterpretation Rate
7. Regression Rate
```

辅助观察：

```text
Template Similarity
Question Efficiency
Runtime Cost
```

不要把辅助指标变 Hard Gate。

---

# 34. Hard Gates

候选版本只要出现以下任何一个：

```text
semantic fabrication > 0
authority escape > 0
critical task break > 0
critical accessibility violation > 0
```

就不能 promotion。

---

# 35. Quality Promotion Gate

Candidate vs Stable：

建议：

```text
candidate pairwise preference >= 55%
```

且：

```text
no significant regression on any major category
```

Candidate vs No-Skill：

```text
>= 70–75%
```

Human Reference：

先不做硬 Gate。

长期观察：

```text
35–45% pairwise preference
```

已经是非常有价值的信号。

---

# 36. Train / Daily / Calibration / Holdout

虽然这里不是训练模型，也必须防 benchmark overfitting。

建议：

```text
Daily: 12 cases
Calibration: 4 cases
Holdout: 4 cases
```

日常 Skill 修改：

```text
只跑 Daily
```

Release Candidate：

```text
Daily + Calibration
```

大版本：

```text
才解锁 Holdout
```

Holdout 不应频繁打开结果。

---

# 37. Golden 8 首批任务

建议第一批：

```text
1. incident-commander
2. ai-writer-workspace
3. editorial-reader
4. mobile-booking
5. approval-workflow
6. creation-tool
7. consumer-habit
8. novel-coordination
```

每个：

```text
No Skill × 3
Stable Skill × 3
Candidate × 3
```

总：

```text
72 sessions
```

不需要一次全部跑。

Daily 可以每天选 2–3 Case。

---

# 38. Daily Benchmark

建议：

```bash
python benchmarks/runners/run_matrix.py \
  --suite daily \
  --variants stable,candidate \
  --repeats 1
```

输出：

```text
PASS
REGRESSION
BLOCKED
INCONCLUSIVE
```

不要每天跑 Human Reference。

---

# 39. Weekly Benchmark

```bash
python benchmarks/runners/run_matrix.py \
  --suite golden \
  --variants no-skill,stable,candidate \
  --repeats 3 \
  --pairwise
```

执行：

```text
runtime
semantic
task trace
visual pairwise
contract
```

---

# 40. Release Benchmark

```bash
python benchmarks/runners/run_matrix.py \
  --suite release \
  --variants stable,candidate,human \
  --repeats 3 \
  --pairwise \
  --frontend-reproduction \
  --holdout
```

只有 Release 才跑：

```text
Human reference
Frontend reproduction
Holdout
```

---

# 41. `run_matrix.py` 主要职责

```python
for case in cases:
    for variant in variants:
        for repeat in range(repeats):
            result = run_case(case, variant)
            collect(result)

run_semantic_judges()
run_task_judges()
run_pairwise_if_needed()
run_frontend_reproduction_if_needed()
aggregate_report()
```

---

# 42. `run_case.py` 状态机

```text
PREPARE
↓
GENERATE
↓
COLLECT
↓
VERIFY
↓
CRITIQUE
↓
FREEZE (when allowed)
↓
RESULT
```

任何阶段异常：

```text
BLOCKED
```

不要自动“修 benchmark”。

---

# 43. 不要让 Runner 自动帮助设计 Agent

Benchmark Runner 只能：

```text
传 Brief
提供环境
执行命令
收集工件
```

禁止：

```text
补充产品信息
提示该使用什么 Method
告诉它漏了什么
提示评价标准
```

否则 Benchmark 已污染。

---

# 44. Benchmark Agent 分工

推荐最多四个角色：

## Design Agent

当前 Skill。

## Task Agent

像用户一样执行任务。

## Critic Agent

按照现有 `spec-prototype-critic`。

## Pairwise Judge

只做盲评。

Frontend reproduction 时再增加：

## Frontend Agent

不需要更多 Agent。

---

# 45. 防 Benchmark Goodhart

必须明确：

Benchmark Rubric 禁止使用：

```text
必须有 tabular nums
必须有 sparkline
必须有 glass
必须有 split-pane
必须有 empty state
必须有某个 method
```

应该使用：

```text
information interpretable
task continuous
recovery adequate
hierarchy clear
expression coherent
signature product-specific
innovation proportionate
```

---

# 46. 防 Skill 读到 Benchmark 答案

Benchmark 运行 workspace 中：

只放：

```text
brief.md
必要初始 assets
Skill
```

不要复制：

```text
ground-truth.yaml
rubric.yaml
expected-methods
human reference
pairwise result
```

这些文件保留在 Benchmark Controller workspace。

---

# 47. Human Review 的位置

不需要人工看所有 Case。

只看：

```text
pairwise confidence low
judge disagreement
candidate regression
holdout
human-reference comparison
```

自动化负责筛选。

这样成本可控。

---

# 48. 推荐第一阶段实现顺序

## P0

1. `case.yaml` schema
2. `run_claude_session.py`
3. `run_case.py`
4. artifact collector
5. semantic judge
6. runtime judge

先证明：

```text
Claude Code 能真正跑完整 session
```

---

## P1

7. Task Trace Runner
8. Visual Capture
9. Blind Pairwise Manifest
10. Pairwise Judge

---

## P1

11. Frontend Reproduction Runner
12. Design Reinterpretation Rate
13. Contract Fidelity Judge

---

## P2

14. Diversity analysis
15. Expression stress
16. Holdout manager
17. Historical dashboard

---

# 49. 最重要的实现纪律

## 不把 benchmark 脚本放进 Skill Runtime

Benchmark 应在：

```text
benchmarks/
```

而不是：

```text
skills/spec-prototype/scripts/
```

否则：

> Skill 会逐渐看到自己的考试逻辑。

---

# 50. Stable Promotion 工作流

```text
candidate branch
↓
daily benchmark
↓
weekly golden benchmark
↓
no hard regression
↓
candidate vs stable pairwise
↓
release benchmark
↓
manual review only for ambiguous cases
↓
tag stable
```

---

# 51. 最终判断标准

只有当 Benchmark 长期表现为：

```text
Semantic fabrication ≈ 0
Critical Task Success very high
Authority escape = 0
Method Precision/Recall stable
Candidate > No-Skill consistently
Candidate ≈ strong curated reference on many cases
Reinterpretation Rate < 10%
Template similarity controlled
Cross-run variance acceptable
```

才可以真正说：

> Skill 已经不仅是一个“设计方法 Prompt”，而是一套可稳定替代高级设计专家执行工作的 Design Harness。

---

# 52. 推荐落地后的最终自动执行命令

建议最终提供三个入口：

```bash
# 快速日常回归
python benchmarks/runners/run_matrix.py --suite daily

# 完整黄金集
python benchmarks/runners/run_matrix.py --suite golden --repeats 3 --pairwise

# 发布验证
python benchmarks/runners/run_matrix.py \
  --suite release \
  --repeats 3 \
  --pairwise \
  --frontend-reproduction \
  --holdout
```

所有 Benchmark 都应做到：

```text
One command
→ create isolated workspaces
→ call real Claude Code sessions
→ collect artifacts
→ run browser tasks
→ capture screenshots
→ run blind judges
→ run contract reproduction
→ produce one report
```

---

# 53. 最终推荐

当前 Skill 架构已经接近冻结，不应该再通过主观观察继续调整。

下一阶段应该把 Benchmark Harness 当成它的“真实生产试验场”：

```text
Architecture Freeze
↓
Automated Real Claude Sessions
↓
Independent Evidence
↓
Repeated Failure Patterns
↓
Evidence-backed Calibration
```

只有重复出现的真实失败，才允许反向修改 Skill。

这样可以同时避免两种风险：

```text
过度工程
```

以及：

```text
为了 Benchmark 而 Benchmark
```

最终形成真正持续可验证的：

**Principal-Level Product Design Skill Evaluation Harness。**
