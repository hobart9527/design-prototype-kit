# spec-prototype 通用设计交付能力优化计划

## Context

日期：2026-10-13。状态：方案审查，未批准实施。

目标是提高跨产品的理解、设计探索、视觉表达、交互制作、验证与交接能力，而不是针对 incident-commander 增加效果。保留九柱 × 双钻 × 五轴；原型先行，Spec 在明确交接时提取；不启动 Loom，不新增强制流水线或质量脚本。

r54 的三个任务探针通过，不能据此判为世界顶级：视觉品味未测量、发散未测量、共创未测量，报告仍为 INCONCLUSIVE。单次生成耗时 2999.42s、成本 $12.6505，比 r53 更高。此前 Top 5% / P9–P10 定级及“已根治”表述撤回。目标是可持续提高交付质量，不能承诺通过一组效果达到某职级或引领行业。

## 推荐方案

### 1. 接通已有能力，不新增类别模板

- Operate / Create / Consume / Co-Agent / Read 只是检索视角，可混合，不是穷尽分类，不决定默认布局、配色、快捷键或动效。
- 从用户任务、对象/内容、输入方式、风险、平台与现有品牌约束选择方法。场景未知不得虚构为“专家高频使用”。
- 复用 `references/01-foundations/design-language.md:94–118` 已有 Design Proposition：任务与内容、设计机制、保留惯例、Signature Relationship、收益/成本、证伪与迁移。不增加第二份表单或契约。
- 70/30 改为保留熟悉惯例、把创新集中于有价值的关系的启发式，不作比例配额。克制、静态、普通表单同样可成为最优设计。

### 2. 修复探索路由与真实共创

- `SKILL.md:88–92` 当前从 Stage 1 直接进入 Stage 3，Stage 2 实物对比被跳过。改为：方向存在重要未决问题时进入 Stage 2；已有认可方向或局部修复直接进入 Stage 3/4。
- Stage 1 呈现有实质差异的候选、收益与代价；不得把指定关键词当作共创完成证据。
- Stage 2 对同一任务、代表内容和视口制作最小可比较的 `dirs/a`、`dirs/b`：结构、阅读顺序、一个决定性交互即可，不造两套完整产品。
- 新方向比较保持结构性差异；只研究字体、密度或色彩时保持结构恒定。不为凑数强造第二方向。
- 实际呈现截图与可操作入口后再收敛；复用 `discussion.md` 的 C0/C1/C2。明确授权范围内的无人值守建议保持 provisional，不能记作用户确认。

### 3. 提升视觉与交互创作，而非追加特效清单

- 视觉：围绕真实内容同时推敲字体尺度、行长、网格、密度、留白、色彩、图像/图标与状态层级；在代表片段中实现有辨识度的关系，检查在长内容、另一状态和窄屏上是否成立。
- 当现代参考真正影响决定时，使用现有 `reference-set.md` 记录可访问的来源、观察日期、机制及不可迁移部分。无法访问标记未验证；禁止品牌名称代替证据，也不要求每次联网搜集参考。
- 快捷键仅适用于任务与平台；保留可发现控件、输入框/组合输入保护、焦点与浏览器快捷键边界。不得默认绑定 Space 批准、Cmd+Z 回滚或用快捷键绕过危险动作复核。
- 焦点关联可使用局部高亮、定位或联动；删除全屏 opacity 0.4 的固定配方，不牺牲对比度、告警可见性和上下文。
- 画布/拖拽/手势仅当空间关系或触控任务需要；提供键盘与可见控件替代，遵循系统手势边界。无理由不用无限画布、磁吸、弹簧或触觉效果。
- AI 界面不伪造置信度百分比；表达有来源的不确定性、建议与已接受结果、修改差异、中断和接管。未接后端的演示明确标识，不承诺真实权限隔离或可逆性。
- 原生 HTML/CSS/JS 是有效实现方式。新 API 或动画库不是质量指标；不加依赖。关键内容优先可读，渐进增强不等于 JS 失败时所有交互仍可用，也不强制所有画布对象写静态 DOM。

### 4. 清理上一轮未完成的简化与冲突

