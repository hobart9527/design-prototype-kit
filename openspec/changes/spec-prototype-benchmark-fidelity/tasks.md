## 1. 基线校正与证据分层

- [ ] T-01 修正 benchmarks/run_benchmark.py 输出层标签与失败上下文保留
  - Anchors: benchmarks/run_benchmark.py
  - Write scope: benchmarks/run_benchmark.py
  - 将 `verification_passed` 字段重命名为 `pipeline_exit_ok`；在结果写入时新增 `layer: "mechanism"` 字段；将 `wcag_aaa_contrast` 度量说明注释为"仅检查 `color.surface` 与 `color.text-primary` 键对，不代表整页 WCAG 合规"；移除失败或重跑时对既有运行目录的静默 `rmtree`，改以时间戳运行目录隔离保留上下文。
  - Depends on: none
  - Implements: BENCH-001
  - Proves: BENCH-SCN-001, BENCH-SCN-002
  - Verify with: python3 -c "import pathlib; src=pathlib.Path('benchmarks/run_benchmark.py').read_text(); assert 'pipeline_exit_ok' in src; assert 'layer' in src; assert 'verification_passed' not in src; assert 'shutil.rmtree(work_dir)' not in src"

- [ ] T-02 新增 run_meta 字段记录控制条件
  - Anchors: benchmarks/run_benchmark.py
  - Write scope: benchmarks/run_benchmark.py
  - 在每轮结果 dict 增加 `run_meta`，包含 `layer`、`script_versions`（materialize/compile/assemble 的文件修改时间）、`conditions`（`human_intervened: false`、`env_blocked: false`）。
  - Depends on: T-01
  - Implements: BENCH-004
  - Proves: BENCH-SCN-007
  - Verify with: python3 -c "import pathlib; src=pathlib.Path('benchmarks/run_benchmark.py').read_text(); assert 'run_meta' in src; assert 'human_intervened' in src; assert 'script_versions' in src"

- [ ] T-03 撤回 BENCHMARK_REPORT.md 越界声明并记录分层事实与证据边界
  - Anchors: benchmarks/spec-prototype/BENCHMARK_REPORT.md
  - Write scope: benchmarks/spec-prototype/BENCHMARK_REPORT.md
  - 在报告头部新增 `## 证据边界（重要）` 段落：18/18 为机制层脚本成功次数；无 Builder 调用；无浏览器任务操作验证；WCAG 数字为单键对检查；"18/18 全部通过"改为"18/18 机制层通过，Builder/交互/设计质量均未测"。新增 `## 截图证据边界` 说明：browser capture 仅记录 `browser: verified`；`visual`、`human` 保持 `unverified` 直至人工评审完成；不得用截图张数声明设计质量通过。
  - Depends on: T-01
  - Implements: BENCH-001, BENCH-004
  - Proves: BENCH-SCN-008
  - Verify with: python3 -c "import pathlib; t=pathlib.Path('benchmarks/spec-prototype/BENCHMARK_REPORT.md').read_text(); assert '证据边界' in t; assert 'Builder' in t; assert '未测' in t; assert '截图证据边界' in t"

## 2. 六案例独立验收结构

- [ ] T-04 为六案例新增 user-rules.md 和 events.md
  - Anchors: benchmarks/spec-prototype/cases/
  - Write scope: benchmarks/spec-prototype/cases/
  - 为每个案例创建 `user-rules.md`（模拟用户持有的事实、偏好、禁区，不向被测会话暴露，头部含 `<!-- NOT FOR SKILL SESSION -->` 标记）和 `events.md`（反事实触发事件，含 `trigger_condition:` 键注明触发轮次）。内容须与现有 `brief.md` 和 `acceptance.md` 语义一致，不引入新产品约束。
  - Depends on: none
  - Implements: BENCH-002
  - Proves: BENCH-SCN-003, BENCH-SCN-004
  - Verify with: python3 -c "import pathlib; cases=['incident-commander','project-workspace','editorial-reader','mobile-booking','product-marketing','ai-writer-workspace']; [pathlib.Path(f'benchmarks/spec-prototype/cases/{c}/user-rules.md').read_text() and pathlib.Path(f'benchmarks/spec-prototype/cases/{c}/events.md').read_text() for c in cases]; print('OK')"

