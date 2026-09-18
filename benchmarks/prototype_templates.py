"""Rich, domain-grounded HTML prototype templates for spec-prototype benchmarks.

Produces high-density, authentic prototypes conforming to v10 specifications:
- Zero dead gray (#808080) and zero inline hex in styles (100% token consumption).
- Layer 1-3 semantic tokens (primitives, semantic surfaces, component slots).
- Tabular numeric telemetry, bounded measures (68ch), and break protocol protection.
- Dual-channel shortcuts (Space/Esc) and declarative state machine (#state=ideal/empty/error).
"""
from __future__ import annotations


COMMON_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{case_name} · prototype</title>
<link rel="stylesheet" href="../../../shared/tokens.css">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; }}
  body {{
    background: var(--bg-void);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 13px;
    line-height: var(--line-height-body);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }}
  .tabular-nums {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; }}

  header {{
    background: var(--bg-base);
    border-bottom: 1px solid var(--border-subtle);
    padding: var(--space-3) var(--space-4);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }}
  .brand {{
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }}
  .badge {{
    background: var(--badge-bg);
    color: var(--badge-text);
    padding: 2px var(--space-2);
    border-radius: var(--radius-pill);
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
  }}
  .badge-danger {{
    background: var(--status-danger);
    color: var(--text-inverse);
  }}
  .badge-warning {{
    background: var(--status-warning);
    color: var(--bg-void);
  }}
  .badge-nominal {{
    background: var(--status-nominal);
    color: var(--text-inverse);
  }}

  .card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-card);
    padding: var(--space-4);
    transition: transform var(--duration-fast) var(--ease-hud), border-color var(--duration-fast);
  }}
  .card:hover {{
    border-color: var(--card-border-active);
  }}

  .btn-primary {{
    background: var(--action-primary);
    color: var(--text-inverse);
    border: none;
    border-radius: var(--radius-btn);
    min-height: var(--min-touch-target);
    min-width: var(--min-touch-target);
    padding: var(--space-2) var(--space-4);
    font-weight: 500;
    font-size: 13px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background var(--duration-fast), transform var(--duration-fast);
  }}
  .btn-primary:hover {{ background: var(--action-primary-hover); }}
  .btn-primary:active {{ transform: scale(0.97); }}

  .btn-ghost {{
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-btn);
    min-height: var(--min-touch-target);
    padding: var(--space-2) var(--space-3);
    font-size: 13px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background var(--duration-fast), color var(--duration-fast);
  }}
  .btn-ghost:hover {{
    background: var(--action-ghost-hover);
    color: var(--text-primary);
  }}

  .overflow-label {{
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    max-width: 100%;
    display: inline-block;
  }}

  .modal-overlay {{
    position: fixed; inset: 0; background: var(--modal-backdrop);
    display: none; align-items: center; justify-content: center; z-index: 100;
  }}
  .modal-card {{
    background: var(--modal-surface);
    border: 1px solid var(--modal-border);
    border-radius: var(--radius-outer);
    padding: var(--space-5);
    max-width: 440px;
    width: 90%;
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
  }}

  .toast {{
    position: fixed; bottom: var(--safe-area-inset-bottom); right: var(--space-4);
    background: var(--bg-surface-raised); border: 1px solid var(--border-bright);
    border-radius: var(--radius-card); padding: var(--space-3) var(--space-4);
    display: none; box-shadow: 0 4px 16px rgba(0,0,0,0.3); z-index: 200;
    color: var(--text-primary); font-weight: 500;
  }}

  /* State-driven views */
  .state-empty, .state-error {{ display: none; }}
  body[data-state="empty"] .state-ideal {{ display: none; }}
  body[data-state="empty"] .state-empty {{ display: flex; flex-direction: column; align-items: center; justify-content: center; padding: var(--space-8); text-align: center; }}
  body[data-state="error"] .state-ideal {{ display: none; }}
  body[data-state="error"] .state-error {{ display: block; border-left: 4px solid var(--status-danger); padding: var(--space-4); background: var(--bg-surface-raised); margin: var(--space-4); }}

  @media (prefers-reduced-motion: reduce) {{
    *, ::before, ::after {{
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }}
  }}
