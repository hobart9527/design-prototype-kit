# Change: 2026-09-29-spec-prototype-workflow-flip

## Why

16 轮复盘表明，spec-prototype 的主要阻塞与资源消耗在于过重的开工前形式化（intent.json、compile_spec_ir、Sealed Provisional、物理锚点推导）以及脆弱的纯文本/AST 软性审计机制。这剥夺了模型探索现代设计风格与视觉创新的空间与算力。
本变更旨在翻转工作流：以人为审美终裁，以原型为探索媒介，以 Spec 为交付契约，以脚本提供客观事实。写原型前无需强制 Spec，Spec 只在工程交付时由定稿反向提取生成；软性/审美校验退出拦截主链，客观硬性检查统一收敛至捕获链路中。

## What Changes

1. **核心原则与阶段生命周期翻转 (Workflow Inversion)**：
   - 更新 `CONTEXT.md`、`SKILL.md`、`core-kernel.md`、`artifact-lifecycle.md`。
   - 更新 Stage 0/1/2/3/5 文档：移除“无 Spec 不写原型代码”的前置硬性要求；将 Spec 编译与冻结限制在 Stage 5 Handoff。
   - 同步修正锁定“先 Spec 后原型”历史措辞的单元测试断言。

2. **现代设计风格语汇与探索扩展 (Modern Style Vocabulary & Exploration)**：
   - 新增 `references/02-craft-methods/modern-style-vocabulary.md`，提供现代设计风格（高密仪表、瑞士网格、温和触感、Bento 等）的场景反向推导器与手法说明。
   - 允许第一轮多方向探索槽位 (`dirs/{a,b,c}`)，避免单文件覆盖冲突。
   - 更新 `templates/discussion.md`，沉淀项目品味档案。

3. **客观硬检查收敛与质检减负 (Unified Hard Preflight & Verification Simplification)**：
   - 明确硬检查判据，收窄保留三项工艺硬缺陷（`:active`、同心圆角、`tabular-nums`）与运行时基础事实（JS 错误、样式生效、WCAG 对比度、横向溢出）。
   - 将原型客观硬检查收敛于 `capture.mjs` 中，提供无头浏览器不可用时的静默降级策略。
   - 清理/退役主调用链中过度的审查脚本（`verify_prototype_quality.py` 等）及对应的纯文本测试，Builder/Critic 移除硬性工具调用上限与单次写完约束。

4. **单向 Handoff 导出与 Token 所有权下放 (Token Authority & Downstream Handoff)**：
   - 原型探索期允许直接手写 `tokens.css`；交接期支持从 CSS 反向导出 `t1.json`。
   - 修复 Stage 5 中 `wcag-check.js` 针对空颜色集的静默假通过缺陷。

## Non-Goals

- 不削弱三项工艺硬缺陷的硬性标准（仅收窄其适用范围到对应组件）。
- 不破坏现有 DTCG token 规范兼容性。
- 不引入重型外部构建打包工具（保持原生 zero-build HTML/CSS/JS 交付）。

## Impact

- 消除原型生成前繁重的形式化阻断，降低首屏产出时间和 Token 消耗。
- 增强原型探索阶段的现代视觉多样性与设计水准。
- 保证工程交接时的 Spec 与 Token 依然具备完备的类型、契约与散列冻结保证。
