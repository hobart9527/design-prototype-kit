# spec-prototype 优化落地审计与修复方案

- **日期**: 2026-09-30
- **审计对象**: HEAD `6a51914`（`refactor(spec-prototype): introduce layered design records and 3-turn lean delivery`）
- **审计基点**: `main...HEAD`（`010a34a` → `6a51914`，45 files changed, +2475 / -786）
- **分支**: `refactor/spec-prototype-layered-delivery`
- **方法**: 只读走查。全部结论先给反证、能实测的一律实测复现，不能复现的撤回。
- **配套文档**: 文档级走查（B1–B3 / F1–F10）见 [2026-09-30-spec-prototype-layered-delivery-review.md](./2026-09-30-spec-prototype-layered-delivery-review.md)。本文聚焦**运行时行为核验**与**可执行修复方案**，两者不重复。

---

## 一、总体结论

**优化方向正确，但端到端链路未闭环。当前不能认定 spec-prototype 已实现可靠的设计交付闭环。**

三类事实：

1. **翻转本身落地良好**。原型优先（Stage 5 才编译 Spec/Token）、`--required-tier execution_spec` 硬失败、verify 的 failures/signals 双通道、lint 六件套退役——这些在代码里都成立，不是纸面声明。
2. **身份、生命周期、证据三条接缝存在真实断裂**，其中两条会让**正常交付路径走不通**（P0），需要修脚本而不是改措辞。
3. **此前的走查（含本会话早段）有 3 条结论被本轮复现推翻**，见 §3，其中一条方向恰好相反。审计自身也需要留痕，避免后人照抄错误结论。

**优先级判断：停止继续做治理层重构，先把 §2 的 5 条接缝修完。** 继续加检查层只会让"设计交付"进一步被"拦截检测"挤压，与本次优化的既定目标相悖。

---

## 二、已证实缺陷

每条给出：现象 → 证据（`file:line`）→ 复现 → 最小修复。除标注外，均在本次审计中实机复现。

### P0-1 canonical freeze → gate 身份错配，交付链路在第二步断裂

冻结写进目录 A，门禁去目录 B 查，两者永不相交。

- `handoff.py:474` — `candidate_id = spec_path.name.removesuffix(".spec.md").removesuffix(".md")`，`r1.spec.md` → `r1`
- `handoff.py:816` — 冻结落盘 `prototype/evidence/<slice>/<candidate_id>/freeze-manifest.json` → `.../reader/r1/`
- `handoff.py:903` — 门禁 `evidence_dir = root / "prototype/evidence" / slice_id / spec_path.stem`，`r1.spec.md` → `r1.spec`，查 `.../reader/r1.spec/`

`removesuffix` 链在第 474 行是正确的（先剥 `.spec.md`）；缺陷在第 903 行用了未经归一化的 `stem`。

**复现**（`/tmp/sp-canon`，canonical `.spec.md` + 合法 approval 行 + tokens.css + prototype scope）：

```
$ handoff.py freeze --root /tmp/sp-canon --spec prototype/specifications/reader/r1.spec.md
(成功，manifest 写入 prototype/evidence/reader/r1/freeze-manifest.json)

$ handoff.py gate --root /tmp/sp-canon --slice reader
prototype_blocked: Downstream Gate Blocked: Specification for slice 'reader' is
'validated' but not yet frozen.
```

冻结产物存在、内容合法，门禁仍判"未冻结"——**下游工程准入在 canonical 路径上永远不可达**。

**为什么没被测试拦住**：`tests/test_spec_only_freeze.py` 全程使用 legacy `r1.md`（`spec_path.stem` == `r1`，两处恰好相等）；`tests/test_handoff_scope_integrity.py:110` 同样。`tests/test_canonical_spec_ir.py:455-489` 只验 `pillar_packet` 的字段，**没有任何测试做过 canonical 的 freeze → gate 往返**。这正是"两个函数各写一份身份推导"的典型后果。

**最小修复**：抽出唯一身份函数，两处共用。

```python
# handoff.py 模块级
def candidate_id_of(spec_path: Path) -> str:
    return spec_path.name.removesuffix(".spec.md").removesuffix(".md")
```

`:474` 与 `:903` 都改为 `candidate_id_of(spec_path)`。补一条 canonical 往返测试：freeze 后 `check_downstream_gate` 必须 `passed`。

---

### P0-2 可变设计记录被纳入冻结，"追加一行进度"即阻断下游准入

