# spec-prototype Skill 全链路走查报告

- **日期**: 2026-09-30
- **对象**: HEAD `6a51914`（refactor(spec-prototype): introduce layered design records and 3-turn lean delivery）
- **分支**: `refactor/spec-prototype-layered-delivery`
- **测试基线**: `python3 -m pytest -q` → **505 passed, 38 skipped, 0 failed**（1174s），与提交声明一致

## 走查方法

1. 全量阅读 SKILL.md / CONTEXT.md / core-kernel.md / 全部 stage 文档（0-5）/ 治理文档（design-record、execution-boundary、handoff、artifact-lifecycle）/ 模板（truth、world、_slice、discussion-seam）/ 关键脚本（execution_boundary、compile_spec_ir、compile_tokens、verify_prototype_quality、handoff、capture.mjs、detect.py）。
2. 在空仓库对 `execution_boundary.py` 做 hook 冒烟模拟：覆盖首写门禁、layered/single-record 两条路径、主链全部 Bash 命令形态（capture、compile_tokens、compile_spec_ir、wcag-check、freeze）。
3. 两个独立只读走查探针分别覆盖 Turn 1-3 主链一致性与 Stage 5/脚本层；探针结论逐条经主会话实证复核（含对两处探针误判的证伪）。

---

## 一、总体结论

**翻转基本落地，主链设计上是通的。** "原型先行、Spec 后置"在核心资产上一致：SKILL.md（304→121 行）大幅瘦身、core-kernel 三条不变量改写正确、stage 文档不再要求写码前置 Spec、verify 已从 verdict 改为 signal（failures 管 exit code、signals 只打印）、lint 退役六件套。hook 冒烟证实：空仓库首写记录 → 写 anchor HTML → capture / compile_tokens / compile_spec_ir / wcag-check / freeze 全部命令形态均可通过边界。

**存在 3 处真实断裂点和 10 处摩擦点**，集中在三类：模板与 stage 文档口径打架、Stage 5 命令序列的隐含前置未写明、agent 定义残留旧的 verdict 语义。全部是文档级修复，不需要再动脚本架构——本次重构已把"拦截检测"收敛到正确位置（写边界 + capture 硬事实 + Stage 5 编译门槛），剩下的问题是措辞与衔接，不是过度设计的回潮。

---

## 二、阻塞级问题（端到端会真的走不通）

### B1. Physical Anchor 双口径 — 模板设卡、stage 放行

- `templates/discussion.md:67-70`：写 "An undeclared anchor blocks formal Stage 2"。
- `references/stages/stage-1-frame.md:128-134`：同一声明是 Optional Guidance，"without acting as a blocking gate"。
- 同一事实两处相反。编译器只在 `--required-tier stage2` 时硬要求 anchor（compile_spec_ir.py:1521），而该 tier 已不在任何主链文档的命令里，进一步支持放行口径。
- **修复**：以 stage-1 为准，删除模板中的 "blocks formal Stage 2" 句。

### B2. `required_states` 模板与编译器互相矛盾

- `templates/briefs/_slice.md:57-59`：指导 "Leave it out until they are known"。
- `compile_spec_ir.py:228-232`（`_REQUIRED_SECTIONS`）：把 `required_states` 列为 `execution_spec` 必需段。
- 后果：按模板老实写 brief 的 slice 到 Stage 5 先天缺块，freeze 第一步（`compile_spec_ir --required-tier execution_spec`）必败。
- **修复**：模板改为 "Turn 3 定稿前必须补齐本块；未填时 freeze 会拒收并列出缺项"，把"先不写"降级为"探索期可不写"。

### B3. Stage 5 freeze 的隐含前置链未文档化

- `handoff.py freeze` 硬要求 `prototype/shared/tokens.css` 存在（handoff.py:490-509），且 compile_spec_ir 必须先以 `execution_spec` 达成；Decisions 表需有本 slice 的 `confirmed|delegated` 行（handoff.py:594-651，需同时命中 approval-source、locator、slice_id 三组 marker）。
- stage-5-freeze.md 的四步顺序恰好正确，但没写明"任何一步失败时后续全部不可达、失败点就是前置清单"。
- **修复**：在 stage-5-freeze.md 开头加 5 行前置检查清单（state 模型块齐全 / tokens.css 已编译 / Decisions 表有本 slice 的 confirmed|delegated 行 / t1.json 已生成 / wcag 通过），每行附对应修复命令。纯文档修复，把 freeze 失败从"逐层踩雷"变成"一次自检"。

---

