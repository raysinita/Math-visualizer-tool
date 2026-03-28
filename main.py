import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Power of a Point", layout="wide", page_icon="◉")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ◉ Power of a Point")
    st.markdown("---")
    R = st.slider("Circle radius", 50, 200, 120, 5)
    st.markdown("---")
    st.markdown("**Drag on canvas:**")
    st.markdown("- **P** — the power point")
    st.markdown("- **A, B** — chord 1 endpoints")
    st.markdown("- **C, D** — chord 2 endpoints")
    st.markdown("---")
    show_proof    = st.checkbox("Show proof", value=False)
    show_triangle = st.checkbox("Show similar triangles", value=True)
    dark_mode     = st.checkbox("Dark mode", value=True)
    st.markdown("---")
    st.markdown(
        "<small style='color:#888'>The theorem: for any two chords "
        "through P,<br><b>PA·PB = PC·PD = |d²−r²|</b></small>",
        unsafe_allow_html=True,
    )

# ── HTML/JS canvas component ──────────────────────────────────────────────────
BG       = "#0e1117" if dark_mode else "#f7f7f2"
SURFACE  = "rgba(255,255,255,0.04)" if dark_mode else "rgba(0,0,0,0.04)"
BORDER   = "rgba(255,255,255,0.08)" if dark_mode else "rgba(0,0,0,0.08)"
TEXT_CLR = "#e8e6df" if dark_mode else "#1a1a1a"
MUTED    = "rgba(255,255,255,0.3)" if dark_mode else "rgba(0,0,0,0.3)"
GRID_CLR = "rgba(255,255,255,0.035)" if dark_mode else "rgba(0,0,0,0.04)"
AXIS_CLR = "rgba(255,255,255,0.07)" if dark_mode else "rgba(0,0,0,0.07)"
SHOW_TRI = "true" if show_triangle else "false"

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;500;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: {BG};
    font-family: 'Sora', sans-serif;
    overflow: hidden;
    user-select: none;
    -webkit-user-select: none;
  }}

  #root {{
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 14px;
    gap: 12px;
  }}

  #canvas-box {{
    flex: 1;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid {BORDER};
    position: relative;
  }}

  canvas {{
    display: block;
    width: 100%;
    height: 100%;
  }}

  #stats {{
    display: flex;
    gap: 10px;
    flex-shrink: 0;
  }}

  .card {{
    flex: 1;
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 13px;
    min-width: 0;
  }}

  .card-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: {'#556' if dark_mode else '#aaa'};
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 5px;
  }}

  .card-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_CLR};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  #mode-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px 3px 7px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
    transition: all 0.25s ease;
  }}
  #mode-pill.inside  {{ background: rgba(92,240,122,0.13); color: #5cf07a; border: 1px solid rgba(92,240,122,0.25); }}
  #mode-pill.outside {{ background: rgba(92,160,240,0.13); color: #5ca0f0; border: 1px solid rgba(92,160,240,0.25); }}
  #mode-pill .dot {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}
  #mode-pill.inside  .dot {{ background: #5cf07a; }}
  #mode-pill.outside .dot {{ background: #5ca0f0; }}

  .good {{ color: #5cf07a !important; }}
  .bad  {{ color: #f05c5c !important; }}

  #hint {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: {'rgba(255,255,255,0.18)' if dark_mode else 'rgba(0,0,0,0.2)'};
    text-align: center;
    flex-shrink: 0;
    padding-bottom: 2px;
    letter-spacing: 0.04em;
  }}
</style>
</head>
<body>
<div id="root">
  <div id="canvas-box"><canvas id="cv"></canvas></div>

  <div id="stats">
    <div class="card">
      <div class="card-label">Mode</div>
      <div id="mode-pill" class="outside"><span class="dot"></span><span id="mode-txt">Outside</span></div>
    </div>
    <div class="card">
      <div class="card-label">PA · PB</div>
      <div class="card-value" id="v-ab">—</div>
    </div>
    <div class="card">
      <div class="card-label">PC · PD</div>
      <div class="card-value" id="v-cd">—</div>
    </div>
    <div class="card">
      <div class="card-label">Power |d²−r²|</div>
      <div class="card-value" id="v-pow">—</div>
    </div>
    <div class="card">
      <div class="card-label">Δ (→ 0)</div>
      <div class="card-value" id="v-delta">—</div>
    </div>
  </div>

  <div id="hint">drag P · A · B · C · D — or click empty space to move P</div>
</div>

<script>
const cv  = document.getElementById('cv');
const ctx = cv.getContext('2d');
const DARK     = {str(dark_mode).lower()};
const SHOW_TRI = {SHOW_TRI};
const R_INIT   = {R};

// ── Colors ────────────────────────────────────────────────────────────────────
const C = {{
  bg:         '{BG}',
  grid:       '{GRID_CLR}',
  axis:       '{AXIS_CLR}',
  circle:     DARK ? 'rgba(255,255,255,0.65)' : 'rgba(0,0,0,0.65)',
  circleFill: DARK ? 'rgba(255,255,255,0.015)': 'rgba(0,0,0,0.015)',
  ptP:        '#c8f060',
  chord1:     '#5b9cf6',
  chord2:     '#f0855b',
  text:       '{TEXT_CLR}',
  muted:      '{MUTED}',
  tri1:       'rgba(91,156,246,0.07)',
  tri2:       'rgba(240,133,91,0.07)',
  scratch:    DARK ? '#0e1117' : '#f7f7f2',
}};

// ── State ─────────────────────────────────────────────────────────────────────
let W, H, CX, CY, R = R_INIT;
let angle1 = 0.45, angle2 = 2.05;
let dragging = null;

const pts = {{
  P: null,
  A: null, B: null,
  C: null, D: null,
}};

// ── Geometry ──────────────────────────────────────────────────────────────────
function circleHits(px, py, dx, dy) {{
  const fx = px - CX, fy = py - CY;
  const a  = dx*dx + dy*dy;
  const b  = 2*(fx*dx + fy*dy);
  const c  = fx*fx + fy*fy - R*R;
  const disc = b*b - 4*a*c;
  if (disc < 0) return null;
  const sq = Math.sqrt(disc);
  const t1 = (-b - sq) / (2*a), t2 = (-b + sq) / (2*a);
  return [
    {{x: px + dx*t1, y: py + dy*t1}},
    {{x: px + dx*t2, y: py + dy*t2}},
  ];
}}

function recomputeChords() {{
  const {{x: px, y: py}} = pts.P;
  const h1 = circleHits(px, py, Math.cos(angle1), Math.sin(angle1));
  const h2 = circleHits(px, py, Math.cos(angle2), Math.sin(angle2));
  if (h1) {{ pts.A = h1[0]; pts.B = h1[1]; }}
  if (h2) {{ pts.C = h2[0]; pts.D = h2[1]; }}
}}

function snapToCircle(x, y) {{
  const dx = x - CX, dy = y - CY;
  const d  = Math.sqrt(dx*dx + dy*dy) || 1;
  return {{x: CX + dx/d*R, y: CY + dy/d*R}};
}}

function dist(a, b) {{ return Math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2); }}

// ── Canvas resize ─────────────────────────────────────────────────────────────
function resize() {{
  const box = document.getElementById('canvas-box');
  W = box.clientWidth;
  H = box.clientHeight;
  const dpr = devicePixelRatio || 1;
  cv.width  = W * dpr;
  cv.height = H * dpr;
  cv.style.width  = W + 'px';
  cv.style.height = H + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  CX = W / 2;
  CY = H / 2;
}}

function initPoints() {{
  pts.P = {{x: CX + Math.round(R * 1.45), y: CY + 22}};
  recomputeChords();
}}

// ── Draw helpers ──────────────────────────────────────────────────────────────
function drawGrid() {{
  const step = 50;
  ctx.lineWidth = 0.8;
  ctx.strokeStyle = C.grid;
  for (let x = ((CX % step) + step) % step; x < W; x += step) {{
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
  }}
  for (let y = ((CY % step) + step) % step; y < H; y += step) {{
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }}
  ctx.strokeStyle = C.axis;
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(CX, 0); ctx.lineTo(CX, H); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0, CY); ctx.lineTo(W, CY); ctx.stroke();
}}