`artifact-lifecycle.md:12` 与 `:65` 明确规定设计记录 `always mutable; never a freeze subject`；`stage-5-freeze.md` 也写 `prototype/discussion.md is the evolvable decision record and is never a freeze subject`。实现与之相反。

- `handoff.py:796-801` — `frozen_artifacts` 展开 `*[retained(root, rel) for rel in sorted(design_record.parts)]`
- `read_design_record` 的 `parts` 覆盖：single-record 的 `prototype/discussion.md`；layered 的 `truth.md` + `world.md` + `briefs/<slice>.md`
- `handoff.py:854-874` — `downstream_admission` 对 `frozen_artifacts` 逐字节校验

**复现 A（single-record）**：

```
freeze → gate: passed / admission: passed
$ echo "- progress note: reviewed the render" >> prototype/discussion.md
admission: prototype_blocked: prototype/discussion.md changed after freeze
(6e54d692 != ff824d6e); re-freeze before admission.
```

**复现 B（layered）**：同样操作追加到 `prototype/truth.md`，`admission` 报 `prototype/truth.md changed after freeze`。注意冻结清单实测含 `prototype/truth.md`——

```
frozen_artifacts: [..., 'prototype/product.md', 'prototype/specifications/reader/r1.md', 'prototype/truth.md']
```

后果：Stage 4 的评审记录、Taste Ledger 追加、`PARTIAL` 标注——全部是**设计动作本身**——每做一次就要重新冻结。设计记录越被认真维护，准入越容易被撞断。

**最小修复**：`frozen_artifacts` 只收不可变交付物，剔除 `design_record.parts`。审批来源的完整性已由 `approval_binding` 的 `source` 单一 digest 覆盖（`handoff.py:823-852` 已单独校验 `binding["record"]` 与 `binding["source"]`），无需整份记录入冻。

```python
"frozen_artifacts": list({
    artifact["path"]: artifact
    for artifact in [
        pkt["specification"],
        *pkt["required_reads"][1:],
        # design_record.parts 移除：记录按 lifecycle 定义可变，不参与字节冻结
        ...
    ] if artifact
}.values()),
```

若确实要对审批行做防篡改，正确做法是**只冻审批行本身的规范化文本**，不是整份记录。改完需同步 `tests/test_spec_only_freeze.py` 中断言 `prototype/discussion.md` 在冻结节内的用例。

---

### P1-3 Token 规则四处互斥，按 stage-2 指导写码必被判 `out_of_sync`

同一动作在四处得到相反判决：

| 位置 | 声明 |
|---|---|
| `stage-2-probe.md:40` | `Directly write or adjust prototype/shared/tokens.css` |
| `stage-5-freeze.md:27` | `Direct authoring of tokens.css is standard in Stage 1~3 exploration` |
| `design-record.md:21` | `compile_tokens.py is the only writer of tokens.css and t1.json` |
| `stage-5-freeze.md:22` | `It does not read tokens.css back: the flow is one-way` |

**复现**（`/tmp/sp-tok`）：

```
compile_tokens.py --discussion prototype/world.md   → check_tokens_sync: in_sync
echo ':root { --bg-surface: #ff00ff; }' > prototype/shared/tokens.css
                                                        → check_tokens_sync: out_of_sync
```

`compile_tokens.py:1376-1389` 的 seal 语义要求 `tokens.css` 字节等于"从源重编的字节"。**探索期手写即失联**，而这恰是 stage-2 让模型做的事。

**严重度说明**：`check_tokens_sync` 的非测试调用者只有 `lint_spec_contracts.py:263`，而后者是 Stage 5 可选助手，主链文档零引用。所以当前**不构成硬阻断**——但规则本身自相矛盾，且编译会静默覆盖探索期手写值（实测 `--discussion world.md` 编译直接改写 `tokens.css`）。

**最小修复**：统一为一条规则并写清代价。

- `design-record.md:21` 改为：`compile_tokens.py 是 t1.json（派生包装）的唯一写者；tokens.css 在探索期可由设计师直写，一旦编译则以编译产物为准，探索期手写值需先回写至设计记录。`
- `stage-2-probe.md:40` 补一句：`探索期直写 tokens.css 属正常路径；Stage 5 编译前须把最终值回写 world.md/discussion.md，否则编译覆盖手写值。`

不建议削弱 seal——单向派生是 Token 权威性的支点，代价记录在文档里即可。

---

### P1-4 craft floor 判定与退出码脱钩：打印 `STATIC: fail`，进程退出 0