## 三、摩擦级问题（不自锁，但每次交付都耗 token/耐心）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| F1 | SKILL.md:66 Turn 3 "Spec extracted" vs stage-4-audit.md:204 "Stage 5 仅用户要求才跑" | 无人追问时 Turn 3 出口口径不一致 | SKILL.md Turn 3 改为 "review + repair 记录即完成；Spec 抽取与 freeze 是显式 opt-in" |
| F2 | stage-3-skeleton.md:103-110 要求 token link 从 IR 读 | IR 在 Stage 5 才存在，Turn 2/3 无 IR 可读 | 改为 "anchor 位于固定深度，相对路径 `../../../shared/tokens.css` 可直接写；Stage 5 编译后由 IR 校验一致性" |
| F3 | stage-4-audit.md:138 引用 `syncReviewPortal` | 该命令不存在；实际是 `generate_review_portal.py` | 统一为脚本名并给出调用形态 |
| F4 | stage-1-frame.md:142 "编译为 intent.json / Spec IR" | intent.json 现行地位不明（边界仍在写时校验它，编译器容忍缺失） | 一句话定性："intent.json 是可选的 Stage 1 机器加速件，缺失时编译器从记录散文恢复" |
| F5 | capture 降级路径只写在 stage-4-audit.md:146-158 | stage-2-probe.md:42-45 与 SKILL.md Turn 2 出口硬性要求 captures；无浏览器时 Turn 1/2 按字面不达标 | 在 stage-2 补一段："无浏览器时 Turn 1/2 出口为 `PARTIAL` + `visual_evidence: unverified`，转 Stage 4 补验"（stage-4 已有完整语义，只差前向引用） |
| F6 | `_slice.md:1-10` frontmatter 的 `authority/stage/applied_methods` 枚举无注册表 | machine-contract.md 只管 `contract:` 块，不管 frontmatter | 在 machine-contract.md 加 frontmatter 枚举表 |
| F7 | discussion-seam.md:17 checkpoint 词汇（`stage2-probe`）与 `_slice.md:5` 的 `stage: hero_probe` 不同源 | 两套 stage 命名并存 | 统一为一套词汇表 |
| F8 | agents/spec-prototype-builder.md:396 仍写 "STATIC: pass verdict line"；critic 同时有 "fail the build" 与 "仅 advisory" | 与 verify 的 signal 口径语义漂移 | builder 改 "signal 行"；critic 统一 "fail the build 仅指三项工艺硬缺陷 + 无障碍地板" |
| F9 | 无人值守流天然到不了 freeze | Turn 1 只记 `proposed`，freeze 要 `confirmed` | 文档明示：无人值守终点是 `PARTIAL/provisional`，freeze 需要真实用户确认——是设计意图不是缺陷，但要写出来防误报 |
| F10 | `draw_seed.py --write` 在 layered 树写不进 brief（缺 `## Slice:` 块） | 退化为手工记录，易丢 | 低优先；stage-2 示例命令补一句 layered 下落点 |

---

## 四、派发路径（subagent envelope）— 唯一残留的过度设计集中区

`execution_boundary.py:82-148` 的 `dispatch()` 要求 builder 的 prompt 是 `packet_for()` 精确匹配的 JSON 或两种受管 envelope（direction-probe / lean-builder-envelope），含逐字节 stale-digest 校验和 Build Authority Gate（envelope 含 `[Hypothesis]` 动作且目标为 formal 时拒派）。这是全 skill 复杂度最高的机制，而 SKILL.md 已明确主设计师直写是主路径、subagent 可选。

**判断**：机制本身自洽（有测试覆盖），但与"主设计师拥有全生命周期"的新定位存在张力。建议不动代码，做两件事：

1. SKILL.md Delivery 段补一句："subagent 派发的 packet 协议属 formal handoff 通道；日常 Turn 1-3 的 detached exploration 用 direction-probe envelope，不要用 lean-builder-envelope 走 formal-candidate（会撞 Build Authority Gate）"。
2. 中期考虑把 lean-builder-envelope 的 stale-digest 校验从边界下沉到 handoff.py 自身——边界只验形态，内容新鲜度由生产方自检。符合"边界是工具准入口、不是内容审批"的既有原则。

---

## 五、verify/lint 收敛质量确认（本次重构最干净的部分）

实证确认：

- `verify_prototype_quality.py` 的 failures/signals 双通道实现正确（assert_quality 注释明示 "Two output channels, and only one of them moves the exit code"），signal 不影响 exit code，主链文档零调用——"软校验退出主链"真实成立。
- craft-floor 三项硬缺陷（`:active` / 同心圆角 / `tabular-nums`）口径在 craft-floor.md / verify / detect.py / capture.mjs 四处一致。
- `lint_spec_contracts.py` 退役六件套后 E001/E022 定位清晰；边界强制 `--root --slice` 属合理收敛。
- shell 白名单实测主链全通；`git log/diff`、`python3 -m pytest`、`mkdir` 均放行（走查探针的相反指控经实测证伪——白名单字符检查发生在 `shlex.split` 之前，空格分隔的参数形态全部可达）。唯一小瑕疵：freeze 的 `--root .` 相对路径被等值校验拒绝（`Path('.').resolve()` 在脚本进程 cwd 下解析，不一定等于 payload cwd），文档统一写绝对路径或 `$PWD` 即可。
- capture.mjs 自带 `mkdirSync(outputDir, {recursive:true})`，证据目录无需手动 mkdir。
- 边界对 builder/critic 工具负载有快速返回（execution_boundary.py:397-404），不限制内部 Bash 自由——主链外的 subagent 不被边界误伤。