function drawCircle() {{
  ctx.beginPath();
  ctx.arc(CX, CY, R, 0, Math.PI * 2);
  ctx.fillStyle   = C.circleFill;
  ctx.fill();
  ctx.strokeStyle = C.circle;
  ctx.lineWidth   = 1.8;
  ctx.stroke();

  // Center
  ctx.beginPath();
  ctx.arc(CX, CY, 3.5, 0, Math.PI * 2);
  ctx.fillStyle = C.muted;
  ctx.fill();

  // Radius tick
  ctx.save();
  ctx.strokeStyle = C.muted;
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([3, 5]);
  ctx.beginPath(); ctx.moveTo(CX, CY); ctx.lineTo(CX + R, CY); ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
  ctx.fillStyle    = C.muted;
  ctx.font         = '10px "JetBrains Mono", monospace';
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(`r = ${{R}}`, CX + R/2, CY - 11);
}}

function drawChordLine(A, B, color) {{
  if (!A || !B) return;
  ctx.beginPath();
  ctx.moveTo(A.x, A.y);
  ctx.lineTo(B.x, B.y);
  ctx.strokeStyle = color;
  ctx.lineWidth   = 1.8;
  ctx.stroke();
}}

function drawSegLabel(p1, p2, txt, color) {{
  const mx = (p1.x + p2.x) / 2;
  const my = (p1.y + p2.y) / 2;
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const ln = Math.sqrt(dx*dx + dy*dy) || 1;
  const nx = -dy / ln * 13, ny = dx / ln * 13;
  ctx.font         = '10px "JetBrains Mono", monospace';
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'middle';
  // backdrop
  ctx.fillStyle = C.scratch + 'cc';
  ctx.fillText(txt, mx + nx, my + ny);
  ctx.fillStyle = color;
  ctx.fillText(txt, mx + nx, my + ny);
}}