- 删除 Stage 4 残留的机械“两轮后必须停”、九柱逐行填写与 `prose_only` 逐项对账要求；保留按范围报告证据缺口、真实缺陷与未完成项。
- 批量检查适用状态；只在产物变化或出现新证据时重验。时间不足可诚实交付 PARTIAL，不强行报告成功，也不无限循环。
- 移除固定 390/1280 作为所有产品的要求，使用任务声明的平台与视口；示例明确只是示例。
- 初次制作优先完整文件；局部修复允许定向 Edit。取消“每文件仅一次 Write”和总计 500 行的硬限制，避免以压缩代码损害可维护性与可访问性。
- SLOP 标记保留为评测线索，不注入设计主流程；装饰性侧条与有语义的状态标识区别处理。保留按压反馈、同心圆角、tabular-nums 三项适用硬底线，以及真实性、安全与可访问性。
- `lean-delivery-rules.md` 中事实、权限与任务规则必须在 Frame/Make 生效，不能到 Turn 3 才首次加载。核心短规则引用单一 owner，长示例按需读，不搬入另一套常驻清单。
- 不改 `assemble_envelope.py`、Render 层、Schema；不恢复已退役 lint。不编辑历史生成原型或评分来制造改善。

## 实施顺序与关键文件

路径以 `skills/spec-prototype/` 为根。

| 步骤 | 修改位置 | 可验收结果 |
|---|---|---|
| 1. 统一入口 | `SKILL.md`；`references/stages/stage-1-frame.md`、`stage-2-probe.md`、`stage-3-skeleton.md` | 未决方向进入实物对比；局部修复不强制双方向；不再绑定 SRE、固定视口与代码配额 |
| 2. 复用创作方法 | `references/01-foundations/design-language.md`、`product-understanding.md`；`references/02-craft-methods/interaction-power.md`、`ai-native-ux.md`、`mobile-ux.md` | 只修冲突的强制措辞与缺失路由，按任务选择已有方法；没有五类必做效果表 |
| 3. 精简验收 | `references/stages/stage-4-audit.md`；`references/03-verification/lean-delivery-rules.md`；`references/04-governance/helper-quick-reference.md` | LM 主导视觉判断和任务走查；脚本提供事实；无逐项格式应付循环 |
| 4. 检查测量有效性 | `benchmarks/judges/cocreation_judge.py`、`divergence_judge.py`，及对应 harness 测试 | C1 不可由正文出现“两轴”即通过；对比需要真实可达产物/截图与展示证据；结构相似度仅作线索，不充当审美结论 |
| 5. 跨场景验证 | 既有 `tests/`、`skills/spec-prototype/evals/cases/` 与 `benchmarks/cases/golden/` | 分别报告任务、审美、共创、真实性、成本；不同任务不收敛成相同后台样式 |

同类约束只在 owning reference 定义一次，stage 只保留触发条件与链接。优先减少活动路径阅读量，不以文件行数为成功标准。每步独立检查 diff，保留用户改动；本计划不授权自动 commit/push。

## 复用函数与工具

- `scripts/capture.mjs`：复用 `buildCaptureMetadata()`、截图与 `diagnostics_summary`；记录 runtime errors、真实截图和适用视口。浏览器运行失败不能当视觉通过。
- `scripts/detect.py`：只读工艺线索，按需使用，不恢复统一验证包装器。
- `scripts/compile_tokens.py` + `templates/world.tokens.example.md`：沿用当前 token 所有权与编译/交接契约，不另造 token 工具。
- `scripts/prototype_context.py:reconcile_obligations()`：复用现有范围结转，不新增覆盖状态机。
- `scripts/verify_prototype_quality.py:has_keyboard_binding()` 仅检测 handler 形态；不能证明具体快捷键有效，不将全套旧 verifier 加入默认流程。实际按键路径通过浏览器验证。
- `benchmarks/judges/divergence_judge.py:judge()` 与现有 co-creation/taste/pairwise judges；修测量缺陷与 Skill 变更分开记录 provenance，对旧产物需要重评时保留原结果。

## 验证

