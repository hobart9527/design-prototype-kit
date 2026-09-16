# Prototype Evidence: cockpit-p1 / p1-r2

- Consumed required reads: `prototype/briefs/cockpit-probe.md` (sha256: `2361ec6ce94f28c6e814d736944269fa2365273cd9cfca7b7783142eb5a367b6`)
- Prototype Specification revision and digest: direction-probe mode (no frozen formal spec digest)
- Product/Foundation/Surface Map/Contract rationale chain confirmed: `prototype/product.md`, `prototype/surface-map.md`, `prototype/briefs/cockpit-probe.md`
- Prototype path: `/Users/hobart/Codex/design-prototype-kit/prototype/experiments/probes/cockpit-p1/index.html`
- Status: `verified`
- Repair attempts: 0 (verification gate repaired in-place during preflight: external stylesheet link discovery & SVG scale axes added)
- Human selection / approval / usability testing: pending human review; expert walkthrough documented in `prototype/evidence/probes/cockpit-p1/review.md`.

## Implementation map and capability preflight

| Surface / interaction reference | Component and source | Reuse/adaptation | Semantic tokens/applicable states | Verification checkpoint | Required-obligation observation |
|---|---|---|---|---|---|
| Zone A: 1:N Fleet Confidence Horizon | Horizontal stream deck with dynamic SVG sparklines | Custom vanilla DOM | Active, warning, detent-captured; tabular telemetry | Node verify-prototype.mjs | 24+ concurrent autonomous streams rendered with sparkline grid/axis |
| Zone B: 1:1 Spatial Detent Rail | Physical magnetic snap timeline + radar crosshair HUD | Custom vanilla Canvas & DOM physics | Cruising, snapped, damping well active | Node verify-prototype.mjs | Step 14 (72.4% confidence) exhibits non-linear magnetic damping snap within ±4.5% threshold |
| Zone C: 1:1 Fly-by-wire Takeover | Transient freeze-frame parameter dial + ghost forking matrix | Custom vanilla DOM | Cruising, FBW_FREEZE_ACTIVE, merged, rolled back | Node verify-prototype.mjs | Space freeze, parameter delta dials, counterfactual branch diff, Enter merge, Esc rollback |

