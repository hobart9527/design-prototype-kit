"""Unit guards for the orthogonal 4-axis craft stack integration.

Covers: canonical IR emits `foundation.craft_stack` conforming to
`prototype-spec.v1.json`, and the tokens compiler surfaces the craft CSS
custom properties consumed by the builder contract.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compile_spec_ir import compile_canonical_ir, SCHEMA_PATH  # noqa: E402
from compile_tokens import compute_tokens, generate_css  # noqa: E402

pytestmark = pytest.mark.unit

COMPLETE_DISCUSSION = """# Design Discussion: Terminal Cluster Workbench

## 1. 业务与用户极端张力 (Core Tension)
- Operational through-put vs Catastrophic Bus-Hang Failures.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Operational Grounding: Slurm + Run:ai
- Kinetic Grounding: Vernier Caliper detents

## 3. 项目级状态模型 (State Model)
- `domain/cluster-nominal` (集群常态): 全部节点健康，张量流水线满负荷。
- `interaction/inspecting` (检视中): 抽屉展开、等待确认。
- `data/cold-metrics` (冷指标): 首次加载、缓存未命中。

## 4. 5-Dial 风格寄存器 (5-Dial Style Register)
- Energy: kinetic
- Density: dense

## 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/cluster-overview`

## 6. Viewport 与强制测试状态
- `Viewport`: `1280px`
- `Required States`: `state-draft`

## 7. 破坏协议 (Break Protocol)
- `stress/bus-hang` | Vector: `NVLink 链路挂起` | Expected: `显示降级徽标`。
"""


def _write_discussion(tmp_path: Path, text: str = COMPLETE_DISCUSSION) -> Path:
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True, exist_ok=True)
    disc.write_text(text, encoding="utf-8")
    return tmp_path


def test_canonical_ir_emits_craft_stack_conforming_to_schema(tmp_path: Path):
    """foundation.craft_stack is compiled and strictly schema-valid."""
    root = _write_discussion(tmp_path)
    ir = compile_canonical_ir(
        root=root,
        slice_id="cluster-overview",
        candidate_id="r1",
        stage="hero_probe",
    )

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=ir, schema=schema)

    stack = ir["foundation"]["craft_stack"]
    assert stack == {}


def test_parse_craft_stack_preserves_only_authored_axes():
    from compile_spec_ir import parse_craft_stack

    assert parse_craft_stack("Light weight instrumentation prose", {}) == {}
    assert parse_craft_stack("plain prose", {"energy": "restrained"}) == {}
    authored = parse_craft_stack(
        "- surface_optics: brushed_bronze\n- data_marks: segmented_bars\n", {}
    )
    assert authored == {
        "surface_optics": "brushed_bronze",
        "data_marks": "segmented_bars",
    }


def test_generate_css_leaves_undeclared_craft_neutral():
    css = generate_css(compute_tokens({}))
    assert "--surface-specular: none;" in css
    assert "--pattern-hatch-45: none;" in css
    assert "--font-display-tracking: 0;" in css
    assert "--font-display-weight: 500;" in css


def test_generate_css_emits_authored_craft_stack_tokens():
    css = generate_css(compute_tokens({}, craft_stack={
        "surface_optics": "coated_instrument_dark",
        "spatial_geometry": "soft_bento_pill",
        "micro_typography": "tight_display_polarized",
        "data_marks": "hatching_dither",
    }))
    assert "--surface-tint:" in css
    assert "--surface-specular: inset 0 1px 0 0 rgba(255, 255, 255, 0.15);" in css
    assert "--pattern-hatch-45: url(\"data:image/svg+xml" in css
    assert "--font-display-tracking: -0.04em;" in css
    assert "--font-display-weight: 800;" in css
