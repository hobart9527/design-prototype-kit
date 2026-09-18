# Design Prototype Kit (v10.1)

高质感产品体验设计决策与原型验证线束（Design Decision & Evidence Harness）。

## 核心架构 (Canonical Design Operating Model)

系统由 **1 主模型 + 3 辅助模型 + 1 条横向 Evidence Protocol** 构成，彻底解耦规范契约与原型验证：

- **主模型 · Nine Pillars (WHAT WE DESIGN)**: Value, Research, Object, Journey, Topology, Attention, Expression, Interaction, Resilience.
- **辅助模型 1 · Double Diamond (HOW WE DECIDE)**: Discover, Define, Develop, Deliver 结构化发散与收敛决策。
- **辅助模型 2 · Five Axes (HOW IT FEELS)**: Density, Energy, Materiality, Rhythm, Character 具象感官标定。
- **辅助模型 3 · Craft Library (HOW WE CRAFT)**: Invariants（跨产品通用品质底线）与 Candidate Techniques（上下文激活的技法库）严格解耦。
- **横向治理 · Evidence Protocol**: 全流程标记 Source, Authority (`explicit` / `derived` / `hypothesis`), Verification 状态，杜绝业务臆造与虚假闭环。

## 适用场景与参考模式 (Composable Reference Patterns)

系统提供可自由组合演进的参考范式，拒绝互斥单一分类器：

- **Dense Workbench Pattern**: 高密数据与运维仪表盘，紧凑微网格与数值对齐。
- **Operational Canvas Pattern**: 现代 SaaS 与协作看板，主从分栏与渐进式层级展开。
- **Editorial Reading Pattern**: 文本沉浸与阅读排版，舒缓字符度量与无干扰视觉基底。
- **Somatic Touchflow Pattern**: 移动与触控优先，拇指热区与高响应性触控交互。

## 交互、韧性与验证

- **Spec as Durable Contract / Prototype as Disposable Proof**: 规约持久化，原型作为证伪假设的低成本实验。
- **Dual Envelope Protocol**: Builder 显式区分 `constraint_envelope` (MUST 业务与状态契约) 与 `creative_envelope` (DESIGN SPACE 构图与视觉节律)。
- **真实证据闭环**: 严格区分机器静态 Linter 覆盖度与视觉/交互人工审核，拒绝虚假综合评分。

## 目录结构

```text
design-prototype-kit/
├── agents/                  # 专属设计 Builder 与独立 Critic 契约
├── skills/spec-prototype/   # 核心设计规约、交互模板与导出工具
│   ├── references/          # 权威设计语言、组件规范与验收标准
│   ├── templates/           # W3C DTCG Token 模版与产物定义
│   └── scripts/             # Token 转换器与验证工具
└── tests/                   # 独立测试与设计规范校验
```

## 测试与校验

```bash
python3 -m pytest tests/ -q
```
