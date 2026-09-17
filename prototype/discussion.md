# Design Discussion: Diffusion GPU Cluster Orchestration Desk

## Resume

- Execution boundary: released
- Product archetype basis: greenfield
- Baseline: Baseline 1: Dense Data & Engineering Workbench (Grounding: Slurm + Run:ai + NVIDIA DCGM Telemetry)
- Active track / current decision: stage-2-anchor / building
- Route basis: IA-first
- Requested scope and stopping point: Stage 2 Core Hero Anchor
- Pending prerequisite: none
- Next action and its prerequisite: verify Hero Anchor with strict-divergence assertion harness

## Stage 1: Grounded Tone & Tension Divergence (破 - 魂)

- **Business Tension**:
  - 4,096 卡 H100 集群超大规模扩散模型生图训练与实时并行渲染，面对峰值张量显存溢出（OOM Spike）、CUDA Bus Hang 与流水线气泡，SRE 必须在 2 秒内识别卡死节点并执行确定性显存抢占与冷热分流。
- **Reality Anchors**:
  - `NVIDIA DCGM Telemetry` (显存带宽占用、SM 利用率、张量核心温度、NVLink 拓扑流)。
  - `Slurm & Run:ai Workbench` (作业分批队列、节点亲和性配额、故障抢占旁路)。
- **5-Dial Style Register**:
  - `Energy`: `quiet` (深渊哑光黑 `#05070a`，等离子青高亮，杜绝一切无意义光效)。
  - `Finish`: `machined-industrial` (1px 锐利层阶边框、等宽数值防抖 `tabular-nums`、微秒级显存刷新标尺)。
  - `Density`: `dense` (多机多卡拓扑网、节点排队深度、显存热图在单屏压缩高信噪比呈现)。
  - `Weight`: `dense-tactile` (`:active scale(0.98)` 机械触感微动)。
  - `Seriousness`: `solemn` (超算关键基础设施，全集群实体 100% 可查可控)。
- **Surface Topology**:
  1. **Primary Workspace**: `experiments/console/hero-anchor/index.html` (Diffusion GPU 集群拓扑调度总控台 + 显存抢占检视抽屉)。
  2. **Contextual Views**: `surfaces/incident-replay/index.html` (CUDA Bus Hang 故障断点与帧显存回放工作台)。
  3. **Supporting Views**: `surfaces/capacity-matrix/index.html` (GPU 算力矩阵与调度分流策略控制面)。