function drawTriangles() {{
  if (!pts.A || !pts.B || !pts.C || !pts.D) return;
  const P = pts.P;

  // △ PAD
  ctx.beginPath();
  ctx.moveTo(P.x, P.y);
  ctx.lineTo(pts.A.x, pts.A.y);
  ctx.lineTo(pts.D.x, pts.D.y);
  ctx.closePath();
  ctx.fillStyle   = C.tri1;
  ctx.fill();
  ctx.save();
  ctx.strokeStyle = C.chord1 + '50';
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([4, 5]);
  ctx.stroke();
  ctx.restore();

  // △ PCB
  ctx.beginPath();
  ctx.moveTo(P.x, P.y);
  ctx.lineTo(pts.C.x, pts.C.y);
  ctx.lineTo(pts.B.x, pts.B.y);
  ctx.closePath();
  ctx.fillStyle   = C.tri2;
  ctx.fill();
  ctx.save();
  ctx.strokeStyle = C.chord2 + '50';
  ctx.lineWidth   = 0.8;
  ctx.setLineDash([4, 5]);
  ctx.stroke();
  ctx.restore();
}}

function drawDistLine() {{
  const P = pts.P;
  ctx.save();
  ctx.strokeStyle = C.ptP + '35';
  ctx.lineWidth   = 1;
  ctx.setLineDash([4, 6]);
  ctx.beginPath(); ctx.moveTo(CX, CY); ctx.lineTo(P.x, P.y); ctx.stroke();
  ctx.restore();
  const d   = dist(P, {{x: CX, y: CY}});
  const mx  = (CX + P.x) / 2 - 10;
  const my  = (CY + P.y) / 2 - 10;
  ctx.fillStyle    = C.ptP + '80';
  ctx.font         = '9px "JetBrains Mono", monospace';
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(`d=${{d.toFixed(1)}}`, mx, my);
}}