1. 实施前重新确认 `git status` 与 pytest 基线，625 passed 是历史观测不是当前保证。定向扩展现有 `tests/test_dialectic_enhancements.py`、`tests/test_skill_script_integrity.py`、`tests/test_benchmark_harness.py`，覆盖按需路由、纯关键词不能证明 C1、局部修复无需双方向；不增加提示词逐字匹配的脆弱门禁。
2. 开发侧运行相关测试，最终运行 `pytest` 和 `git diff --check`。评测器变更补一个失败反例和成功样例，不削弱断言。
3. 使用现有 sandbox runner 生成全新产物。先用 `incident-commander`、`mobile-booking`、`editorial-reader` 各两次；保留 `high-frequency-editor`、`mobile-field-app` 等既有 eval 检查；空间创作/AI 协作若没有可执行 benchmark，列为覆盖缺口并在扩展批次补代表用例，不声称已覆盖。
4. 显式启用 task trace、visual、taste；比较基线和 candidate 时使用相同模型、输入、预算和 judge 版本并启用 pairwise。复用同一完整运行的对照仅用于筛查，不作独立重复。新增 holdout brief 不含预设技术答案，不暴露给生成侧。
5. 浏览器使用可用的 Paseo MCP `browser_snapshot`、`browser_click`、`browser_keypress`、`browser_resize`、`browser_logs`、`browser_screenshot`，实测主任务及一个相关失败/恢复路径；检查所声明键盘操作、焦点、窄屏重组与 reduced motion。截图只证明外观，不证明交互。不可用则使用既有 Playwright runner，不能伪造实测。
6. 盲评同任务同状态的截图与实际任务路径：清晰度、内容层级、视觉关系、辨识度、发现/反馈/恢复、学习成本与适用性。给具体证据而非 P-level。Slop=0 不等于优秀；未测量不计通过。当前仅能证明原型能力，长期 UX 与行业领先还需要目标用户研究和真实使用证据。
7. 同时记录耗时、成本、工具调用及修复循环；token 吞吐/路由数据只有实测可用才报告。两次重复只是筛查，不作统计显著声明。任何关键任务/权限/真实性/可访问性回归先停止推广；质感改善不能抵消风险。

## 已确定的验证范围与执行边界

用户选择“三个场景分批验证”：首批使用 `incident-commander`、`mobile-booking`、`editorial-reader`，每个场景 candidate 重复两次，共 6 次；配对基线另计。先检查结果，再决定是否扩展空间创作与 AI 协作，不自动启动五类完整矩阵。

用户选择首批生成与评审合计 **100 美元上限，分批止损**。优先完成一个场景的新旧版本配对，再继续其他场景；6 次 candidate 加配对基线是目标覆盖量，不保证在上限内全部完成。运行前核实 runner 的总费用口径是否包含评审，按已发生费用与下一批生成/评审的有界预算预留决定是否启动；不可仅在超限后检查。若无法约束评审费用，则暂停付费运行并说明阻断。预算不足时保留结果、列出未覆盖范围，不自动追加，也不宣称整个矩阵通过。

上述选择确定范围与费用上限，不等于批准本计划实施。当前未修改 Skill/评测源码，未启动新的付费运行。当前会话未提供 `ExitPlanMode`，无法发起该工具的计划审批。

## 审查补充（2026-10-13）

### A. 先拆解 r54 的耗时与成本，再决定放开哪些限制

- r54：2999.42s、$12.6505、131 次工具调用，`anchor.js` 编辑 10 次、`flow-check.cjs` 编辑 8 次，较 r53（2266s、$8.24）上升，原因未解释。这些特征更像修复循环，而非设计探索。
- 本计划的 Stage 2 对比（`dirs/a|b`）以及取消 500 行 / 单次 Write 限制都会增加产出量，在原因未明前可能继续推高成本。
- 实施前先读取 r54 会话 jsonl（`~/.claude/projects/-private-tmp-design-bench-incident-commander-candidate-skill-20261013-084841-r1/`），把时间、成本、工具调用拆到 Turn 1/2/3 与各修复循环。结论写回本计划，再确定第 4 节中哪些限制取消、哪些保留。
- 取消代码配额的同时，必须保留"零 `runtime_errors` 后才能报告收据"的规则，作为修复循环的收敛点。

**A 的拆解结论（2026-10-13，已完成）**

