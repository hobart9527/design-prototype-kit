## Purpose

建立原型设计 Skill 的可信基准，使脚本机制、给定契约的实现能力与真实逐轮设计交付分别拥有独立证据，防止测试器补洞、评分泄漏及不等条件对比误导后续优化。

## ADDED Requirements

### Requirement: BENCH-001 Evidence-bounded mechanism results
基准 MUST 显式标注执行层级；机制检查 SHALL 仅声称实际执行的编译、组装与具体 Token 对比检查，不得声称完整 Skill、页面交互或整页 WCAG 合规。历史报告 MUST 保留来源并撤回无证据结论，不伪造重测结果。

#### Scenario: BENCH-SCN-001 Script success is not delivery success
- **WHEN** 三个机制脚本成功而未运行 Builder 或浏览器任务
- **THEN** 结果标为机制层成功且交付、交互和人工质量均为未测，不得产生完整 Skill 通过记录

#### Scenario: BENCH-SCN-002 Failure preserves context
- **WHEN** 任一机制步骤失败或输出格式无效
- **THEN** 保留步骤、退出码和错误上下文，结果不得通过，既有运行目录不得被覆盖删除

### Requirement: BENCH-002 Independent case inputs
六类案例 MUST 分离初始 brief、模拟用户事实与回应规则、反事实事件、独立验收。每个验收项 SHALL 指定自动行为检查或人工评价方法，不得要求通用固定配色、布局或装饰。

#### Scenario: BENCH-SCN-003 Six case coverage
- **WHEN** 检查六案例定义
- **THEN** 每案例均有可追溯的业务任务、至少一个改变需求或引入恢复路径的事件，以及独立验收方法

#### Scenario: BENCH-SCN-004 User responds without solving the test
- **WHEN** Skill 请求澄清
- **THEN** 模拟用户按当前问题与冻结事实回应，不读取隐藏验收、替 Skill 写契约或将尚未讨论的设计标为确认

### Requirement: BENCH-003 Authentic run admission
完整 Skill 实验 MUST 经真实入口与逐轮会话执行；运行证据 SHALL 记录实际版本、输入、确认来源、派发一致性及人工介入。真实入口或工具记录缺失 SHALL 返回明确阻断或证据不足，不得回退为手工脚本模拟。Skill 自身跳过流程 MUST 计为被测失败，而非从失败分母移除。

#### Scenario: BENCH-SCN-005 Tampered dispatch is detected
- **WHEN** 正式协议要求原样派发但文件与实际载荷不一致
- **THEN** 运行记录明确偏离来源，测试器修改归为实验污染，Skill 修改归为流程失败，不记为完整成功

#### Scenario: BENCH-SCN-006 Unsupported session execution blocks honestly
- **WHEN** 当前平台不能证明可启动隔离真实 Skill 会话并接收逐轮用户回应
- **THEN** 实验标为环境阻断并给出缺失能力，既不生成虚构会话也不将预制契约运行标为完整 Skill

### Requirement: BENCH-004 Independent evaluation and paired comparison
对照 MUST 分开统计执行真实性、任务行为、人工设计质量与成本；仅比较层级、案例版本和控制条件匹配的记录。全部尝试 SHALL 保留；未评分 SHALL 为待评审。任何修复 MUST 指向实际观察到的首次责任偏离，不得以个案偏好增加全局设计禁令。

#### Scenario: BENCH-SCN-007 Noncomparable runs are refused
- **WHEN** 比较脚本耗时与 Builder 耗时，或案例、模型及关键运行条件不一致
- **THEN** 输出不可直接比较及具体原因，不计算误导性的提升百分比

#### Scenario: BENCH-SCN-008 Pending review remains pending
- **WHEN** 只有静态通过和截图而无任务行为记录或人工评分
- **THEN** 对应维度保留未验证或待评审，不输出总体设计通过结论

#### Scenario: BENCH-SCN-009 Baseline precedes repair
- **WHEN** 开始真实试跑并准备优化 Skill
- **THEN** 先保留不可变旧版和所有运行证据；仅在真实失败被归因后提出明确修复和配对复测，无法执行时报告阻断而非声称已优化
