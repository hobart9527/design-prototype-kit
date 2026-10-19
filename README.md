# Design Prototype Kit (v10.2)

[中文说明](#中文说明) | [English Documentation](#english-documentation)

---

<a name="中文说明"></a>
# 中文说明

`design-prototype-kit` 是 AI 产品体验设计的单脑工作流线束:设计决策沉淀为高密度设计记录,机器契约由此编译,原型作为验证耗材走查真实渲染证据。

**唯一工作流权威是 [`skills/spec-prototype/SKILL.md`](skills/spec-prototype/SKILL.md)** — 流程、门禁、产物契约以它为准;本 README 只是导览。

## 流程:3 Turn / 5 Stage(单脑)

| Turn | Stage | 产出 |
|---|---|---|
| 1 | Frame(立)/ Propose(破) | 设计记录(张力、五轴、方向),`## Resume` 断点 |
| 2 | Make(作) | tokens.css(编译)+ Hero Anchor 原型 + 捕获证据 |
| 3 | Look(观)→ Refine(修)→ Freeze(封) | Spec IR、审查、freeze 批准绑定 |

Turn 1→2 门禁:设计记录须带 `## Resume` 且 Stage checkpoint 越过 `stage1-contract`。

## 产物地图

```text
prototype/
├── discussion.md                            # 单记录布局;分层树下为薄 Resume seam
│   ├── truth.md                             # 分层:产品事实、张力、Decisions 权威表(内置 ## Resume)
│   ├── world.md                             # 分层:视觉世界、品味台账、token 唯一权威
│   └── briefs/<slice>.md                    # 分层:每 slice 一份(表面策略与证据)
├── specifications/<slice>/r1.spec.md        # RFC 规格(compile_spec_ir.py 编译)
├── contracts/compiled/<slice>/r1.spec.json  # Canonical Spec IR
├── shared/tokens.css                        # 编译产物(compile_tokens.py 唯一写入者)
└── experiments/<slice>/anchor/index.html    # 高保真可运行原型
```

## 目录

- `skills/spec-prototype/` — skill 本体(SKILL.md + references + scripts + templates)
- `benchmarks/` — 评测线束(runners/judges),与 skill 分发解耦
- `agents/` — 可选的分离式子代理提示词(builder/critic),主流程不依赖
- `openspec/` — OpenSpec 变更治理(仅 Loom 任务使用)
- `tests/` — pytest 套件(760+)

## 退役机制(仅兼容保留,勿用于新流程)

- `assemble_envelope.py` 双信封派发 — 仅 legacy/benchmark 兼容;产物生命周期见 `references/04-governance/artifact-lifecycle.md`
- `lint_spec_contracts.py` 六件套门禁 — 已退役,文件保留
- 独立 Critic 固定 5 视口评审 — 验证分层见 `references/03-verification/`

## 升级注记

v10.2 编译器输出新增 `--font-display` 令牌:既有记录重跑 `compile_tokens.py` 以重新封版 tokens.css(`--check-sync` 会先报 out_of_sync,重编译后恢复)。

---

<a name="english-documentation"></a>
# English Documentation

`design-prototype-kit` is a single-brain harness for AI product experience design: decisions settle into a high-density design record, machine contracts compile from it, and prototypes serve as disposable evidence under real rendering.

**The sole workflow authority is [`skills/spec-prototype/SKILL.md`](skills/spec-prototype/SKILL.md)** — this README is only a guide.

## Flow: 3 Turns / 5 Stages (single brain)

| Turn | Stage | Output |
|---|---|---|
| 1 | Frame / Propose | Design record (tension, five axes, direction), `## Resume` seam |
| 2 | Make | tokens.css (compiled) + Hero Anchor prototype + capture evidence |
| 3 | Look → Refine → Freeze | Spec IR, review, freeze approval binding |

Turn 1→2 gate: the design record must carry a `## Resume` block whose Stage checkpoint has advanced past `stage1-contract`.

## Artifact map

```text
prototype/
├── discussion.md                            # Single-record layout; thin Resume seam on layered trees
│   ├── truth.md                             # Layered: product facts, tension, Decisions & authority (built-in ## Resume)
│   ├── world.md                             # Layered: visual world, taste ledger, sole token authority
│   └── briefs/<slice>.md                    # Layered: one slice per file (surface strategy & evidence)
├── specifications/<slice>/r1.spec.md        # RFC spec (compiled via compile_spec_ir.py)
├── contracts/compiled/<slice>/r1.spec.json  # Canonical Spec IR
├── shared/tokens.css                        # Compiled output (compile_tokens.py is the sole writer)
└── experiments/<slice>/anchor/index.html    # High-fidelity runnable prototype
```

## Layout

- `skills/spec-prototype/` — the skill (SKILL.md + references + scripts + templates)
- `benchmarks/` — evaluation harness (runners/judges), decoupled from skill distribution
- `agents/` — optional detached subagent prompts (builder/critic); the main flow does not depend on them
- `openspec/` — OpenSpec change governance (Loom tasks only)
- `tests/` — pytest suite (760+)

## Retired mechanisms (kept for compatibility only — do not use in new flows)

- `assemble_envelope.py` dual-envelope dispatch — legacy/benchmark compatibility; see `references/04-governance/artifact-lifecycle.md`
- `lint_spec_contracts.py` six-piece gate — retired, file retained
- Independent Critic with a fixed 5-viewport review — see `references/03-verification/` for tiered verification

## Upgrade note

The v10.2 compiler emits a new `--font-display` token: re-run `compile_tokens.py` on existing records to re-seal tokens.css (`--check-sync` reports out_of_sync until recompiled).