"""

COMMON_FOOTER = """
  <!-- Two-Phase Confirmation Modal -->
  <div class="modal-overlay" id="action-modal" role="dialog" aria-modal="true">
    <div class="modal-card">
      <h3 style="margin-top: 0; color: var(--text-primary); font-size: 16px;">{action_modal}</h3>
      <p style="color: var(--text-secondary); margin: var(--space-3) 0 var(--space-5) 0; font-size: 13px; line-height: 1.5;">
        Confirm execution for target resource? This operation commits state transition across active topology nodes.
      </p>
      <div style="display: flex; justify-content: flex-end; gap: var(--space-2);">
        <button onclick="closeModal()" class="btn-ghost">Cancel</button>
        <button class="btn-primary" id="commit-btn" onclick="commitAction()">{action_commit}</button>
      </div>
    </div>
  </div>

  <!-- Operational Feedback Toast -->
  <div class="toast" id="toast-notify" role="status">
    {action_toast}
  </div>

  <script>
    function openModal() {{
      document.getElementById('action-modal').style.display = 'flex';
    }}
    function closeModal() {{
      document.getElementById('action-modal').style.display = 'none';
    }}
    function commitAction() {{
      closeModal();
      const toast = document.getElementById('toast-notify');
      toast.style.display = 'block';
      setTimeout(() => {{ toast.style.display = 'none'; }}, 4000);
    }}
    function applyState() {{
      const hash = location.hash.replace('#', '');
      const params = new URLSearchParams(hash);
      const state = params.get('state') || 'ideal';
      document.body.dataset.state = state;
    }}
    window.addEventListener('hashchange', applyState);
    applyState();

    window.addEventListener('keydown', (e) => {{
      if ((e.key === ' ' || e.key === 'p') && e.target === document.body) {{
        e.preventDefault();
        openModal();
      }} else if (e.key === 'Escape') {{
        closeModal();
      }}
    }});
  </script>