---

## 六、关于"P9+ 设计专家能力栈"的评估

机制层面这个 skill 已具备顶级设计师的**工作流骨架**：张力先行（Frame）、结构性发散（Divergence Generator 六步 + 两轴裁决，Structure 为必选轴）、真实渲染证据闭环（capture → 看图 → 修复）、品味账本（world.md 的 Taste Ledger）、Signature Moment 预算（70/30 按 Operate/Read/Persuade/Experience 四 mode 调制）、诚实的 `PARTIAL` 语义（宁记未验不装通过）。设计语言参考库（design-language.md 六块契约、modern-style-vocabulary、Five Axes）提供判断的词汇表而非菜单，分寸正确。

要真正逼近 P9+，缺的不是更多检查，而是两处心智缺口（建议后续迭代补齐，本轮不必动）：

1. **看图能力的制度化**——stage-4 已有"先写判断再看检测输出"的正确顺序（step 3a/3b），但模型实际读 PNG 的质量取决于 prompt 里对"看什么"的引导密度；stage-4 的 Direction Contract 对照表（THESIS/OWN-WORLD/STORY/FIRST VIEWPORT/FORM/FINISH 六问）很好，可在 capture 收据里强制回链到该表。
2. **修改的算子化**——operators.md 已存在但 stage 文档引用稀疏；把 "bolder/quieter/tighter" 类请求的 refine-operator 纪律（目标轴、from→to、不变量、证伪器，一次一个算子）提到 SKILL.md 的 Craft 段一行，能显著减少"重写而非修复"的模型本能。

---

## 七、修复方案（按序执行）

全部为文档/措辞修复，零脚本架构变更，一个交付批次内可完成：

1. **B1**：删 `templates/discussion.md:70` 的 blocking 句。
2. **B2**：改 `templates/briefs/_slice.md:57-59` 的"先不写"口径为"freeze 前必填"。
3. **B3**：`stage-5-freeze.md` 开头加前置检查清单。
4. **F1-F3**：SKILL.md Turn 3 出口口径、stage-3 token link 措辞、stage-4 review portal 命令名。
5. **F4-F7**：intent.json 定性句、stage-2 capture 降级段、frontmatter 枚举表、stage 命名统一。
6. **F8**：builder/critic 的 verdict 语义对齐 signal 口径。
7. 每条修复配既有测试文件的断言同步（test_canonical_ontology / test_v10_integrity 锁有措辞断言），收尾 `python3 -m pytest -q` 全绿。

---

## 附录 A：hook 冒烟测试实录（/tmp/sp-fresh 空仓库）

| 操作 | 结果 |
|---|---|
| 首写 `prototype/truth.md`（layered 锚点） | 放行 |
| 记录非空后写 `experiments/slice-a/anchor/index.html` | 放行 |
| 写 `prototype/shared/tokens.css` | 放行 |
| 写根目录外文件 `outside.md` | 拒绝（正确：必须驻留 prototype/） |
| 记录存在但为空时写其他 artifact | 拒绝（正确：先更新设计记录） |
| `node capture.mjs <file> --output <dir> --viewports …` | 放行 |
| `python3 compile_tokens.py --discussion prototype/world.md` | 放行 |
| `python3 compile_spec_ir.py --slice x --required-tier execution_spec` | 放行 |
| `node wcag-check.js … --level AA` | 放行 |
| `handoff.py freeze --root . --spec …` | 拒绝（`.` 相对路径解析不等值；绝对路径放行） |
| `handoff.py freeze --root <abs> --spec …` | 放行 |
| `python3 -m pytest -q` / `git log` / `git diff --stat` / `mkdir -p` | 放行 |

## 附录 B：关键脚本健康度

| 脚本 | 行数 | 状态 |
|---|---|---|
| compile_spec_ir.py | 1783 | 分层读取 seam（read_design_record）正确；tier 准入门清晰；intent.json 缺失回退散文恢复 |
| compile_tokens.py | 1500 | formal/probe 双模正确；layered 树下确认文本合并 truth.md（_confirmed_authority_text） |
| verify_prototype_quality.py | 1704 | failures/signals 双通道正确；主链零调用 |
| handoff.py | 1031 | freeze 三层前置（tokens.css → approval binding → digest）顺序正确；layered 读 truth.md |
| lint_spec_contracts.py | 335 | E001/E022 定位清晰，六件套已退役 |
| execution_boundary.py | 468 | 首写门禁、layered 锚点、spec_view_advisory 均正确；dispatch 协议自洽 |
| capture.mjs | 666 | 三级降级（playwright → 系统浏览器 CLI → browser_unavailable exit 2）；自建输出目录 |