`verify_prototype_quality.py` 的 tier 结论未回接 `failures`，`assert_quality` 的返回值只看 `failures`。

- `:1098` `probe_craft_floors` 失败 → `:1103` 置 `tiers["L2"] = {"status": "failed"}`、`evidence["outcome"] = "failed"`
- `:1616` `LAST_TIER_EVIDENCE.update(tiered_quality_evidence(...))`
- `:1620-1626` 打印分支**读 `tier_outcome`**：`elif tier_outcome in ("failed", "blocked"): print("STATIC: fail")`
- `:1661-1665` 返回分支**只读 `failures`**：`if failures: ... return False` / `return True`

两处读的是不同变量。结果：**打印 `fail`，退出码 0**。

**复现**（`/tmp/sp-vq2`，注入 `probe_craft_floors → (False, "craft floor assertion: press feedback missing")`）：

```
TIER L2: failed (craft floor assertion: press feedback missing)
STATIC: fail
assert_quality returned: True      ← 与上一行矛盾
$ python3 probe_shim.py; echo $?
0
```

相对地，`:378` 的 touch-target 失败走 `failures` 路径（`tests/test_pipeline.py` 覆盖），退出码正确。**唯 craft floor 这一条断了**。而 `agents/spec-prototype-critic.md:159` 写的是 `report a Floor VIOLATION and fail the build`——声明与实现不一致。

**最小修复**（二选一，取决于哪条语义是对的）：

- **若 craft floor 是硬地板**（critic.md 的口径）：在 `:1616` 后把 tier 失败并入返回判定。
  ```python
  if failures or tier_outcome in ("failed", "blocked"):
      ...
      return False
  ```
  注意与 `:1624-1632` 的 `environment_not_ready` 分支区分——环境未就绪仍应返回 `True`（该分支设计正确，不动）。
- **若 craft floor 只是 advisory**（`stage-4-audit.md:40-42` 的口径）：把 `:1620` 的打印分支改为不输出 `STATIC: fail`。

**必须二选一，不能两存**。同时补测试：注入 craft floor 失败，断言退出码与 `STATIC` 行一致。现有 `tests/test_quality_tiers.py:147-161` 只测了 `tiered_quality_evidence` 的内部状态，没测 `assert_quality` 的返回值——这正是漏洞所在。

---

### P1-5 capture 状态确认自证：hash 分支恒真

- `capture.mjs:63-70` — `buildStateUrl` 对非 `default` 状态自动拼 `#state=<state>`
- `capture.mjs:125-127` — 确认谓词 `declared === expectedState || hashState === expectedState`

`hashState` 读的就是 `buildStateUrl` 刚写进去的那个值，右分支无论页面是否响应恒为真。

**复现**（`node cap_pred.mjs`，直接调用谓词）：

```
empty   | url: http://x/a.html#state=empty   | declared:'' hash: empty  => confirmed: true
error   | url: http://x/a.html#state=error   | declared:'' hash: error  => confirmed: true
loading | url: http://x/a.html#state=loading | declared:'' hash: loading => confirmed: true
```

即：**页面完全没有实现 `data-state` 时，所有状态捕获仍报 `confirmed: true`**。`stage-4-audit.md:141` 的 "A state is captured only if its trigger was applied and the page confirmed it" 因此不成立——`state_unconfirmed` 仅自产自销。

**最小修复**：删掉自证分支，只认页面自报的状态。

```javascript
confirmed: expectedState === "default"
  ? !declared || declared === "default"
  : declared === expectedState,
```

若确有页面依赖 hash 驱动状态（`hashchange` 监听），则改为**先导航、后询问**：导航后重新读取 `dataset.state`，并要求与 expected 相等。这需要页面合约明确 `data-state` 是状态的可观测出口——建议同时写入 `stage-2-probe.md` 的出口要求。

**这不是纯 cleanup**：它决定 `required_states` 的捕获证据是否可信，进而决定 Stage 4 的评审是否建立在真实渲染状态上。

---

## 三、撤回的误报

同一条接缝写错方向比漏写更危险。以下 4 条经实测**推翻**，记录在此以防重犯。