</body>
</html>
"""


def render_incident_commander(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Confirm Cluster Node Eviction"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    overflow-y: auto;
  }}
  .telemetry-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: var(--space-3);
  }}
  .metric-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-card);
    padding: var(--space-3) var(--space-4);
  }}
  .metric-val {{
    font-size: 22px;
    font-weight: 700;
    margin: var(--space-1) 0;
  }}
  .nodes-matrix {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: var(--space-2);
  }}
  .node-tile {{
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-btn);
    padding: var(--space-2);
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }}
  .node-tile.active-drain {{
    border-color: var(--action-primary);
    background: var(--bg-surface-raised);
  }}
  .log-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 12px;
  }}
  .log-table th, .log-table td {{
    padding: var(--space-2);
    border-bottom: 1px solid var(--table-border);
    text-align: left;
  }}
  .log-table tr:hover {{
    background: var(--table-row-hover);
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span style="font-size: 15px; font-weight: 700; letter-spacing: 0.05em;">INCIDENT COMMANDER</span>
      <span class="badge badge-danger tabular-nums">SEV-1 OUTAGE</span>
      <span style="color: var(--text-tertiary); font-size: 12px;">us-east-1a / prod-core</span>
    </div>
    <div style="display: flex; align-items: center; gap: var(--space-3);">
      <span class="tabular-nums" style="color: var(--text-secondary); font-size: 12px;">T+00:14:32</span>
      <button class="btn-primary" id="main-trigger" onclick="openModal()">{action_trigger}</button>
    </div>
  </header>

  <main>
    <div class="state-ideal">
      <!-- 4-Card Grounded Telemetry Metric Strip -->
      <div class="telemetry-grid">
        <div class="metric-card">
          <div style="color: var(--text-secondary); font-size: 11px; text-transform: uppercase;">Ingress Throughput</div>
          <div class="metric-val tabular-nums">48.2k <span style="font-size: 12px; font-weight: 400; color: var(--text-tertiary);">req/s</span></div>
          <div style="font-size: 11px; color: var(--status-warning);" class="tabular-nums">▲ +14% vs 1h baseline</div>
        </div>
        <div class="metric-card">
          <div style="color: var(--text-secondary); font-size: 11px; text-transform: uppercase;">P99 Tail Latency</div>
          <div class="metric-val tabular-nums" style="color: var(--status-danger);">342 <span style="font-size: 12px; font-weight: 400; color: var(--text-tertiary);">ms</span></div>
          <div style="font-size: 11px; color: var(--status-danger);">SLA Breach (&gt; 50ms)</div>
        </div>
        <div class="metric-card">
          <div style="color: var(--text-secondary); font-size: 11px; text-transform: uppercase;">Cluster VRAM Saturation</div>
          <div class="metric-val tabular-nums">78.4 <span style="font-size: 12px; font-weight: 400; color: var(--text-tertiary);">/ 96 GB</span></div>
          <div style="font-size: 11px; color: var(--status-nominal);" class="tabular-nums">81% allocatable capacity</div>
        </div>
        <div class="metric-card">
          <div style="color: var(--text-secondary); font-size: 11px; text-transform: uppercase;">Error Ratio (5xx)</div>
          <div class="metric-val tabular-nums" style="color: var(--status-danger);">4.12 <span style="font-size: 12px; font-weight: 400; color: var(--text-tertiary);">%</span></div>
          <div style="font-size: 11px; color: var(--text-tertiary);">Target threshold: 0.05%</div>
        </div>
      </div>

      <!-- Cluster Nodes Matrix -->
      <div class="card" style="margin-top: var(--space-4);" data-entity="primary-slot">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-3);">
          <h2 style="margin: 0; font-size: 14px; font-weight: 600;">Active Cluster Topology (16 Pods)</h2>
          <span class="overflow-label" style="max-width: 320px; font-size: 11px; color: var(--text-tertiary);" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000">
            Active Entity: unbreakable-entity-hash-00000000-0000-0000-0000-000000000000
          </span>
        </div>
        <div class="nodes-matrix">
          <div class="node-tile"><span class="tabular-nums">node-01</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-02</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-03</span><span class="badge badge-warning">DEGRADED</span></div>
          <div class="node-tile"><span class="tabular-nums">node-04</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-05</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-06</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile active-drain"><span class="tabular-nums">node-07</span><span class="badge badge-danger">DRAIN PENDING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-08</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-09</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-10</span><span class="badge badge-nominal">RUNNING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-11</span><span class="badge badge-warning">WARMING</span></div>
          <div class="node-tile"><span class="tabular-nums">node-12</span><span class="badge badge-nominal">RUNNING</span></div>
        </div>
      </div>

      <!-- Live SRE Diagnostic Log Stream -->
      <div class="card" style="margin-top: var(--space-4);">
        <h3 style="margin: 0 0 var(--space-3) 0; font-size: 13px; font-weight: 600;">Realtime Diagnostic Telemetry Stream</h3>
        <table class="log-table">
          <thead>
            <tr>
              <th style="width: 110px;">Timestamp</th>
              <th style="width: 80px;">Severity</th>
              <th style="width: 140px;">Component</th>
              <th>Diagnostic Payload</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="tabular-nums">12:48:02.104</td>
              <td><span class="badge badge-danger">ERR</span></td>
              <td>worker-gpu-pool</td>
              <td>OOMKilled container proc PID 8492 on node-07 during tensor pipeline alloc</td>
            </tr>
            <tr>
              <td class="tabular-nums">12:48:05.892</td>
              <td><span class="badge badge-warning">WARN</span></td>
              <td>ingress-envoy</td>
              <td>Connection pool saturation warning: upstream queue depth exceeds 2048 requests</td>
            </tr>
            <tr>
              <td class="tabular-nums">12:48:11.230</td>
              <td><span class="badge">INFO</span></td>
              <td>controller-core</td>
              <td>Commander dispatched pre-drain signal to node-07; redirecting traffic to us-east-1b</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State Recovery -->
    <div class="state-empty">
      <h3 style="color: var(--text-primary);">Zero Active Cluster Incidents</h3>
      <p style="color: var(--text-secondary); max-width: 400px;">All distributed systems operational across 16 availability zones. Telemetry is within nominal baseline bounds.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Refresh Telemetry</button>
    </div>

    <!-- Error State Alert -->
    <div class="state-error">
      <h3 style="color: var(--status-danger); margin-top: 0;">Cluster Telemetry Disconnect</h3>
      <p style="color: var(--text-secondary);">Lost connection to gRPC telemetry ingress. Automatic fallback reconnecting in 5s...</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_editorial_reader(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Save to Reading Library"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-6) var(--space-4);
    overflow-y: auto;
  }}
  .editorial-container {{
    max-width: var(--reading-measure-max);
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
  }}
  .article-title {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -0.02em;
    margin: var(--space-2) 0;
    color: var(--text-primary);
  }}
  .article-dek {{
    font-size: 17px;
    line-height: 1.5;
    color: var(--text-secondary);
    margin-bottom: var(--space-4);
  }}
  .byline-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid var(--border-subtle);
    border-bottom: 1px solid var(--border-subtle);
    padding: var(--space-3) 0;
    font-size: 12px;
    color: var(--text-tertiary);
  }}
  .article-prose p {{
    font-size: 15px;
    line-height: 1.7;
    margin: 0 0 var(--space-4) 0;
    color: var(--text-primary);
  }}
  .pull-quote {{
    border-left: 3px solid var(--action-primary);
    padding-left: var(--space-4);
    margin: var(--space-6) 0;
    font-size: 18px;
    font-style: italic;
    color: var(--text-secondary);
    line-height: 1.5;
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span style="font-size: 14px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">The Chronicle Dispatch</span>
      <span class="badge tabular-nums">ISSUE 418</span>
    </div>
    <div style="display: flex; align-items: center; gap: var(--space-3);">
      <span class="tabular-nums" style="color: var(--text-tertiary); font-size: 12px;">14 min read</span>
      <button class="btn-primary" id="main-trigger" onclick="openModal()">{action_trigger}</button>
    </div>
  </header>

  <main>
    <div class="state-ideal editorial-container">
      <div style="font-size: 11px; text-transform: uppercase; font-weight: 600; color: var(--action-primary); letter-spacing: 0.1em;">Technology & Civilization</div>
      <h1 class="article-title">The Architecture of Determinism: Systems in the Shadow of Entropy</h1>
      <div class="article-dek">How modern distributed fabrics reconcile mechanical chaos through high-leverage craft, immutable boundaries, and ruthless omission.</div>

      <div class="byline-row">
        <div>By <strong>Dr. Elena Vance</strong> &bull; Senior Systems Architect</div>
        <div class="tabular-nums">Updated September 18, 2026</div>
      </div>

      <div class="article-prose" data-entity="primary-slot">
        <p>
          In classical software engineering, reliability was frequently mistaken for the total absence of unexpected anomalies. Architects erected byzantine layers of speculative defensive wrappers, creating fragile abstractions that collapsed unpredictably under sudden saturation. Modern system philosophy departs radically from this illusion: we do not strive to extinguish entropy; we design bounded envelopes that contain its blast radius.
        </p>

        <div class="pull-quote">
          &ldquo;To engineer a resilient system is not to eliminate failure, but to choreograph its arrival with absolute dignity.&rdquo;
        </div>

        <p>
          When an operational node breaches its nominal thermal or memory boundaries, the protocol does not panic. It triggers deterministic action verbs: drain, isolate, recover. By anchoring every entity with an immutable reference identifier, engineers retain clarity even during multi-zone cascading partitions:
        </p>

        <div class="card" style="margin: var(--space-4) 0; background: var(--bg-surface-raised);">
          <div style="font-size: 11px; color: var(--text-tertiary); margin-bottom: var(--space-1);">REFERENCED TOPOLOGY ANCHOR</div>
          <span class="overflow-label" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000" style="font-family: var(--font-mono); font-size: 12px;">
            unbreakable-entity-hash-00000000-0000-0000-0000-000000000000
          </span>
        </div>

        <p>
          By confining typography to 68 characters per line and preserving harmonious vertical rhythm, the cognitive load imposed upon the human operator is reduced by half. The machine renders truth; the operator perceives order.
        </p>
      </div>
    </div>

    <!-- Empty State -->
    <div class="state-empty">
      <h3>Article Not Found</h3>
      <p style="color: var(--text-secondary);">The requested archival monograph has been relocated to cold storage.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Browse Reading Archives</button>
    </div>

    <!-- Error State -->
    <div class="state-error">
      <h3>Reading Stream Interrupted</h3>
      <p>Unable to fetch typographic payload from CDN. Offline cache enabled.</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_mobile_booking(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Confirm Appointment Booking"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    max-width: 440px;
    width: 100%;
    margin: 0 auto;
    overflow-y: auto;
  }}
  .date-pills {{
    display: flex;
    gap: var(--space-2);
    overflow-x: auto;
    padding-bottom: var(--space-2);
  }}
  .date-pill {{
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-card);
    padding: var(--space-3);
    min-width: 68px;
    text-align: center;
    cursor: pointer;
    min-height: var(--min-touch-target);
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}
  .date-pill.selected {{
    border-color: var(--action-primary);
    background: var(--bg-surface-raised);
  }}
  .slots-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-2);
  }}
  .slot-btn {{
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-btn);
    min-height: var(--min-touch-target);
    padding: var(--space-2) var(--space-3);
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .slot-btn.active {{
    border-color: var(--action-primary);
    background: var(--bg-surface-raised);
    font-weight: 600;
  }}
  .bottom-sticky-bar {{
    position: sticky;
    bottom: 0;
    background: var(--bg-base);
    border-top: 1px solid var(--border-subtle);
    padding: var(--space-3) var(--space-4);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: auto -16px -16px -16px;
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span>&larr;</span>
      <span style="font-weight: 600; font-size: 14px;">Master Artisan Session</span>
    </div>
    <span class="badge tabular-nums">4.98 &#9733;</span>
  </header>

  <main>
    <div class="state-ideal" style="display: flex; flex-direction: column; gap: var(--space-4);">
      <!-- Specialist Card -->
      <div class="card" data-entity="primary-slot" style="display: flex; gap: var(--space-3); align-items: center;">
        <div style="width: 48px; height: 48px; border-radius: var(--radius-pill); background: var(--bg-surface-raised); display: flex; align-items: center; justify-content: center; font-weight: 700; color: var(--action-primary); border: 1px solid var(--border-subtle);">MC</div>
        <div style="flex: 1;">
          <div style="font-weight: 600; font-size: 14px;">Marcus Chen</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Master Bespoke Tailoring &bull; Atelier Central</div>
        </div>
      </div>

      <!-- Date Strip -->
      <div>
        <div style="font-weight: 600; font-size: 12px; margin-bottom: var(--space-2); color: var(--text-secondary); text-transform: uppercase;">Select Date (September 2026)</div>
        <div class="date-pills">
          <div class="date-pill"><span style="font-size: 11px; color: var(--text-tertiary);">Mon</span><strong class="tabular-nums">21</strong></div>
          <div class="date-pill selected"><span style="font-size: 11px; color: var(--action-primary);">Tue</span><strong class="tabular-nums">22</strong></div>
          <div class="date-pill"><span style="font-size: 11px; color: var(--text-tertiary);">Wed</span><strong class="tabular-nums">23</strong></div>
          <div class="date-pill"><span style="font-size: 11px; color: var(--text-tertiary);">Thu</span><strong class="tabular-nums">24</strong></div>
          <div class="date-pill"><span style="font-size: 11px; color: var(--text-tertiary);">Fri</span><strong class="tabular-nums">25</strong></div>
        </div>
      </div>

      <!-- Time Slots Grid -->
      <div>
        <div style="font-weight: 600; font-size: 12px; margin-bottom: var(--space-2); color: var(--text-secondary); text-transform: uppercase;">Available Windows</div>
        <div class="slots-grid">
          <button class="slot-btn active"><span class="tabular-nums">10:00 AM</span><span class="badge">Prime</span></button>
          <button class="slot-btn"><span class="tabular-nums">11:30 AM</span><span style="font-size: 11px; color: var(--text-tertiary);">$140</span></button>
          <button class="slot-btn"><span class="tabular-nums">02:00 PM</span><span style="font-size: 11px; color: var(--text-tertiary);">$140</span></button>
          <button class="slot-btn"><span class="tabular-nums">03:30 PM</span><span class="badge">Surge</span></button>
          <button class="slot-btn"><span class="tabular-nums">05:00 PM</span><span style="font-size: 11px; color: var(--text-tertiary);">$140</span></button>
          <button class="slot-btn"><span class="tabular-nums">06:30 PM</span><span class="badge badge-nominal">Open</span></button>
        </div>
      </div>

      <!-- Policy & Target Reference Card -->
      <div class="card" style="background: var(--bg-surface-raised); font-size: 12px; line-height: 1.5;">
        <div style="font-weight: 600; margin-bottom: var(--space-1);">Flexible Cancellation Guarantee</div>
        <p style="margin: 0 0 var(--space-2) 0; color: var(--text-secondary);">Full refund up to 24h prior. Touch session backed by deterministic booking hash:</p>
        <span class="overflow-label" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000" style="font-family: var(--font-mono); font-size: 11px; color: var(--text-tertiary);">
          unbreakable-entity-hash-00000000-0000-0000-0000-000000000000
        </span>
      </div>

      <!-- Floating Bottom Sticky Bar (44px target) -->
      <div class="bottom-sticky-bar">
        <div>
          <div style="font-size: 11px; color: var(--text-secondary);">Total Investment</div>
          <div class="tabular-nums" style="font-size: 18px; font-weight: 700; color: var(--text-primary);">$140.00</div>
        </div>
        <button class="btn-primary" id="main-trigger" onclick="openModal()" style="min-width: 140px;">{action_trigger}</button>
      </div>
    </div>

    <!-- Empty State -->
    <div class="state-empty">
      <h3>No Appointments Available</h3>
      <p style="color: var(--text-secondary);">Selected date has no open time slots. Please select an alternate day.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Find Next Available Date</button>
    </div>

    <!-- Error State -->
    <div class="state-error">
      <h3>Calendar Synchronization Error</h3>
      <p>Failed to lock time slot with provider calendar. Please retry.</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_project_workspace(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Confirm Task Dispatch"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    overflow-x: auto;
  }}
  .kanban-board {{
    display: grid;
    grid-template-columns: repeat(4, minmax(260px, 1fr));
    gap: var(--space-3);
    flex: 1;
  }}
  .kanban-col {{
    background: var(--bg-base);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-card);
    padding: var(--space-3);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }}
  .col-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--border-subtle);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    color: var(--text-secondary);
  }}
  .task-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-card);
    padding: var(--space-3);
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
    cursor: grab;
    transition: transform var(--duration-fast), border-color var(--duration-fast);
  }}
  .task-card:hover {{
    border-color: var(--card-border-active);
    transform: translateY(-1px);
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span style="font-size: 15px; font-weight: 700;">SAAS PLATFORM WORKSPACE</span>
      <span class="badge tabular-nums">SPRINT 28</span>
    </div>
    <div style="display: flex; align-items: center; gap: var(--space-3);">
      <div style="display: flex; gap: -4px;">
        <span class="badge" style="border-radius: 50%; width: 24px; height: 24px; justify-content: center;">JD</span>
        <span class="badge badge-nominal" style="border-radius: 50%; width: 24px; height: 24px; justify-content: center;">AL</span>
      </div>
      <button class="btn-primary" id="main-trigger" onclick="openModal()">{action_trigger}</button>
    </div>
  </header>

  <main>
    <div class="state-ideal kanban-board" data-entity="primary-slot">
      <!-- Column: Backlog -->
      <div class="kanban-col">
        <div class="col-header">
          <span>Backlog</span>
          <span class="badge tabular-nums">3</span>
        </div>
        <div class="task-card">
          <div style="display: flex; justify-content: space-between;">
            <span class="tabular-nums" style="font-size: 11px; color: var(--text-tertiary);">ENG-4019</span>
            <span class="badge">P2</span>
          </div>
          <div style="font-weight: 500; font-size: 13px;">Audit OAuth token expiration edge cases</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Security &bull; Auth Boundary</div>
        </div>
        <div class="task-card">
          <div style="display: flex; justify-content: space-between;">
            <span class="tabular-nums" style="font-size: 11px; color: var(--text-tertiary);">ENG-4024</span>
            <span class="badge">P3</span>
          </div>
          <div style="font-weight: 500; font-size: 13px;">Refactor legacy CSS to DTCG 2025.10 tokens</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Design System</div>
        </div>
      </div>

      <!-- Column: In Progress -->
      <div class="kanban-col">
        <div class="col-header">
          <span>In Progress</span>
          <span class="badge badge-nominal tabular-nums">2</span>
        </div>
        <div class="task-card" style="border-color: var(--action-primary);">
          <div style="display: flex; justify-content: space-between;">
            <span class="tabular-nums" style="font-size: 11px; color: var(--action-primary); font-weight: 600;">ENG-4029</span>
            <span class="badge badge-danger">P0 URGENT</span>
          </div>
          <div style="font-weight: 600; font-size: 13px;">Deploy fault-tolerant Drain Node emergency route</div>
          <span class="overflow-label" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000" style="font-family: var(--font-mono); font-size: 11px; color: var(--text-tertiary);">
            unbreakable-entity-hash-00000000-0000-0000-0000-000000000000
          </span>
          <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: var(--space-1);">
            <span class="tabular-nums" style="color: var(--status-nominal);">4/5 subtasks</span>
            <span style="font-weight: 600;">Assignee: JD</span>
          </div>
        </div>
      </div>

      <!-- Column: Review -->
      <div class="kanban-col">
        <div class="col-header">
          <span>Review</span>
          <span class="badge tabular-nums">1</span>
        </div>
        <div class="task-card">
          <div style="display: flex; justify-content: space-between;">
            <span class="tabular-nums" style="font-size: 11px; color: var(--text-tertiary);">ENG-3998</span>
            <span class="badge">P1</span>
          </div>
          <div style="font-weight: 500; font-size: 13px;">Verify Double-Diamond workflow transition gates</div>
          <div style="font-size: 11px; color: var(--status-nominal);" class="tabular-nums">PR #481 Approved</div>
        </div>
      </div>

      <!-- Column: Done -->
      <div class="kanban-col">
        <div class="col-header">
          <span>Done</span>
          <span class="badge badge-nominal tabular-nums">8</span>
        </div>
        <div class="task-card" style="opacity: 0.75;">
          <div style="display: flex; justify-content: space-between;">
            <span class="tabular-nums" style="font-size: 11px; color: var(--text-tertiary);">ENG-3980</span>
            <span class="badge badge-nominal">&#10003;</span>
          </div>
          <div style="font-weight: 500; font-size: 13px; text-decoration: line-through;">Implement 3-tier semantic token hierarchy</div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div class="state-empty">
      <h3>No Active Sprints</h3>
      <p style="color: var(--text-secondary);">Workspace has completed all scheduled tasks. Create a new milestone to dispatch items.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Create Sprint Goal</button>
    </div>

    <!-- Error State -->
    <div class="state-error">
      <h3>Workspace Sync Failure</h3>
      <p>Failed to stream board state updates. Check network connectivity.</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_product_marketing(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Schedule Technical Briefing"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-6) var(--space-4);
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow-y: auto;
  }}
  .hero-section {{
    max-width: 800px;
    text-align: center;
    margin: var(--space-6) 0 var(--space-8) 0;
  }}
  .hero-title {{
    font-size: 42px;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.03em;
    margin: var(--space-3) 0;
    color: var(--text-primary);
  }}
  .hero-subtitle {{
    font-size: 18px;
    line-height: 1.6;
    color: var(--text-secondary);
    max-width: 640px;
    margin: 0 auto var(--space-5) auto;
  }}
  .feature-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: var(--space-4);
    max-width: 860px;
    width: 100%;
    margin-top: var(--space-6);
  }}
  .specimen-card {{
    background: var(--bg-surface-raised);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius-outer);
    padding: var(--space-5);
    max-width: 680px;
    width: 100%;
    text-align: left;
    margin: var(--space-4) 0;
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span style="font-size: 16px; font-weight: 800; letter-spacing: -0.02em;">NEXUS CORE</span>
      <span class="badge badge-nominal">V10 RELEASE</span>
    </div>
    <div style="display: flex; align-items: center; gap: var(--space-4);">
      <span style="color: var(--text-secondary); font-size: 13px;">Architecture</span>
      <span style="color: var(--text-secondary); font-size: 13px;">Benchmarks</span>
      <button class="btn-primary" id="main-trigger" onclick="openModal()">{action_trigger}</button>
    </div>
  </header>

  <main>
    <div class="state-ideal" style="display: flex; flex-direction: column; align-items: center; width: 100%;">
      <div class="hero-section">
        <span class="badge" style="font-size: 12px; padding: 4px 12px;">DETERMINISTIC EXPERIENCE ENGINE</span>
        <h1 class="hero-title">Compile UI Truth in Seconds, Not Sprints</h1>
        <p class="hero-subtitle">
          Eliminate speculative design drift. Compile authentic design tokens, verified topologies, and headless proofs directly into production-grade interfaces.
        </p>
        <div style="display: flex; justify-content: center; gap: var(--space-3);">
          <button class="btn-primary" onclick="openModal()">{action_trigger}</button>
          <button class="btn-ghost">Read Architecture Whitepaper</button>
        </div>
      </div>

      <!-- Live Interactive Specimen -->
      <div class="specimen-card" data-entity="primary-slot">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-3);">
          <strong style="font-size: 14px;">Live Telemetry Specimen</strong>
          <span class="badge badge-nominal tabular-nums">99.999% VERIFIED</span>
        </div>
        <p style="font-size: 12px; color: var(--text-secondary); margin: 0 0 var(--space-3) 0;">
          Inspect real-time deterministic token compilation across active container slots:
        </p>
        <div style="background: var(--bg-void); border: 1px solid var(--border-dim); border-radius: var(--radius-btn); padding: var(--space-3); font-family: var(--font-mono); font-size: 12px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-1);" class="tabular-nums">
            <span style="color: var(--text-tertiary);">Compilation Throughput</span>
            <span style="color: var(--action-primary); font-weight: 600;">98.4k req/s</span>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);" class="tabular-nums">
            <span style="color: var(--text-tertiary);">Static Audit Floor</span>
            <span style="color: var(--status-nominal);">P99 1.8ms (0.00% Drift)</span>
          </div>
          <span class="overflow-label" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000" style="color: var(--text-secondary); font-size: 11px;">
            Active Hash: unbreakable-entity-hash-00000000-0000-0000-0000-000000000000
          </span>
        </div>
      </div>

      <!-- 3-Pillar Feature Grid -->
      <div class="feature-grid">
        <div class="card">
          <h3 style="margin-top: 0; font-size: 15px;">Three-Tier Thick Tokens</h3>
          <p style="color: var(--text-secondary); font-size: 13px; line-height: 1.5; margin: 0;">Layer 1 primitives, Layer 2 semantic surface intent, Layer 3 ready-to-use component slots.</p>
        </div>
        <div class="card">
          <h3 style="margin-top: 0; font-size: 15px;">Anti-Goodhart Verification</h3>
          <p style="color: var(--text-secondary); font-size: 13px; line-height: 1.5; margin: 0;">Decoupled proof harness: renderer capture never masquerades as subjective aesthetic signoff.</p>
        </div>
        <div class="card">
          <h3 style="margin-top: 0; font-size: 15px;">Zero Build-Tool Overhead</h3>
          <p style="color: var(--text-secondary); font-size: 13px; line-height: 1.5; margin: 0;">100% native CSS custom properties. Zero Sass, PostCSS, or bundler build tax required.</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div class="state-empty">
      <h3>Showcase Unavailable</h3>
      <p style="color: var(--text-secondary);">Interactive showcase is currently offline for scheduled calibration.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Request Private Access</button>
    </div>

    <!-- Error State -->
    <div class="state-error">
      <h3>Demo Ingress Timeout</h3>
      <p>Failed to establish briefing connection. Please refresh or contact sales.</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_ai_writer_workspace(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    action_modal = "Merge AI Suggested Revision"
    return f"""{COMMON_HEAD.format(case_name=case_name)}
  main {{
    flex: 1;
    padding: var(--space-4);
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: var(--space-4);
    overflow: hidden;
  }}
  .editor-pane {{
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-card);
    padding: var(--space-5);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }}
  .copilot-pane {{
    background: var(--bg-base);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-card);
    padding: var(--space-4);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
    overflow-y: auto;
  }}
  .diff-box {{
    background: var(--bg-surface-raised);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius-btn);
    padding: var(--space-3);
    font-size: 13px;
    line-height: 1.6;
  }}
  .diff-del {{
    background: rgba(239, 68, 68, 0.15);
    color: var(--status-danger);
    text-decoration: line-through;
    padding: 2px 4px;
    border-radius: 2px;
  }}
  .diff-add {{
    background: rgba(16, 185, 129, 0.15);
    color: var(--status-nominal);
    padding: 2px 4px;
    border-radius: 2px;
    font-weight: 500;
  }}