function drawPoint(x, y, color, label, r = 7) {{
  // glow
  ctx.beginPath();
  ctx.arc(x, y, r + 5, 0, Math.PI * 2);
  ctx.fillStyle = color + '18';
  ctx.fill();
  // body
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle   = color;
  ctx.fill();
  ctx.strokeStyle = C.scratch;
  ctx.lineWidth   = 2;
  ctx.stroke();
  // label
  ctx.fillStyle    = C.text;
  ctx.font         = '500 12px "Sora", sans-serif';
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'bottom';
  ctx.fillText(label, x, y - r - 4);
}}

// ── Update stats panel ────────────────────────────────────────────────────────
function updateStats() {{
  const P  = pts.P;
  const d  = dist(P, {{x: CX, y: CY}});
  const inside = d < R;
  const power  = Math.abs(d*d - R*R);

  const pill = document.getElementById('mode-pill');
  pill.className = inside ? 'inside' : 'outside';
  document.getElementById('mode-txt').textContent = inside ? 'Inside' : 'Outside';

  document.getElementById('v-pow').textContent = power.toFixed(2);

  if (pts.A && pts.B && pts.C && pts.D) {{
    const PA = dist(P, pts.A), PB = dist(P, pts.B);
    const PC = dist(P, pts.C), PD = dist(P, pts.D);
    const ab = PA * PB, cd = PC * PD;
    const delta = Math.abs(ab - cd);
    document.getElementById('v-ab').textContent    = ab.toFixed(2);
    document.getElementById('v-cd').textContent    = cd.toFixed(2);
    const dEl = document.getElementById('v-delta');
    dEl.textContent = delta.toFixed(3);
    dEl.className   = 'card-value ' + (delta < 1.5 ? 'good' : 'bad');
  }}
}}

// ── Main draw ─────────────────────────────────────────────────────────────────
function draw() {{
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = C.bg;
  ctx.fillRect(0, 0, W, H);

  drawGrid();
  drawCircle();
  drawDistLine();

  if (SHOW_TRI) drawTriangles();

  // Chords
  drawChordLine(pts.A, pts.B, C.chord1);
  drawChordLine(pts.C, pts.D, C.chord2);

  // Segment labels
  if (pts.A && pts.B && pts.C && pts.D) {{
    const P = pts.P;
    drawSegLabel(P, pts.A, 'PA', C.chord1);
    drawSegLabel(P, pts.B, 'PB', C.chord1);
    drawSegLabel(P, pts.C, 'PC', C.chord2);
    drawSegLabel(P, pts.D, 'PD', C.chord2);
  }}

  // Chord endpoints (draw before P so P is on top)
  if (pts.A) drawPoint(pts.A.x, pts.A.y, C.chord1, 'A', 6);
  if (pts.B) drawPoint(pts.B.x, pts.B.y, C.chord1, 'B', 6);
  if (pts.C) drawPoint(pts.C.x, pts.C.y, C.chord2, 'C', 6);
  if (pts.D) drawPoint(pts.D.x, pts.D.y, C.chord2, 'D', 6);

  // P last (always on top)
  drawPoint(pts.P.x, pts.P.y, C.ptP, 'P', 9);

  updateStats();
}}

// ── Drag logic ────────────────────────────────────────────────────────────────
const HIT_R = 16;

function getPos(e) {{
  const rect = cv.getBoundingClientRect();
  const src  = e.touches ? e.touches[0] : e;
  return {{
    x: (src.clientX - rect.left) * (W / rect.width),
    y: (src.clientY - rect.top)  * (H / rect.height),
  }};
}}

function hitTest(x, y) {{
  const order = ['P', 'A', 'B', 'C', 'D'];
  for (const k of order) {{
    const p = pts[k];
    if (!p) continue;
    if (dist({{x, y}}, p) < HIT_R) return k;
  }}
  return null;
}}

cv.addEventListener('mousedown', e => {{
  e.preventDefault();
  const pos = getPos(e);
  const hit = hitTest(pos.x, pos.y);
  if (hit) {{
    dragging = hit;
  }} else {{
    // Teleport P
    pts.P = {{x: pos.x, y: pos.y}};
    recomputeChords();
    draw();
  }}
}});

