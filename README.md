# Design Prototype Kit

工业级体验设计系统与交互原型套件（Design & Prototype Engine）。

## 核心定位

解耦基础设施配置，专注于高质感 UI/UE/UX/UR 全链路设计决策与动态原型交付。

## 四大工业级场景基线 (Design System Baselines)

1. **Dense Workbench (高密数据工作台)**: `4px` 基准网格，Tabular Mono 字符对齐，紧凑边距与高信息密度。
2. **Immersive Web (流体 SaaS / 商业 Web)**: `8px` 网格系统，丰富排版阶梯与渐进式层级。
3. **Editorial Reading (阅读沉浸 / 文档编辑)**: 固定字符宽度（`68ch`），舒缓行高（1.65），零杂讯干扰。
4. **Touch-First Mobile (纯 C 端触控沉浸)**: 移动端拇指热区，`44x44px` 最小触控目标，自然弹簧阻尼曲线（`cubic-bezier(0.16, 1, 0.3, 1)`），弹性吸附与拉取刷新交互。

## 交互与状态能力

- **五大关键体验状态 (Experience States)**: Loading (骨架屏), Empty (引导 CTA), Partial (降级/弱网), Error (局部容错与重试), Overflow (极端字符与分页)。
- **物理世界微交互 (Kinetics)**: 弹性按压反馈（`:active { transform: scale(0.97); }`）、减速阻尼与持久化暂态。
- **A/B 架构权衡决策 (Trade-off Thinking)**: 显式推演 Option A (极致效率) vs Option B (渐进引导) 的取舍成本。
- **真实 UR 验收底线**: 严禁伪造用户访谈与合成虚假评分，坚持启发式走查与任务漏斗证伪。

## 目录结构

```text
design-prototype-kit/
├── agents/                  # 专属设计 Builder 与独立 Critic 契约
├── skills/spec-prototype/   # 核心设计规约、交互模板与导出工具
│   ├── references/          # 权威设计语言、组件规范与验收标准
│   ├── templates/           # W3C DTCG Token 模版与产物定义
│   └── scripts/             # Token 转换器与验证工具
└── tests/                   # 独立测试与设计规范校验
```

## 测试与校验

```bash
python3 -m pytest tests/ -q
```
