# Direction Probe Brief: AI 自动编排流协同决策台 (Agent Detent Cockpit)

- Mode: `direction-probe`
- Probe ID: `cockpit-p1`
- Repository root: `/Users/hobart/Codex/design-prototype-kit`
- Probe target path: `prototype/experiments/probes/cockpit-p1/index.html`
- Core design thesis: 为高危金融/风控 Agent 编排流提供亚秒级电传接管中控。以“自动巡航操纵杆（Fly-by-wire Detent）”为核心隐喻，摒弃全局阻塞弹窗，以时间轴磁吸阻尼与原位瞬时冻结重构人机协同手感。

## Walking Skeleton Core Interactions (必须完整实现并可交互)

1. **Zone A: 1:N Fleet Confidence Horizon (百流置信地平线)**:
   - 顶部全景雷达，实时流式展示 24+ 路并发自主智能体流水线的吞吐量、状态与置信度。
   - 颜色语义：置信度 ≥85% 为极速巡航状态（冷色/青绿低噪微光）；70%~84% 为阻尼预警（琥珀/暖金光晕）；<70% 触发阻尼井强制捕获。
   - 支持键盘 `[` 与 `]` 快速在并发流之间切换聚焦。

2. **Zone B: 1:1 Spatial Detent Rail (空间阻尼时间轴跑道)**:
   - 居中展示当前聚焦流水线的时间展开轨迹（Waypoints）。
   - 每个航路点（Step）具有真实的参数流（如“对冲调仓”、“滑点容差”、“仓位敞口”）。
   - **核心灵魂手感（Magnetic Snap）**：在低置信度（如第 14 步置信度 72%）与大额动作点，时间轴自动生成“重力阻尼井（Detent Well）”。当用户拖拽或用左右光标巡视时间指针时，靠近阻尼井会有平滑的粘滞减速与物理磁吸锁定（Magnetic Snap），并展开带有声学/光学微振动的警示雷达。

3. **Zone C: 1:1 Fly-by-wire Takeover (空格瞬时冻结与分支原位微调)**:
   - 任何时刻长按或轻按 `Space` 键，全场时间流毫秒级原位定格（Freeze Frame）。
   - 跑道中央瞬时展开电传参数调控盘（Fly-by-wire Detent Dial），操作员可通过拖拽滑块或键盘光标微调 Delta（如将滑点从 1.5% 压低至 0.4%，将持仓比从 60% 削减至 25%）。
   - 右侧即时浮现**阴影分支预测（Ghost Forking）**：高亮展示人工干预分支（Manual Intervention）与智能体原始分支（Autonomous Ghost）在收益率、胜率、回撤风险上的差分对比。
   - 按下 `Enter` 或释放确认合流（Merge Stream），系统消除分支并全速恢复巡航；按下 `Esc` 放弃干预回退。

4. **视觉与设计底线 (Anti-Toy Standards)**:
   - 工业级深色座舱质感（Jet Black `#0a0b0e` + 航空高反差电传字阶）。
   - 数据展示全量采用 Tabular Mono (`font-variant-numeric: tabular-nums`) 严格对齐。
   - 零全局 Blocking Modal 弹窗；所有微调与决策均在原位时间轴与右侧视窗内闭环。
   - 原生 HTML + CSS + JS 单文件自包含，零外部 npm 构建依赖，开箱即用。