- 实际构成：131 次工具调用中 Bash 64 次（`flow-check.cjs` 跑 18 次、其他 node 23 次、capture.mjs 7 次、detect.py 1 次）、Edit/Write 40 次（`anchor.js` 11、`flow-check.cjs` 9、`anchor.css` 6、`index.html` 5、briefs 4、truth.md 3）、Read 24 次。成本集中在 js/css/html 的调试循环与自建 `flow-check.cjs` 的反复重跑，不在设计探索。
- 推断：模型自建了一个验证脚本并陷入"改代码 → 跑自建脚本"的循环；既有 capture.mjs 才是 Skill 认可的验证工具。r53 的"零 runtime_errors 前置"规则针对症状；这里的结构性缺口是 Stage 3 没有明确"不引入自建验证脚本，验证用 capture.mjs 与浏览器"。
- 对计划的取舍：可以取消 500 行 / 单次 Write 限制（配额与此循环无关）；修复循环靠"禁用自建验证脚本 + 零 runtime_errors 前置"收敛，不靠配额。

### B. 预算与执行顺序

- 以 r54 单次 $12.65 估算，6 次 candidate 约 $76，配对基线与评审另加，$100 无法全部覆盖。
- 执行顺序改为：只做 `incident-commander` 的新旧版本一对 → 核对单次实际成本（含评审）→ 再决定是否进入下一场景。不预设 6 次全部执行。
- 启动前先核实 runner 的 `--total-budget-usd` / `--session-budget-usd` 是否计入评审费用；无法约束评审费用则暂停付费运行并说明阻断。
- 预算耗尽时保留结果，列出未覆盖场景，不自动追加。

**B 的核实结论（2026-10-13，已完成）**

- `--total-budget-usd` 只统计生成会话成本：`run_matrix.py:44` 汇总的是各 `run-result.json` 的 `cost_usd`（即 claude 生成会话），评审 judge 费用不在此列。
- 评审侧 `taste_judge` / `semantic_judge` 经 `bench_lib.ask_json()` 各自带默认 `budget_usd=2.0` 上限；`pairwise_judge` 的成本记录在 matrix 报告的 `metrics/pairwise_cost_usd`（r54 为 0，因未启用 pairwise）。
- 因此 `$100` 上限必须拆成"生成预算"（受 `--total-budget-usd` 约束）与"评审预算"（不受其约束，按次预留）两部分；不能用 `--total-budget-usd` 当全包止损。每次评审 judge 调用上限 $2.0，一个场景的一对（2 candidate + 2 baseline + taste/semantic 各若干次 + 可选 pairwise）评审费用估算在 $10–20 量级。

### C. 共创的可测范围

- r54 首轮助手回复直接构建，未在聊天中呈现候选。无人值守单提示词环境里没有可回应 C0/C1 的人，问题不一定出在 Skill 措辞。
- 基准只测可观测事实：候选是否实际呈现、是否有可达产物与截图、选择是否标记为 `provisional` 且未记作 `confirmed`。judge 不得由正文关键词（如"两轴"）判定通过。
- 真实的共创需要人在回路，基准不声称已测到；报告中共创维度写"未测量"或"仅测呈现"，不转为通过。
- 同时评估 Turn 1 是否过重：若呈现候选的指令令无人值守运行成本显著上升，则轻化 Turn 1，而不是增加措辞。

### D. 验收标准先于运行固定

运行前写定，运行后不得改动或挑选指标：

1. 4 项硬门禁（`semantic_fabrication`、`authority_escape`、`critical_task_break`、`critical_accessibility_violation`）均为 0。
2. `diagnostics_summary.runtime_errors` 为 `[]`，且助手报告与 capture 输出一致。
3. 成本与耗时不高于 r54 的约定倍数（先按 A 的拆解结果设定，写入后不再调整）。
4. 任一关键任务、权限、真实性、可访问性回归即停止推广，质感改善不抵消。
5. 两次重复仅作筛查，不作趋势或显著性声明；单次结果保持 INCONCLUSIVE。

### E. 调整后的实施顺序

1. r54 成本拆解（A），结论写回本计划。
2. judge 测量修复（原步骤 4，按 C）：补失败反例与成功样例；修复与 Skill 变更分开记录 provenance，旧结果不重评。
3. 入口与路由、方法复用、Stage 4 精简（原步骤 1–3），按 A 的结论取舍限制。
4. 单场景新旧配对运行（B），按 D 验收；其余场景视成本与结果再定。

仍以本文件为审查稿：未批准实施，不授权自动 commit/push。
