# Design Discussion: Diffusion GPU Cluster Orchestration Desk

## Resume

- Execution boundary: released
- Product archetype basis: Archetype A: Greenfield 0-to-1 (全新超算集群调度平台)
- Baseline: Baseline 1: Dense Workbench (Grounding: Slurm + Run:ai + NVIDIA DCGM Telemetry)
- Active track / current decision: stage-1-divergence / completed
- Route basis: IA-first
- Requested scope and stopping point: Full 5-Stage Canonical Pipeline
- Pending prerequisite: none
- Next action and its prerequisite: Materialize 6-Pillar Spec Contracts via materialize_contracts.py

## Stage 1: Grounded Tone & Tension Divergence (破 - 魂)

### 1. 业务与用户极端张力 (Core Tension)
- **业务后果**: 4,096 卡 H100 SXM5 超大规模集群实时进行 Diffusion 并行反向传播与 KV-Cache 渲染。一旦单机 NVLink 发生 Bus Hang 或显存 OOM 浪涌，每秒产生超算排队损耗。
- **操作者冲突**: SRE 操作员必须在 **2 秒内** 从 4,096 块 GPU 中秒级定位故障节点并执行确定的**显存抢占/节点排空**；但误排空健康作业将导致整批训练权重回滚。

### 2. 现实双地锚 (Reality Benchmark Anchors)
- **业务地锚 (Operational Anchor)**: `NVIDIA DCGM Telemetry & Run:ai Console`（高频张量显存热图、NVLink 吞吐拓扑、多租户配额排队）。
- **物理地锚 (Kinetic / Physical Anchor)**: `Aircraft Fly-by-wire Detent & Machined Vernier Caliper`（电传操纵磁吸阻尼位移、卡尺游标微动、绝无虚饰）。

### 3. 三大冷酷舍弃 (Ruthless Omissions)
1. **舍弃消费级发光拟态卡片**: 杜绝多重弥散阴影和无意义彩色图表，全屏采用 1px 细线发丝级边界与深渊哑光黑背景。
2. **舍弃裸指标数据展示 (Zero Naked Metrics)**: 所有 VRAM 容量与利用率数值强制附带 60 秒内联微时序走势图（Micro Sparklines）与集群基准分位线。
3. **舍弃多步繁复确认模态**: 核心排空动作遵循动作动词四态闭环，支持 `Space` 键瞬时检视、`Enter` 键机械压感提交。

### 4. 5-Dial 风格寄存器 (5-Dial Style Register)
- `Energy`: `quiet` (深渊哑光黑 `#05070a`，等离子青高亮，杜绝一切光污染)。
- `Finish`: `machined-industrial` (1px 锐利边框、`tabular-nums` 等宽防抖数值)。
- `Density`: `dense` (4,096 节点单屏高信噪比点阵矩阵)。
- `Weight`: `dense-tactile` (`:active scale(0.97)` 机械微动压感)。
- `Seriousness`: `solemn` (超算严谨工业仪器，零娱乐花哨动效)。
- `Palette`: `plasma-cyan`

### 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/hero-anchor`（4,096 GPU 拓扑阵列总览 + 显存抢占检视抽屉）。
- **上下文视图 (Contextual)**: `surfaces/incident-replay`（CUDA Bus Hang 故障微秒级帧回放）。
- **支撑视图 (Supporting)**: `surfaces/capacity-matrix`（算力配额矩阵与跨节点分流配置）。