| # | 早期结论 | 实测结果 | 结论 |
|---|---|---|---|
| R1 | 分层树 `released` 无接收位，写 seam 也无效 | `discussion.md` seam 写 `- Execution boundary: released` 时 `active_root` 返回 `None`（`execution_boundary.py:266-273` 先处理） | **撤回**。分层树确有 release 通道。残留弱点仅是：seam 缺失时 `:282-284` 退化为"仅看 anchor 存在且非空"。低优先，计入文档瑕疵即可 |
| R2 | `probe_craft_floors` 已实现但未接主路径 | `:1098` 在 `tiered_quality_evidence` 内调用，`:1616` 由 `assert_quality` 调用 | **撤回**。探针**在主路径上**。真问题是它的失败进不了退出码，即 P1-4 |
| R3 | 冻结后 drift 需 re-freeze 是自锁 | 确为设计行为（manifest 绑定字节） | **撤回**。但 P0-2 修正后，re-freeze 的触发面应从"记录追加"收窄到"交付物变更" |
| R4 | 缺 `verify` 调用是 P0 漏洞、应加质量门禁 | `handoff.md:119-125` 明确 spec-only 可冻、`implementation/platform/production` 恒 `pending`——有意区分设计批准与实现验证 | **撤回**。不主张新增 gate |

另有一条**降级**：Stage 5 编译会静默覆盖探索期手写 token。实测确认覆盖行为，但既然 seal 属有意设计、且 `check_tokens_sync` 不在主链，定性为**成本记录**（写入 P1-3 的修复文案），不单列缺陷。

---

## 四、测试与证据统计

- **本次定向套件**（权威相关文件，实跑）：
  `tests/test_spec_only_freeze.py` `test_handoff_scope_integrity.py` `test_quality_tiers.py` `test_craft_floor_probe.py` `test_tokens.py` `test_builder_boundary.py`
  → **81 passed, 1 warning in 261.75s**
- 上述 81 条**全绿**，同时 P0-1、P0-2、P1-4 均真实存在——**测试通过不构成交付闭环证明**，因为缺口恰好落在测试未覆盖的接缝（canonical 往返、冻结节成员、`assert_quality` 返回值）。
- **r19/r20/r21 基准报告不可作为 HEAD 完成证明**：`source_identity` 与 HEAD 不一致，r20 为 INVALID_CONTROL，r21 为单臂 INCONCLUSIVE。本轮未新增基准运行。
- 说明：本轮未跑全量 `pytest`（约 20 分钟量级），上述为定向套件结果，不能外推为全量基线。

---

## 五、修复方案（按批执行，批次间可独立验收）

### 第一批：修链路，不扩架构（P0，必须先做）

| # | 动作 | 文件 | 验收 |
|---|---|---|---|
| 1 | 抽 `candidate_id_of()`，`:474` `:903` 共用 | `handoff.py` | 新增 canonical freeze→gate 往返测试通过 |
| 2 | `frozen_artifacts` 剔除 `design_record.parts` | `handoff.py:796-801` | 追加 design record 一行后 `admission` 仍 `passed` |
| 3 | 统一 token 规则文案（唯一写者 → 派生包装唯一写者 + 探索期直写路径） | `design-record.md:21`、`stage-2-probe.md:40` | 两处口径一致，无"only writer"歧义 |
| 4 | 修 capture 状态确认谓词，去掉 hash 自证分支 | `capture.mjs:125-127` | 无 `data-state` 的页面捕获 `state_unconfirmed` |
| 5 | craft floor 语义二选一并落地（建议按 critic.md 口径并入退出码） | `verify_prototype_quality.py:1616-1665` | 新测试：craft 失败 → `assert_quality` 返回 `False`，且 `STATIC` 行与退出码一致 |

验收：冻结 → 门禁 → 准入三段全通；追加设计记录不再阻断；五项各有回归测试。收尾执行 `make unit && make architecture`。

### 第二批：把主路径收敛为"设计动作闭环"

目标：让 Turn 1–3 是一串设计动作，而不是一串前置条件。

1. **补齐 stage-5-freeze.md 前置清单**（对应走查 B3），每行附对应修复命令——把"逐层踩雷"变成"一次自检"。
2. **stage-2 补 capture 降级段落**（对应走查 F5）：无浏览器时 Turn 1/2 出口为 `PARTIAL` + `visual_evidence: unverified`，前向引用 stage-4 的完整语义。
3. **工艺摘要收窄声明**：`capture.mjs:642-645` 的 `has_active_feedback` / `has_tabular_nums` 是全页存在性（`some(...)`），不得表述为逐组件 pass。逐组件判定已由 `verify_prototype_quality.py:910-963` 实现——**复用它，不要新建**。若 Stage 4 需要逐组件信号，直接把 `probe_craft_floors` 输出接进 review 材料，不新增校验层。
4. **builder/critic 措辞对齐**：`critic.md:159`（`fail the build`）与 `:376`（`advisory evidence only`）在第一批第 5 项定案后统一。
5. **`stage-2-probe.md` 补 `data-state` 合约**（P1-5 修复的前置）：明确 `data-state` 是状态的可观测出口，capture 以它为准。

