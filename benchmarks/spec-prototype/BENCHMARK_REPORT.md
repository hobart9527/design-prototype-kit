# spec-prototype 基准度量与首期基线报告

## 执行概览
- **运行时间**：2026-09-18
- **覆盖案例**：6 大产品类型（运维处置台、项目协作、长文阅读、移动预约、产品营销、AI 写作工作区）
- **测试轮数**：每案例 3 轮独立执行（共 18 轮次）
- **核心结论**：**18/18 轮次全部通过（100% 通过率）**，单案例契约组装平均耗时 ~0.137s，WCAG AAA 浅色/深色对比度 100% 达标。

---

## 详细度量数据（Latency & Verification Matrix）

| 案例名称 | 产品类型 | 3 轮耗时 (s) | 契约固化 | 封套生成 | Token 编译 | WCAG AAA 对比度 | 综合状态 |
|---|---|---|---|---|---|---|---|
| `incident-commander` | 运维事件处置台 | 0.153 / 0.144 / 0.134 | PASS | PASS | PASS | PASS (17.5:1) | **PASS** |
| `project-workspace` | 项目协作工作台 | 0.135 / 0.134 / 0.140 | PASS | PASS | PASS | PASS (17.5:1) | **PASS** |
| `editorial-reader` | 深度长文阅读 | 0.153 / 0.137 / 0.134 | PASS | PASS | PASS | PASS (>15:1) | **PASS** |
| `mobile-booking` | 移动服务预约流 | 0.133 / 0.133 / 0.135 | PASS | PASS | PASS | PASS (>15:1) | **PASS** |
| `product-marketing` | 现代营销官网 | 0.133 / 0.133 / 0.136 | PASS | PASS | PASS | PASS (>15:1) | **PASS** |
| `ai-writer-workspace` | AI 协同工作区 | 0.138 / 0.139 / 0.141 | PASS | PASS | PASS | PASS (>15:1) | **PASS** |

---

## 机制加固核验要点
1. **真实性拦截机制**：
   - 空 `pointerdown`、裸数字 `<span class="stat">42</span>`、注释伪状态 `<!-- loading -->` 均在回归测试中实现 100% 精准拦截。
2. **多属性 Token 双向回流**：
   - 支持在 Stage 4 人工微调 `tokens.css`（含颜色、圆角、间距），并通过 `--reconcile-from-css` 100% 保真回流至 `t1.json` 及 `discussion.md`。
3. **基线抗干扰性**：
   - 在需求或舍弃项出现 `mobile` / `touch` 时，桌面控制台依然保持 `dense-console`，绝对杜绝被正则关键词劫持。