cv.addEventListener('mousemove', e => {{
  e.preventDefault();
  const pos = getPos(e);

  // Cursor styling
  if (!dragging) {{
    cv.style.cursor = hitTest(pos.x, pos.y) ? 'grab' : 'crosshair';
  }} else {{
    cv.style.cursor = 'grabbing';
  }}

  if (!dragging) return;

  if (dragging === 'P') {{
    pts.P = pos;
    recomputeChords();
  }} else {{
    // Snap endpoint to circle, recompute other end through P
    const snapped = snapToCircle(pos.x, pos.y);
    if (dragging === 'A' || dragging === 'B') {{
      angle1 = Math.atan2(snapped.y - pts.P.y, snapped.x - pts.P.x);
      recomputeChords();
      // pin the dragged end exactly to where finger is
      pts[dragging] = snapped;
    }} else {{
      angle2 = Math.atan2(snapped.y - pts.P.y, snapped.x - pts.P.x);
      recomputeChords();
      pts[dragging] = snapped;
    }}
  }}
  draw();
}});

cv.addEventListener('mouseup',    () => {{ dragging = null; }});
cv.addEventListener('mouseleave', () => {{ dragging = null; }});

cv.addEventListener('touchstart', e => {{
  e.preventDefault();
  const pos = getPos(e);
  dragging = hitTest(pos.x, pos.y);
  if (!dragging) {{
    pts.P = pos;
    recomputeChords();
    draw();
  }}
}}, {{passive: false}});

cv.addEventListener('touchmove', e => {{
  e.preventDefault();
  if (!dragging) return;
  const pos = getPos(e);
  if (dragging === 'P') {{
    pts.P = pos;
    recomputeChords();
  }} else {{
    const snapped = snapToCircle(pos.x, pos.y);
    if (dragging === 'A' || dragging === 'B') {{
      angle1 = Math.atan2(snapped.y - pts.P.y, snapped.x - pts.P.x);
      recomputeChords();
      pts[dragging] = snapped;
    }} else {{
      angle2 = Math.atan2(snapped.y - pts.P.y, snapped.x - pts.P.x);
      recomputeChords();
      pts[dragging] = snapped;
    }}
  }}
  draw();
}}, {{passive: false}});

cv.addEventListener('touchend', () => {{ dragging = null; }});

// ── Init ──────────────────────────────────────────────────────────────────────
function boot() {{
  resize();
  initPoints();
  draw();
}}

window.addEventListener('resize', () => {{
  resize();
  // keep P in relative position
  if (pts.P) {{
    pts.P.x = Math.min(Math.max(pts.P.x, 20), W - 20);
    pts.P.y = Math.min(Math.max(pts.P.y, 20), H - 20);
    recomputeChords();
  }}
  draw();
}});

boot();
</script>
</body>
</html>"""

components.html(html, height=640, scrolling=False)

# ── Proof (optional) ──────────────────────────────────────────────────────────
if show_proof:
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Inside — intersecting chords")
        st.markdown(r"""
$\triangle PAD \sim \triangle PCB$ because:
- $\angle APD = \angle CPB$ (vertical angles)
- $\angle DAP = \angle BCP$ (same arc $DB$)

$$\frac{PA}{PC} = \frac{PD}{PB} \;\Longrightarrow\; \boxed{PA \cdot PB = PC \cdot PD = r^2 - d^2}$$
        """)
    with c2:
        st.markdown("#### Outside — secant-secant")
        st.markdown(r"""
$\triangle PAD \sim \triangle PCB$ because:
- $\angle P$ is shared
- $\angle PAD = \angle PCB$ (same arc $BD$)

$$\frac{PA}{PC} = \frac{PD}{PB} \;\Longrightarrow\; \boxed{PA \cdot PB = PC \cdot PD = d^2 - r^2}$$

**Tangent special case:** $PT^2 = d^2 - r^2$
        """)