### 第三批：以作品证明能力

机制已有骨架：张力先行、结构性发散、渲染证据闭环、Taste Ledger、Signature Moment 预算（四 mode 调制）、诚实的 `PARTIAL`。缺的是两处**心智数据**，不是更多检查：

1. **看图能力的制度化**——`stage-4-audit.md:20-25` 的"先写判断再看检测输出"顺序正确，但模型读 PNG 的质量取决于引导密度。把 Direction Contract 对照表（THESIS / OWN-WORLD / STORY / FIRST VIEWPORT / FORM / FINISH）**强制回链进 capture 收据**，让每次评审都从这六问开始。
2. **修改的算子化**——`operators.md` 已存在但 stage 文档引用稀疏。把 refine-operator 纪律（目标轴、from → to、不变量、证伪器，一次一个算子）提到 SKILL.md 一行，抑制"重写而非修复"的本能。

判断"是否达到 P9+"，可用的证据只有一件：**同一 brief 下产出的原型，能否让资深设计师看不出是模型所出**。跑一次真实 brief、留档渲染与评审记录，比再加十项检查更有说服力。

---

## 附录：复现清单

| 场景 | 位置 | 关键命令 |
|---|---|---|
| P0-1 身份错配 | `/tmp/sp-canon` | `handoff.py freeze --root … --spec prototype/specifications/reader/r1.spec.md` → `handoff.py gate --root … --slice reader` |
| P0-2 记录入冻 | `/tmp/sp-var3`、`/tmp/sp-lay` | freeze → `echo '- progress note' >> prototype/discussion.md`（或 `truth.md`）→ `downstream_admission` |
| P1-3 token 互斥 | `/tmp/sp-tok` | `echo ':root { --bg-surface: #ff00ff; }' > prototype/shared/tokens.css` → `check_tokens_sync(...)` |
| P1-4 craft 退出码 | `/tmp/sp-vq2` | 注入 `probe_craft_floors → (False, …)` 后 `assert_quality(...)`，比较 `STATIC` 行与返回值 |
| P1-5 状态自证 | `/tmp` | `node cap_pred.mjs`（复制 `buildStateUrl` + 确认谓词） |
| R1 seam 有接收位 | `/tmp/sp-rel2` | seam 写 `- Execution boundary: released` → `active_root(root)` 返回 `None` |

所有复现均在临时目录进行，未改动仓库文件。

## 残留项仲裁附录（2026-10-01 收敛）

五项残留逐一定性，两项修复、两项关闭、一项保持冻结：

- **已修 H5 残差**（seal 确认关键词整行匹配）：`compile_tokens.py` 的 `_has_confirmed_token_authority` 改为按列判定——状态单元格按值定位，决策主题取首个非 ID 单元格，宽表（≥5 列）另认末列 scope；`## Confirmed Decisions` 标题捷径改为要求节体含调色板关键词。Reason/quote 列的 "token" 字样不再误升格种子调色板为 human authority。回归见 `tests/test_tokens.py::test_token_authority_requires_token_specific_confirmation` 扩展断言。
- **已修 wcag-check.js 部分解析静默收窄**：可解析组内存在但解不出 hex 的 token 进入显式 `skipped` 列表并 `exit 1`，与既有"空 schema 不得伪装通过"立场对齐（从零色收窄扩展到部分收窄）。
- **已修 preview.mjs 探针截图前缀错位**：`capturesFor` 在直接前缀 `evidence/<artifactId>/` 无匹配且 id 为多段探针形态时回退 `evidence/probes/<首段>/`，探针截图不再跌入 "Additional evidence" 桶。回归见 `tests/test_skill_script_integrity.py::test_preview_probe_capture_prefix_falls_back_to_probe_dir`。
- **关闭 H4**（compile_tokens 只读 world.md/discussion.md）：非缺陷。token *值*权威在 `world.md`（`compile_tokens.py` 自探测读取），`contract:tokens` 纪律块归 `spec_contract_blocks.py` 读共享区——两个权威对象本就不同，brief 无该块、"分裂"不发生；合并它们反而违反边界保持。
- **保持不动 benchmarks/baselines 冻结副本**：基线身份要求快照冻结，同步会破坏 benchmark 可比性，这是设计而非债务。