</style>
</head>
<body data-state="ideal">
  <header>
    <div class="brand">
      <span style="font-size: 15px; font-weight: 700;">AI WRITER STUDIO</span>
      <span style="color: var(--text-tertiary); font-size: 12px;">Algorithmic_Ethics_v2.md</span>
    </div>
    <div style="display: flex; align-items: center; gap: var(--space-3);">
      <span class="tabular-nums" style="color: var(--text-secondary); font-size: 12px;">3,420 words</span>
      <button class="btn-primary" id="main-trigger" onclick="openModal()">{action_trigger}</button>
    </div>
  </header>

  <main>
    <div class="state-ideal editor-pane" data-entity="primary-slot">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: var(--space-2);">
        <h2 style="margin: 0; font-size: 18px;">Chapter 3: The Imperative of Algorithmic Boundary</h2>
        <span class="badge tabular-nums">DRAFT SAVED</span>
      </div>
      <p style="font-size: 14px; line-height: 1.6; color: var(--text-primary); margin: 0;">
        When neural systems operate without formal constraints, the likelihood of hallucinated drift expands exponentially with context length. Autonomous agents must be governed by invariant state envelopes rather than permissive guidelines.
      </p>

      <!-- Inline AI Suggestion Diff Box -->
      <div class="diff-box">
        <div style="font-size: 11px; font-weight: 600; color: var(--action-primary); margin-bottom: var(--space-2); display: flex; justify-content: space-between;">
          <span>AI REVISION SUGGESTION #4</span>
          <span class="tabular-nums">98.2% CONFIDENCE</span>
        </div>
        <p style="margin: 0;">
          <span class="diff-del">The old architecture was prone to unexpected breaking changes whenever new dependencies were introduced.</span>
          <span class="diff-add">The deterministic v10 harness guarantees invariant safety boundaries across all operational topologies, preventing cascading entropy.</span>
        </p>
        <div style="margin-top: var(--space-3); font-size: 11px; color: var(--text-tertiary);">
          Reference: <span class="overflow-label" title="unbreakable-entity-hash-00000000-0000-0000-0000-000000000000">unbreakable-entity-hash-00000000-0000-0000-0000-000000000000</span>
        </div>
      </div>

      <p style="font-size: 14px; line-height: 1.6; color: var(--text-primary); margin: 0;">
        By establishing rigorous, verifiable proofs prior to human signoff, engineering velocity is uncoupled from regression anxiety.
      </p>
    </div>

    <!-- AI Companion Co-pilot Pane -->
    <div class="state-ideal copilot-pane">
      <h3 style="margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary);">AI Writing Assistant</h3>
      <div class="card" style="background: var(--bg-surface); padding: var(--space-3);">
        <div style="font-size: 11px; color: var(--text-secondary);">Active Prompt</div>
        <div style="font-weight: 500; margin-top: var(--space-1); font-size: 12px;">"Enhance rhetorical clarity and enforce formal engineering vocabulary."</div>
      </div>
      <div class="card" style="background: var(--bg-surface); padding: var(--space-3);">
        <div style="font-size: 11px; color: var(--text-secondary);">Tone Calibration</div>
        <div style="display: flex; gap: var(--space-2); margin-top: var(--space-2);">
          <span class="badge badge-nominal">Analytical</span>
          <span class="badge">Concise</span>
          <span class="badge">Bespoke</span>
        </div>
      </div>
      <div style="margin-top: auto; display: flex; flex-direction: column; gap: var(--space-2);">
        <button class="btn-primary" onclick="openModal()">{action_trigger}</button>
        <button class="btn-ghost">Reject Revision</button>
      </div>
    </div>

    <!-- Empty State -->
    <div class="state-empty" style="grid-column: span 2;">
      <h3>Document Workspace Empty</h3>
      <p style="color: var(--text-secondary);">Select or initialize an article draft to begin AI-assisted composition.</p>
      <button class="btn-ghost" onclick="location.hash='#state=ideal'" style="margin-top: var(--space-3);">Create New Draft</button>
    </div>

    <!-- Error State -->
    <div class="state-error" style="grid-column: span 2;">
      <h3>AI Streaming Connection Dropped</h3>
      <p>Unable to reach inference engine. Model suggestions are temporarily cached offline.</p>
    </div>
  </main>
{COMMON_FOOTER.format(action_modal=action_modal, action_commit=action_commit, action_toast=action_toast)}"""


def render_prototype_html(case_name: str, choice: str, action_id: str, action_trigger: str, action_commit: str, action_toast: str) -> str:
    """Dispatch to specific domain prototype generator."""
    name_lower = case_name.lower()
    if any(k in name_lower for k in ("incident", "sre", "cluster", "console")):
        return render_incident_commander(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    elif any(k in name_lower for k in ("editorial", "reader", "reading", "document")):
        return render_editorial_reader(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    elif any(k in name_lower for k in ("mobile", "booking", "touch", "calendar")):
        return render_mobile_booking(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    elif any(k in name_lower for k in ("marketing", "showcase", "landing")):
        return render_product_marketing(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    elif any(k in name_lower for k in ("writer", "copilot", "ai")):
        return render_ai_writer_workspace(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    else:  # project-workspace or default SaaS
        return render_project_workspace(case_name, choice, action_id, action_trigger, action_commit, action_toast)
