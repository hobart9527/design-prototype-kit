# Product Surface Map: Agent Detent Cockpit

> Derived Surface Topology and journey/coverage authority. Working index: `prototype/surface-map.md`.

## Identity

- Product / project: Agent Detent Cockpit (AI 自动编排流协同决策台)
- Surface Map revision / status: `r1` / `draft`
- Product record and source references: `prototype/product.md`
- Foundation / Design Proposition reference or explicit deferral: `prototype/experience-foundation.md`
- Supersedes: none
- Actual approval or delegated-scope reference: User confirmed Scenario 1
- Total in-scope pages and surfaces: 1 核心视窗聚合台 (Single Integrated Cockpit Surface with 3 Coordinated Zones)
- Requested scope and deliberate non-coverage:
  - In-scope: 极速巡航状态流、磁吸时间轴阻尼井、空格瞬时冻结原位微调、分支并联预测试算。
  - Deliberate non-coverage: 节点拖拽连线设计器、全量底层系统日历及账单结算中心。

## Topology basis

- Product Thesis, actors/jobs/outcomes served: 为风控操盘专家提供百路 Agent 编排流水线的毫秒级电传接管与触感阻尼巡航。
- Object/content relationships and lifecycle/authority constraints:
  - 1:N Pipeline Fleet -> 1:1 Active Runway -> 1:N Waypoints & Detent Wells -> 0:1 Fork Prediction.
- Object cardinality to structural container mapping:
  - **Zone A (Top)**: 1:N Fleet Confidence Horizon (水平流置信度雷达，高密横条展示全集群健康态).
  - **Zone B (Center)**: 1:1 Focused Runway & Spatial Detent Rail (单流巡航主跑道 + 阻尼磁吸时间轴).
  - **Zone C (Right/Dock)**: 1:1 Fly-by-wire Takeover & Fork Preview (空格瞬态激活的原位电传调控与阴影分支预测).
- 3-tier wayfinding and context preservation:
  - Tier 1 (Global): 顶层集群置信度分布与报警聚合，键盘 `[` 与 `]` 快速在流之间穿梭切流。
  - Tier 2 (Contextual): 主跑道时间轴，水平拖拽或左右光标巡游，遇 Detent Well 自动磁吸滞留。
  - Tier 3 (Secondary): 原位冻结弹出参数 Delta 调控盘，上下文完全保留在视窗背景，零跳转。
- Vertical slice scoping: Thin Walking Skeleton 聚焦于“低置信度阻尼吸附”与“空格键原位微调接管”两大灵魂交互。
- Organizing principle and user mental-model evidence: 航空电传操纵巡航系统，操作员视野永远处于“主航向”前方，不离开主控台。

## Page/surface necessity decisions

| Surface ID | Kind | Independent job/work mode | Necessity reason | Split/merge alternative and rationale |
|---|---|---|---|---|
| `cockpit-main` | Unified Workbench Page | 全流程监控与即时接管 | 必须维持毫秒级情境感知，拆分为独立页面会造成上下文丢失与切换延迟 | Merge: 坚决单屏聚合，拒绝分页 |

## Signature Moments & Ruthless Omissions

- **Signature Moment 1: Magnetic Detent Timeline (磁吸阻尼时间轴)**
  - 时间轴在低置信度（<85%）与关键调仓节点自动生成引力场。拖拽时间轴指针经过该点时，产生明显的粘滞阻尼（Friction Damping）与吸附锁定，并瞬间展示风险警报雷达。
- **Signature Moment 2: Spacebar Fly-by-wire Takeover (空格瞬态原位微调)**
  - 任何巡航时刻按下 `Space`，时间流瞬时停顿（Freeze Frame），中央即刻展开参数电传刻度盘（Dial）。滑动滚轮或使用键盘微调资金滑点容差与头寸上限，松开 `Space` 即刻合流，流水线继续全速冲刺。
- **Ruthless Omissions (极端取舍)**:
  - 坚决不做任何弹出式 Blocking Modal 审批弹窗（所有介入收敛至热键与物理阻尼场）。
  - 坚决不做通用工作流的连线拖拽与画布缩放（只保留时间航道拓扑）。
  - 坚决不做静态空白占位图或空泛的打分勋章。

## State applicability

| Surface/transition | State or condition | Why applicable / why not applicable | Trigger and user need | Behavior/recovery | Evidence required |
|---|---|---|---|---|---|
| `cockpit-main` | High-speed Cruising (全速巡航) | 正常状态（置信度 > 85%） | 数据流高频推进，专家被动监控 | 时间轴保持平滑流动，高密数码特征滚动 | 流体数据动画，低对比不刺眼 |
| `cockpit-main` | Detent Captured (阻尼捕获) | 低置信度异常（置信度 72%） | 触发引力阻尼井 | 时间指针磁吸停顿，出现橙色预警光晕与风险归因雷达 | 阻尼吸附手感与触感反馈 |
| `cockpit-main` | Fly-by-wire Freeze (原位冻结) | 人工主动按下空格 | 专家决定修正参数 | 时间停滞，右侧分支预测（Ghost Fork）显示预估胜率对比 | 实时参数推演预览与无缝合流 |