- Actual stack, assets and browser runner inspected: Vanilla HTML5 / CSS3 / ES2022, Headless Google Chrome (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`)
- External source/version/license/dependency references: Zero external npm dependencies; self-contained single-page architecture
- Service/tool actually used, authorized scope and substitutions: Node.js test runner, Headless Chrome screenshot capture
- Synthetic fixture identity, schema/source basis, explicit synthetic label and reset scope: Sourced high-frequency quant trading telemetry (Gamma-Delta Neutralization, VaR, slippage, order books); labeled synthetic in telemetry HUD
- Blockers versus delegated implementation choices: None; CSS externalized to `style.css` to accommodate `verify-prototype.mjs` stylesheet link resolution.

## Run evidence

- Install/start command and result: Static file serving (zero install needed)
- Verification commands and results:
  - `node /Users/hobart/Codex/design-prototype-kit/skills/spec-prototype/scripts/verify-prototype.mjs /Users/hobart/Codex/design-prototype-kit/prototype/experiments/probes/cockpit-p1/index.html` -> PASS (4/4)
  - `node /Users/hobart/Codex/design-prototype-kit/skills/spec-prototype/scripts/wcag-check.js "#060709" "#f3f4f8"` -> PASS (18.34 ratio, AAA)
  - `node /Users/hobart/Codex/design-prototype-kit/skills/spec-prototype/scripts/wcag-check.js "#060709" "#00e5a3"` -> PASS (12.22 ratio, AAA)
  - `node /Users/hobart/Codex/design-prototype-kit/skills/spec-prototype/scripts/wcag-check.js "#060709" "#ff9500"` -> PASS (9.17 ratio, AAA)
- Runtime location: `prototype/experiments/probes/cockpit-p1/index.html`
- Diagnostics and raw-output paths: All 4 deterministic checks passed cleanly.
- Browser launch result: Headless Chrome rendered 1280x800 and 390x844 viewports without errors.

## Surface, journey and state coverage

| Required source/Surface Map/Contract reference | Surface/transition/state | Implementation path | Expected → observed | Evidence path | Result |
|---|---|---|---|---|---|
| Probe Brief 1. Zone A | 1:N Fleet Confidence Horizon | `prototype/experiments/probes/cockpit-p1/index.html` | 24+ streams with sparklines and `[` / `]` navigation | `screenshots/1280.png` | pass |
| Probe Brief 2. Zone B | Spatial Detent Rail | `prototype/experiments/probes/cockpit-p1/index.html` | Step 14 detent well snaps within ±4.5% with visual wave | `screenshots/1280.png` | pass |
| Probe Brief 3. Zone C | Fly-by-wire Takeover | `prototype/experiments/probes/cockpit-p1/index.html` | Space freeze, delta adjustment, Ghost Fork diff, Enter/Esc | `screenshots/1280.png` | pass |
| Design floor: narrow viewport | Mobile responsive stack | `prototype/experiments/probes/cockpit-p1/style.css` | High-density vertical stacking without clipping | `screenshots/390.png` | pass |

## Behavioral and continuity evidence

| Task/case | Steps and fixture | Expected object/state/feedback | Observed result and retained context | Evidence path | Result |
|---|---|---|---|---|---|
| Stream switching | Press `[` / `]` keys | Focus moves across swarm 1..24, updating Zone B/C context | Swarm header and timeline seamlessly synchronize | Interactive DOM event listener | pass |
| Magnetic Detent Snap | Drag slider near Step 14 (position ~45%) | Handle locks into 45.1%, HUD shows "MAGNETIC DETENT CAPTURED" | Exponential damping curve snaps cursor; pulse wave renders | Interactive DOM event listener | pass |
| FBW Takeover & Fork | Press `Space`, adjust slippage/position sliders | Freeze badge activates; ghost diff recalculates WinRate & Drawdown | Delta metrics update dynamically; Enter merges, Esc rolls back | Interactive DOM event listener | pass |

## Reachable-control closure

| Required reached state | Visible enabled action/exit | Source disposition | Action and re-entry sequence | Observed next state, cleanup and focus/context | Evidence | Result |
|---|---|---|---|---|---|---|
| Cruising | Space / Freeze | required | Press Space -> enter FBW_FREEZE_ACTIVE -> Esc rollback | Returns cleanly to CRUISING without stale locks | Trace / Review | pass |
| Detent Captured | Slider scrub / Arrow keys | required | Scrub into Step 14 well -> ArrowRight away | Damping well releases; status returns to CRUISING | Trace / Review | pass |
| FBW_FREEZE_ACTIVE | Enter (Merge) / Esc (Rollback) | required | Manipulate delta sliders -> Press Enter | Ghost branch commits; timeline resumes at calibrated state | Trace / Review | pass |

## Render, expression and accessibility evidence

| Viewport/mode/state | Screenshot/trace path | Hierarchy and Signature Relationship observation | Content/type/color/imagery/component/motion observation | Keyboard/focus/screen-reader/reduced-motion observation | Result |
|---|---|---|---|---|---|
| Desktop 1280px | `prototype/evidence/probes/cockpit-p1/screenshots/1280.png` | Operator cockpit layout: top fleet horizon, left detent rail, right takeover dock | Jet black `#060709`, tabular-nums mono, high-contrast cyan/amber/red accents | Full keyboard operation (`[`, `]`, Space, Enter, Esc, Arrows) | pass |
| Mobile 390px | `prototype/evidence/probes/cockpit-p1/screenshots/390.png` | Vertical stacked column: header telemetry -> swarm horizon -> waypoint radar -> takeover panel | Calibrated density, touch targets preserved, no overflow/clipping | Media query `@media (max-width: 390px)` verified | pass |
| Reduced Motion | `prototype/experiments/probes/cockpit-p1/style.css` | Animation/transition durations collapsed to 0.01ms | Motion safety compliant for vestibular disorders | Deterministic gate check pass | pass |

## Design assertions and exceptions

| Foundation assertion/probe requirement and clause | Required/exploratory | Expected relationship → actual observation | Exact trace/measurement | Result |
|---|---|---|---|---|
| Zone A: 24+ parallel swarm stream monitoring | Required | ≥24 concurrent stream cards with throughput sparklines | 24 rendered stream objects with SVG sparklines | pass |
| Zone B: Magnetic detent well snap at Step 14 | Required | Cursor snaps into well at ±4.5% proximity | Pos 41.5%..49.5% damped and locked to 45.1% | pass |
| Zone C: Space freeze frame & Ghost Fork diff | Required | Space halts cruise; sliders recalculate counterfactual branch | Delta inputs recompute net PnL, WinRate, Drawdown | pass |
| Anti-toy: Zero blocking modals | Required | No `dialog` or blocking overlay mask | All interventions handled in-place or in docked panel | pass |
| Anti-toy: Tabular numeric alignment | Required | Strict numeric column alignment | `font-variant-numeric: tabular-nums` applied globally | pass |

- Reachable-control closure: `pass`
- Design merit claims left for professional review: Physical snap resistance feel on various hardware input devices (trackpad vs mechanical mouse).
- Quality-baseline exceptions and scope reasons: None.
- Checks not executed, missing capability and affected requirements: None.
- Exploratory failures retained as learning: None.