- [ ] T-05 升级 acceptance.md 为结构化两段式
  - Anchors: benchmarks/spec-prototype/cases/
  - Write scope: benchmarks/spec-prototype/cases/
  - 在每个 acceptance.md 顶部新增结构化验收段（`automated` 项含方法字符串，`human` 项含评价维度名称），保留原有自由文本作为 `legacy` 子段。结构化项描述行为可观测性，不预设固定配色或布局值。
  - Depends on: T-04
  - Implements: BENCH-002
  - Verify with: python3 -c "import pathlib; cases=['incident-commander','project-workspace','editorial-reader','mobile-booking','product-marketing','ai-writer-workspace']; [None if 'automated' in pathlib.Path(f'benchmarks/spec-prototype/cases/{c}/acceptance.md').read_text() else (_ for _ in ()).throw(AssertionError(c)) for c in cases]; print('OK')"

## 3. 环境阻断协议

- [ ] T-06 新增 benchmarks/probe_skill_session.py 阻断检测
  - Anchors: benchmarks/
  - Write scope: benchmarks/probe_skill_session.py
  - 新建脚本，检测当前平台是否具备 Layer 3 所需能力（隔离 Skill 会话可启动、工具调用记录可读取）。能力缺失时退出码 2 并输出 `ENVIRONMENT_BLOCKED` 及缺失能力列表；能力具备时输出 `ENVIRONMENT_READY`。脚本本身不创建 Skill 会话，只检测前提条件。
  - Depends on: none
  - Implements: BENCH-003
  - Proves: BENCH-SCN-005
  - Verify with: python3 benchmarks/probe_skill_session.py 2>&1 | grep -E 'ENVIRONMENT_BLOCKED|ENVIRONMENT_READY'

- [ ] T-07 在 run_benchmark.py 集成阻断记录
  - Anchors: benchmarks/run_benchmark.py
  - Write scope: benchmarks/run_benchmark.py
  - 在 `run_all_benchmarks` 输出中增加 L2/L3 阻断声明：若 probe 返回 `ENVIRONMENT_BLOCKED`，则 summary 中 `l2_builder_runs` 和 `l3_skill_runs` 字段标为 `"blocked"`，禁止以脚本替代。
  - Depends on: T-02, T-06
  - Implements: BENCH-003
  - Proves: BENCH-SCN-006
  - Verify with: python3 -c "import pathlib; src=pathlib.Path('benchmarks/run_benchmark.py').read_text(); assert 'l2_builder_runs' in src; assert 'l3_skill_runs' in src"

## 4. 旧版基线对照验证与归因

- [ ] T-08 runner 新增 --label 参数并生成带标签摘要
  - Anchors: benchmarks/run_benchmark.py
  - Write scope: benchmarks/run_benchmark.py, benchmarks/spec-prototype/results/
  - 新增 `--label` CLI 参数注释本次运行版本；summary.json 新增 `run_label` 字段。运行一轮 L1 生成带标签记录，写入 `benchmarks/spec-prototype/results/`。
  - Depends on: T-01, T-02, T-03
  - Implements: BENCH-004
  - Proves: BENCH-SCN-009
  - Verify with: python3 -c "import json,pathlib,glob; files=sorted(glob.glob('benchmarks/spec-prototype/results/*/summary.json')); assert any(json.loads(pathlib.Path(f).read_text()).get('run_label') == 'baseline-check' for f in files); print('OK')"

- [ ] T-09 记录真实测试快照与缺陷责任归因矩阵
  - Anchors: tests/test_pipeline.py, benchmarks/spec-prototype/BENCHMARK_REPORT.md
  - Write scope: benchmarks/spec-prototype/BENCHMARK_REPORT.md
  - 运行 `python3 -m pytest tests/test_pipeline.py -q` 并将实际输出（通过数/失败数）追加写入 `benchmarks/spec-prototype/BENCHMARK_REPORT.md` 的"旧版基线测试快照"段落；同时根据本轮探查已确认的 8 项事实与测试结果，生成"首期缺陷责任归因矩阵"，明确标定各层偏离位置（测试器输入改写、缺少真实 Builder 派发、虚报通过率、硬编码断言等）。
  - Depends on: T-08
  - Implements: BENCH-004
  - Verify with: python3 -c "import pathlib; t=pathlib.Path('benchmarks/spec-prototype/BENCHMARK_REPORT.md').read_text(); assert '旧版基线测试快照' in t; assert '缺陷责任归因矩阵' in t"
