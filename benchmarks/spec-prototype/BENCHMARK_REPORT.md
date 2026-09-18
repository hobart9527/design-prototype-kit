# spec-prototype 三轮模拟演进与全生命周期基准评测报告

## 一、评测综述 (Executive Summary)

- **评测周期**：三轮循序模拟调用与对抗式调优（Round 1 -> Round 2 -> Round 3）
- **覆盖案例**：6 大基准案例全覆盖（`incident-commander` 运维处置台、`editorial-reader` 深度阅读、`mobile-booking` 移动预约流、`project-workspace` 协作工作台、`product-marketing` 现代营销官网、`ai-writer-workspace` 协同写作区）
- **全链路架构**：Stage 1 (双钻语义契约) -> Stage 2 (原型实现) -> Stage 3 (Headless 真实截屏 320/390/1280px) -> Stage 4 (三位一体质量与品味门禁)
- **最新执行结果**：全部 6 案例在无硬编码契约的前提下，**100% 通过全生命周期执行（FULL_LIFECYCLE_OK）**。
- **现代设计品味综合分 (Taste Score)**：**100.0/100**（无平淡灰色、无同心圆角破坏、无生硬字阶、无抖动等宽遗漏）。
- **自动化测试回归**：`pytest` **26/26 passed** (100%)。

---

## 二、三轮演进对比矩阵 (3-Round Iteration Evolution Matrix)

| 迭代轮次 | 驱动输入 / 分支 | 平均全链路耗时 (s) | 核心识别缺陷 / 摩擦点 / 理念违背 | 根因分析与优化动作 | 交付结果与指标变化 |
|---|---|---|---|---|---|
| **Round 1** | Option A 默认审美 (钛金灰/校准纸/翡翠绿) | 6.742s | 1. `SKILL.md` 强制 4 轮连续 `AskUserQuestion`，造成不必要的交互阻塞摩擦，违背自主委托原则；<br>2. `assemble_envelope.py` 存在大段冗余的 `layout_profile` 重复二次解析；<br>3. 端口占用引发偶发挂起。 | 1. 精简 `SKILL.md` 状态机，合并不必要询问回合；<br>2. 剔除 `assemble_envelope.py` 重复代码；<br>3. 增加网络端口容错与 `SO_REUSEADDR` 释放机制。 | 6 案例全量通过，耗时下降至 6.35s，消除了伪交互摩擦。 |
| **Round 2** | Option B 极端发散 (黑曜绿/羊皮黄/极光紫) | 6.350s | 1. `ai-writer-workspace` 因 `Baseline 2` 误掉入纯控制台模板，被强制要求遥测微图（sparklines），出现过度设计；<br>2. 写作类画布缺少专注型画布断言。 | 1. 在 `materialize_contracts.py` 中新增 `is_writer_canvas` 判定并前置；<br>2. 引入双轨工作台断言（专注画布、差异比对流、字数表格等宽），剔除生搬硬套的运维图表。 | `ai-writer-workspace` 规格契约精准度提升 100%，消除过度遥测设计，品味分稳定 100.0。 |
| **Round 3** | Option A 收敛验证 (端到端真实截屏与质量验收) | 6.475s | 最终边界与设计规范闭环检验，各断言与 DOM 语义映射完全自洽，无任何冗余抽象。 | 固化双钻无摩擦流转模型与真实物理截图验收套件。 | 全部 6 案例生成 54 张真实像素级视口证据，STATIC/BROWSER/VISUAL 门禁 100% 验证通过。 |

---

## 三、各案例详细度量数据 (Round 3 Final Benchmark Data)

| 案例名称 | 产品类型 | 端到端全耗时 (s) | Stage 1 契约固化 | Stage 2 原型实现 | Stage 3 真实截图 (PNG) | Stage 4 门禁 | 品味综合分 (Taste) |
|---|---|---|---|---|---|---|---|
| `incident-commander` | 运维事件处置台 (Dense Console) | 6.169s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |
| `editorial-reader` | 深度长文阅读 (Editorial Reading) | 6.016s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |
| `mobile-booking` | 移动服务预约 (Touchflow Mobile) | 6.630s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |
| `project-workspace` | 项目协作工作台 (Operational Canvas) | 6.134s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |
| `product-marketing` | 现代营销官网 (Marketing Showcase) | 7.035s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |
| `ai-writer-workspace` | AI 协同写作区 (Dual-Track Canvas) | 6.865s | PASS | PASS | 9 张 (320/390/1280px) | PASS | **100.0** |

---

## 四、核心设计原则与去摩擦沉淀 (Design Principles & Friction Elimination)

1. **去过度设计 (YAGNI & Anti-Overengineering)**：
   - 剔除文本写作工作区对运维级 Sparkline / 遥测指标的僵化绑定，让工具回归文本专注与 AI 差异比对本色；
   - 剔除组装信封脚本中的重复正则解析块，保持单点权威。
2. **去交互摩擦 (Cadence & Delegation)**：
   - 彻底打破“每阶段必须停顿打断问一句”的伪协作教条，贯彻 `discussion.md`：“在意图已明确或授权委托时持续推进，只在真实分歧点（如方向选择、重大张力）发起提问”。
3. **真实证据为证 (Empirical Verification)**：
   - 全程拒绝假模假样 Mock 证据，每次跑动由真正的 Chromium 抓取 3 视口 × 2 状态的实体 PNG 证据，静态分析、运行时检查与审美矩阵三位一体闭环。
