import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Power of a Point", layout="wide", page_icon="◉")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ◉ Power of a Point")
    st.markdown("---")
    R = st.slider("Circle radius", 50, 180, 120, 5)
    st.markdown("---")
    show_proof    = st.checkbox("Show proof writeup", value=False)
    show_triangle = st.checkbox("Show similar triangles", value=True)
    show_grid     = st.checkbox("Show coordinate grid", value=True)
    dark_mode     = st.checkbox("Dark mode", value=True)
    st.markdown("---")
    st.markdown("**Keyboard shortcuts**")
    st.markdown("`R` — reset · `T` — triangles · `G` — grid · `Space` — next mode")
    st.markdown("---")
    st.markdown(
        "<small style='color:#666'>Three cases: chords (inside) · "
        "secants (outside) · tangent (on circle).<br><br>"
        "In every case: <b>PA·PB = PC·PD = |d²−r²|</b></small>",
        unsafe_allow_html=True,
    )

BG        = "#0b0d12" if dark_mode else "#f4f3ee"
TEXT_CLR  = "#e0ddd6" if dark_mode else "#1c1c1a"
MUTED     = "rgba(255,255,255,0.28)" if dark_mode else "rgba(0,0,0,0.28)"
SURF      = "rgba(255,255,255,0.04)" if dark_mode else "rgba(0,0,0,0.035)"
BORDER    = "rgba(255,255,255,0.07)" if dark_mode else "rgba(0,0,0,0.07)"
SHOW_TRI  = "true" if show_triangle else "false"
SHOW_GRID = "true" if show_grid else "false"

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,500;1,9..144,300&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{BG};font-family:'JetBrains Mono',monospace;overflow:hidden;user-select:none;-webkit-user-select:none}}
#root{{display:flex;flex-direction:column;height:100vh;padding:12px;gap:10px}}
#canvas-box{{flex:1;border-radius:14px;overflow:hidden;border:1px solid {BORDER};position:relative;min-height:0}}
canvas{{display:block;width:100%;height:100%}}

/* Tooltip */
#tooltip{{
  position:absolute;pointer-events:none;
  background:{'rgba(18,20,28,0.96)' if dark_mode else 'rgba(245,244,238,0.96)'};
  border:1px solid {BORDER};
  border-radius:10px;padding:9px 13px;
  font-size:11px;line-height:1.7;color:{TEXT_CLR};
  max-width:220px;opacity:0;transition:opacity 0.18s;
  backdrop-filter:blur(8px);
  box-shadow:0 4px 24px rgba(0,0,0,0.3);
}}
#tooltip.visible{{opacity:1}}
#tooltip b{{color:#c8f060;font-weight:600}}
#tooltip .dim{{color:{MUTED};font-size:10px}}

/* Stats bar */
#stats{{display:flex;gap:8px;flex-shrink:0}}
.card{{flex:1;background:{SURF};border:1px solid {BORDER};border-radius:10px;padding:8px 12px;min-width:0;transition:border-color 0.2s}}
.card.highlight{{border-color:rgba(200,240,96,0.35)}}
.lbl{{font-size:9px;color:{'#4a4e5a' if dark_mode else '#aaa'};text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px}}
.val{{font-size:14px;font-weight:600;color:{TEXT_CLR};white-space:nowrap;font-family:'JetBrains Mono',monospace}}
.val.good{{color:#5cf07a}}.val.bad{{color:#f05c5c}}.val.warn{{color:#f0c85b}}

/* Mode pill */
#pill{{display:inline-flex;align-items:center;gap:5px;padding:3px 10px 3px 7px;border-radius:20px;font-size:9px;font-weight:600;letter-spacing:0.07em;transition:all 0.25s}}
#pill.inside   {{background:rgba(92,240,122,0.12);color:#5cf07a;border:1px solid rgba(92,240,122,0.22)}}
#pill.outside  {{background:rgba(92,160,240,0.12);color:#5ca0f0;border:1px solid rgba(92,160,240,0.22)}}
#pill.tangent  {{background:rgba(200,240,96,0.12); color:#c8f060;border:1px solid rgba(200,240,96,0.22)}}
#pill .dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0}}
#pill.inside .dot{{background:#5cf07a}}
#pill.outside .dot{{background:#5ca0f0}}
#pill.tangent .dot{{background:#c8f060}}

/* Bottom row */
#bottom{{display:flex;align-items:center;gap:12px;flex-shrink:0}}
#hint{{font-size:9px;color:{'rgba(255,255,255,0.18)' if dark_mode else 'rgba(0,0,0,0.18)'};letter-spacing:0.05em;flex:1}}
#anim-btn{{
  padding:6px 14px;border-radius:8px;font-size:10px;font-weight:600;
  font-family:'JetBrains Mono',monospace;letter-spacing:0.05em;cursor:pointer;
  background:rgba(200,240,96,0.12);color:#c8f060;
  border:1px solid rgba(200,240,96,0.25);transition:all 0.15s;
}}
#anim-btn:hover{{background:rgba(200,240,96,0.2)}}
#anim-btn:active{{transform:scale(0.97)}}
#reset-btn{{
  padding:6px 14px;border-radius:8px;font-size:10px;font-weight:600;
  font-family:'JetBrains Mono',monospace;letter-spacing:0.05em;cursor:pointer;
  background:{SURF};color:{MUTED};
  border:1px solid {BORDER};transition:all 0.15s;
}}
#reset-btn:hover{{color:{TEXT_CLR};border-color:{'rgba(255,255,255,0.2)' if dark_mode else 'rgba(0,0,0,0.2)'}}}
</style>
</head>
<body>
<div id="root">
  <div id="canvas-box">
    <canvas id="cv"></canvas>
    <div id="tooltip"></div>
  </div>

  <div id="stats">
    <div class="card" id="card-mode">
      <div class="lbl">Mode</div>
      <div id="pill" class="outside"><span class="dot"></span><span id="mode-txt">Outside</span></div>
    </div>
    <div class="card">
      <div class="lbl">PA · PB</div>
      <div class="val" id="v-ab">—</div>
    </div>
    <div class="card">
      <div class="lbl">PC · PD</div>
      <div class="val" id="v-cd">—</div>
    </div>
    <div class="card highlight">
      <div class="lbl">Power  |d²−r²|</div>
      <div class="val" id="v-pow">—</div>
    </div>
    <div class="card">
      <div class="lbl">Δ (→ 0)</div>
      <div class="val" id="v-delta">—</div>
    </div>
    <div class="card">
      <div class="lbl">d (|OP|)</div>
      <div class="val" id="v-d">—</div>
    </div>
  </div>

  <div id="bottom">
    <div id="hint">drag P · A · B · C · D — click empty space to move P — R to reset</div>
    <button id="reset-btn" onclick="resetAll()">↺ Reset</button>
    <button id="anim-btn" onclick="startAnimation()">▶ Animate proof</button>
  </div>
</div>

<script>
// ── Config ────────────────────────────────────────────────────────────────────
const DARK     = {'true' if dark_mode else 'false'};
const SHOW_TRI = {SHOW_TRI};
const SHOW_GRID= {SHOW_GRID};
let   R        = {R};
const MARGIN   = 40; // keep P inside canvas minus this border

const CLR = {{
  bg:          '{BG}',
  grid:        DARK ? 'rgba(255,255,255,0.032)' : 'rgba(0,0,0,0.04)',
  gridMajor:   DARK ? 'rgba(255,255,255,0.065)' : 'rgba(0,0,0,0.08)',
  axis:        DARK ? 'rgba(255,255,255,0.08)'  : 'rgba(0,0,0,0.1)',
  axisLabel:   DARK ? 'rgba(255,255,255,0.2)'   : 'rgba(0,0,0,0.25)',
  circle:      DARK ? 'rgba(255,255,255,0.6)'   : 'rgba(0,0,0,0.6)',
  circleFill:  DARK ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
  chord1:      '#5b9cf6',
  chord2:      '#f0855b',
  tangent:     '#c8f060',
  ptP:         '#c8f060',
  text:        '{TEXT_CLR}',
  muted:       '{MUTED}',
  scratch:     '{BG}',
  tri1:        'rgba(91,156,246,0.08)',
  tri2:        'rgba(240,133,91,0.08)',
  segPulse:    'rgba(200,240,96,0.55)',
}};

// ── Canvas / layout ───────────────────────────────────────────────────────────
const cv  = document.getElementById('cv');
const ctx = cv.getContext('2d');
let W, H, CX, CY, dpr;

function resize() {{
  const box = document.getElementById('canvas-box');
  W = box.clientWidth; H = box.clientHeight;
  dpr = window.devicePixelRatio || 1;
  cv.width  = W * dpr; cv.height = H * dpr;
  cv.style.width = W + 'px'; cv.style.height = H + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  CX = W / 2; CY = H / 2;
}}

// ── State ─────────────────────────────────────────────────────────────────────
let angle1 = 0.45, angle2 = 2.05;
let dragging = null;
let animState = null; // animation controller
const pts = {{ P:null, A:null, B:null, C:null, D:null }};

// Math coords: 1 unit = SCALE px
const SCALE = 40;
function toMath(px, py)  {{ return [+(( px-CX)/SCALE).toFixed(2), +((-py+CY)/SCALE).toFixed(2)]; }}

// ── Geometry ──────────────────────────────────────────────────────────────────
function circleHits(px, py, dx, dy) {{
  const fx=px-CX, fy=py-CY;
  const a=dx*dx+dy*dy, b=2*(fx*dx+fy*dy), c=fx*fx+fy*fy-R*R;
  const disc=b*b-4*a*c;
  if (disc < 0) return null;
  const sq=Math.sqrt(disc);
  const t1=(-b-sq)/(2*a), t2=(-b+sq)/(2*a);
  return [{{x:px+dx*t1,y:py+dy*t1}}, {{x:px+dx*t2,y:py+dy*t2}}];
}}

function recomputeChords() {{
  const {{x:px, y:py}} = pts.P;
  const h1=circleHits(px,py,Math.cos(angle1),Math.sin(angle1));
  const h2=circleHits(px,py,Math.cos(angle2),Math.sin(angle2));
  if (h1) {{ pts.A=h1[0]; pts.B=h1[1]; }}
  if (h2) {{ pts.C=h2[0]; pts.D=h2[1]; }}
}}

function snapToCircle(x, y) {{
  const dx=x-CX, dy=y-CY, d=Math.sqrt(dx*dx+dy*dy)||1;
  return {{x:CX+dx/d*R, y:CY+dy/d*R}};
}}

function dist(a,b) {{ return Math.sqrt((a.x-b.x)**2+(a.y-b.y)**2); }}

function clampP(x, y) {{
  return {{
    x: Math.max(MARGIN, Math.min(W-MARGIN, x)),
    y: Math.max(MARGIN, Math.min(H-MARGIN, y)),
  }};
}}

function getMode() {{
  const d = dist(pts.P, {{x:CX,y:CY}});
  if (Math.abs(d - R) < 6) return 'tangent';
  return d < R ? 'inside' : 'outside';
}}

// ── Grid drawing ──────────────────────────────────────────────────────────────
function drawGrid() {{
  if (!SHOW_GRID) return;
  const minor=SCALE, major=SCALE*5;

  ctx.lineWidth=0.6;
  ctx.strokeStyle=CLR.grid;
  for (let x=(CX%minor+minor)%minor; x<W; x+=minor) {{
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
  }}
  for (let y=(CY%minor+minor)%minor; y<H; y+=minor) {{
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
  }}

  ctx.lineWidth=0.8;
  ctx.strokeStyle=CLR.gridMajor;
  for (let x=(CX%major+major)%major; x<W; x+=major) {{
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
  }}
  for (let y=(CY%major+major)%major; y<H; y+=major) {{
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
  }}

  // axes
  ctx.strokeStyle=CLR.axis; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(CX,0); ctx.lineTo(CX,H); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(0,CY); ctx.lineTo(W,CY); ctx.stroke();

  // axis labels
  ctx.fillStyle=CLR.axisLabel;
  ctx.font='9px "JetBrains Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  for (let u=-10; u<=10; u++) {{
    if (u===0) continue;
    const px=CX+u*SCALE, py=CY+u*SCALE;
    if (px>10 && px<W-10) ctx.fillText(u, px, CY+4);
    ctx.textAlign='right'; ctx.textBaseline='middle';
    if (py>10 && py<H-10) ctx.fillText(-u, CX-5, py);
    ctx.textAlign='center'; ctx.textBaseline='top';
  }}
  ctx.fillText('O', CX+5, CY+4);
}}

// ── Circle ────────────────────────────────────────────────────────────────────
function drawCircle() {{
  ctx.beginPath(); ctx.arc(CX,CY,R,0,Math.PI*2);
  ctx.fillStyle=CLR.circleFill; ctx.fill();
  ctx.strokeStyle=CLR.circle; ctx.lineWidth=2; ctx.stroke();

  // center
  ctx.beginPath(); ctx.arc(CX,CY,3.5,0,Math.PI*2);
  ctx.fillStyle=CLR.muted; ctx.fill();

  // radius indicator
  ctx.save();
  ctx.strokeStyle=CLR.muted; ctx.lineWidth=0.7;
  ctx.setLineDash([3,5]);
  ctx.beginPath(); ctx.moveTo(CX,CY); ctx.lineTo(CX+R,CY); ctx.stroke();
  ctx.restore();
  ctx.fillStyle=CLR.muted;
  ctx.font='10px "JetBrains Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  const rMath=(R/SCALE).toFixed(1);
  ctx.fillText(`r=${{rMath}}`, CX+R/2, CY-12);
}}

// ── Chord / tangent lines ─────────────────────────────────────────────────────
function drawChord(A, B, color, alpha=1) {{
  if (!A||!B) return;
  ctx.save();
  ctx.globalAlpha=alpha;
  ctx.beginPath(); ctx.moveTo(A.x,A.y); ctx.lineTo(B.x,B.y);
  ctx.strokeStyle=color; ctx.lineWidth=1.8; ctx.stroke();
  ctx.restore();
}}

function drawTangent(P, color) {{
  // tangent is perpendicular to OP at the point on circle
  const dx=P.x-CX, dy=P.y-CY;
  const d=Math.sqrt(dx*dx+dy*dy)||1;
  const tx=-dy/d, ty=dx/d; // tangent direction
  const len=180;
  ctx.save();
  ctx.strokeStyle=color; ctx.lineWidth=1.8;
  ctx.setLineDash([6,5]);
  ctx.beginPath();
  ctx.moveTo(P.x-tx*len, P.y-ty*len);
  ctx.lineTo(P.x+tx*len, P.y+ty*len);
  ctx.stroke();
  ctx.restore();
  // right angle mark
  const s=10;
  const ox=-dx/d*s, oy=-dy/d*s;
  ctx.save();
  ctx.strokeStyle=color+'99'; ctx.lineWidth=1;
  ctx.beginPath();
  ctx.moveTo(P.x+ox, P.y+oy);
  ctx.lineTo(P.x+ox+tx*s, P.y+oy+ty*s);
  ctx.lineTo(P.x+tx*s, P.y+ty*s);
  ctx.stroke();
  ctx.restore();
}}

// ── Similar triangles ─────────────────────────────────────────────────────────
function drawTriangles() {{
  if (!SHOW_TRI||!pts.A||!pts.B||!pts.C||!pts.D) return;
  const P=pts.P;
  [[P,pts.A,pts.D,CLR.tri1,CLR.chord1],[P,pts.C,pts.B,CLR.tri2,CLR.chord2]].forEach(([p1,p2,p3,fill,stroke])=>{{
    ctx.beginPath(); ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y); ctx.lineTo(p3.x,p3.y); ctx.closePath();
    ctx.fillStyle=fill; ctx.fill();
    ctx.save(); ctx.strokeStyle=stroke+'55'; ctx.lineWidth=0.9;
    ctx.setLineDash([4,5]); ctx.stroke(); ctx.restore();
  }});
}}

// ── Segment label ─────────────────────────────────────────────────────────────
function segLabel(p1, p2, txt, color, alpha=1) {{
  const mx=(p1.x+p2.x)/2, my=(p1.y+p2.y)/2;
  const dx=p2.x-p1.x, dy=p2.y-p1.y, ln=Math.sqrt(dx*dx+dy*dy)||1;
  const nx=-dy/ln*14, ny=dx/ln*14;
  ctx.save(); ctx.globalAlpha=alpha;
  ctx.font='10px "JetBrains Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillStyle=CLR.scratch+'cc'; ctx.fillText(txt,mx+nx,my+ny);
  ctx.fillStyle=color;             ctx.fillText(txt,mx+nx,my+ny);
  ctx.restore();
}}

// ── Distance line ─────────────────────────────────────────────────────────────
function drawDistLine() {{
  const P=pts.P;
  ctx.save(); ctx.strokeStyle=CLR.ptP+'30'; ctx.lineWidth=1;
  ctx.setLineDash([4,6]);
  ctx.beginPath(); ctx.moveTo(CX,CY); ctx.lineTo(P.x,P.y); ctx.stroke();
  ctx.restore();
}}

// ── Point dot ─────────────────────────────────────────────────────────────────
function drawDot(x, y, color, label, r=7, alpha=1) {{
  ctx.save(); ctx.globalAlpha=alpha;
  // glow
  ctx.beginPath(); ctx.arc(x,y,r+6,0,Math.PI*2);
  ctx.fillStyle=color+'15'; ctx.fill();
  // body
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2);
  ctx.fillStyle=color; ctx.fill();
  ctx.strokeStyle=CLR.scratch; ctx.lineWidth=2; ctx.stroke();
  // label
  ctx.fillStyle=CLR.text; ctx.font='500 11px "JetBrains Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='bottom';
  ctx.fillText(label, x, y-r-5);
  ctx.restore();
}}

// ── Coord label near point ────────────────────────────────────────────────────
function coordLabel(pt, color) {{
  const [mx, my] = toMath(pt.x, pt.y);
  ctx.font='9px "JetBrains Mono",monospace';
  ctx.fillStyle=color+'aa';
  ctx.textAlign='center'; ctx.textBaseline='top';
  ctx.fillText(`(${{mx}},${{my}})`, pt.x, pt.y+10);
}}

// ── Stats panel ───────────────────────────────────────────────────────────────
function updateStats() {{
  const P=pts.P;
  const d=dist(P,{{x:CX,y:CY}});
  const mode=getMode();
  const power=Math.abs(d*d-R*R);

  const pill=document.getElementById('pill');
  pill.className=mode;
  document.getElementById('mode-txt').textContent=
    mode==='inside'?'Inside':mode==='tangent'?'Tangent':'Outside';

  document.getElementById('v-d').textContent  = (d/SCALE).toFixed(2);
  document.getElementById('v-pow').textContent= (power/SCALE/SCALE).toFixed(3);

  if (mode==='tangent') {{
    document.getElementById('v-ab').textContent='PT²';
    document.getElementById('v-cd').textContent=(power/SCALE/SCALE).toFixed(3);
    document.getElementById('v-delta').textContent='0.000';
    document.getElementById('v-delta').className='val good';
    return;
  }}

  if (pts.A&&pts.B&&pts.C&&pts.D) {{
    const ab=dist(P,pts.A)*dist(P,pts.B);
    const cd=dist(P,pts.C)*dist(P,pts.D);
    const delta=Math.abs(ab-cd);
    document.getElementById('v-ab').textContent=(ab/SCALE/SCALE).toFixed(3);
    document.getElementById('v-cd').textContent=(cd/SCALE/SCALE).toFixed(3);
    const dEl=document.getElementById('v-delta');
    dEl.textContent=(delta/SCALE/SCALE).toFixed(4);
    dEl.className='val '+(delta<1.5?'good':delta<8?'warn':'bad');
  }}
}}

// ── Main draw ─────────────────────────────────────────────────────────────────
function draw() {{
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle=CLR.bg; ctx.fillRect(0,0,W,H);

  drawGrid();
  drawCircle();
  drawDistLine();

  const mode=getMode();

  if (mode==='tangent') {{
    // snap P exactly to circle for clean display
    const snapped=snapToCircle(pts.P.x,pts.P.y);
    drawTangent(snapped, CLR.tangent);
    // draw second chord normally
    drawChord(pts.C,pts.D,CLR.chord2);
    if(pts.C&&pts.D) {{
      segLabel(snapped,pts.C,'PC',CLR.chord2);
      segLabel(snapped,pts.D,'PD',CLR.chord2);
    }}
    drawDot(snapped.x,snapped.y,CLR.tangent,'T',8);
    coordLabel(snapped, CLR.tangent);
  }} else {{
    if(SHOW_TRI) drawTriangles();
    drawChord(pts.A,pts.B,CLR.chord1);
    drawChord(pts.C,pts.D,CLR.chord2);
    if(pts.A&&pts.B&&pts.C&&pts.D) {{
      const P=pts.P;
      segLabel(P,pts.A,'PA',CLR.chord1);
      segLabel(P,pts.B,'PB',CLR.chord1);
      segLabel(P,pts.C,'PC',CLR.chord2);
      segLabel(P,pts.D,'PD',CLR.chord2);
    }}
    if(pts.A) drawDot(pts.A.x,pts.A.y,CLR.chord1,'A',6);
    if(pts.B) drawDot(pts.B.x,pts.B.y,CLR.chord1,'B',6);
    if(pts.C) drawDot(pts.C.x,pts.C.y,CLR.chord2,'C',6);
    if(pts.D) drawDot(pts.D.x,pts.D.y,CLR.chord2,'D',6);
    drawDot(pts.P.x,pts.P.y,CLR.ptP,'P',9);
    coordLabel(pts.P, CLR.ptP);
  }}

  updateStats();
}}

// ── Animated proof ────────────────────────────────────────────────────────────
/*
  Steps:
  0  fade in circle + P
  1  draw chord AB, label PA PB, flash product
  2  draw chord CD, label PC PD, flash product
  3  highlight that PA·PB = PC·PD, pulse both
  4  show "= |d²−r²|", flash power value
*/
let animRAF = null;

function easeInOut(t) {{ return t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2; }}

function startAnimation() {{
  if (animRAF) {{ cancelAnimationFrame(animRAF); animRAF=null; }}
  resetAll(false); // reset without redraw

  const btn=document.getElementById('anim-btn');
  btn.textContent='■ Stop';
  btn.onclick=stopAnimation;

  const steps=[
    {{dur:600,  label:'Drawing circle…'}},
    {{dur:900,  label:'Chord AB through P…'}},
    {{dur:900,  label:'PA · PB = ?'}},
    {{dur:900,  label:'Chord CD through P…'}},
    {{dur:900,  label:'PC · PD = ?'}},
    {{dur:1200, label:'PA·PB = PC·PD — the invariant!'}},
    {{dur:1000, label:'Both equal |d² − r²|'}},
    {{dur:600,  label:'Done ✓'}},
  ];

  let step=0, stepStart=null;

  function frame(ts) {{
    if (!stepStart) stepStart=ts;
    const elapsed=ts-stepStart;
    const s=steps[step];
    const t=Math.min(elapsed/s.dur, 1);
    const et=easeInOut(t);

    ctx.clearRect(0,0,W,H);
    ctx.fillStyle=CLR.bg; ctx.fillRect(0,0,W,H);
    drawGrid();

    // always draw circle
    ctx.globalAlpha = step>=1 ? 1 : et;
    drawCircle();
    ctx.globalAlpha=1;

    const P=pts.P;

    if (step>=1) {{
      // chord 1
      const alpha = step===1 ? et : 1;
      drawChord(pts.A,pts.B,CLR.chord1, alpha);
      if(pts.A) drawDot(pts.A.x,pts.A.y,CLR.chord1,'A',6,alpha);
      if(pts.B) drawDot(pts.B.x,pts.B.y,CLR.chord1,'B',6,alpha);
    }}
    if (step>=2) {{
      const pulse = step===2 ? 0.5+0.5*Math.sin(elapsed/120) : 1;
      segLabel(P,pts.A,'PA',CLR.chord1, pulse);
      segLabel(P,pts.B,'PB',CLR.chord1, pulse);
      // product box
      if (pts.A&&pts.B) {{
        const ab=(dist(P,pts.A)*dist(P,pts.B)/SCALE/SCALE).toFixed(2);
        const bx=P.x+30, by=P.y-50;
        ctx.save();
        ctx.globalAlpha=step===2?et:1;
        ctx.fillStyle=CLR.chord1+'22';
        roundRect(ctx,bx-4,by-14,120,22,6); ctx.fill();
        ctx.strokeStyle=CLR.chord1+'55'; ctx.lineWidth=0.8; ctx.stroke();
        ctx.fillStyle=CLR.chord1; ctx.font='600 11px "JetBrains Mono",monospace';
        ctx.textAlign='left'; ctx.textBaseline='middle';
        ctx.fillText(`PA·PB = ${{ab}}`, bx, by-3);
        ctx.restore();
      }}
    }}
    if (step>=3) {{
      const alpha=step===3?et:1;
      drawChord(pts.C,pts.D,CLR.chord2,alpha);
      if(pts.C) drawDot(pts.C.x,pts.C.y,CLR.chord2,'C',6,alpha);
      if(pts.D) drawDot(pts.D.x,pts.D.y,CLR.chord2,'D',6,alpha);
    }}
    if (step>=4) {{
      const pulse=step===4?0.5+0.5*Math.sin(elapsed/120):1;
      segLabel(P,pts.C,'PC',CLR.chord2,pulse);
      segLabel(P,pts.D,'PD',CLR.chord2,pulse);
      if(pts.C&&pts.D) {{
        const cd=(dist(P,pts.C)*dist(P,pts.D)/SCALE/SCALE).toFixed(2);
        const bx=P.x+30, by=P.y-24;
        ctx.save(); ctx.globalAlpha=step===4?et:1;
        ctx.fillStyle=CLR.chord2+'22';
        roundRect(ctx,bx-4,by-14,120,22,6); ctx.fill();
        ctx.strokeStyle=CLR.chord2+'55'; ctx.lineWidth=0.8; ctx.stroke();
        ctx.fillStyle=CLR.chord2; ctx.font='600 11px "JetBrains Mono",monospace';
        ctx.textAlign='left'; ctx.textBaseline='middle';
        const ab=(dist(P,pts.A)*dist(P,pts.B)/SCALE/SCALE).toFixed(2);
        ctx.fillText(`PC·PD = ${{cd}}`, bx, by-3);
        ctx.restore();
      }}
    }}
    if (step>=5) {{
      // flash equality
      const pulse=0.6+0.4*Math.sin(elapsed/150);
      const cx2=P.x+30, cy2=P.y-72;
      ctx.save(); ctx.globalAlpha=(step===5?et:1)*pulse;
      ctx.fillStyle=CLR.ptP+'25';
      roundRect(ctx,cx2-4,cy2-14,200,22,6); ctx.fill();
      ctx.strokeStyle=CLR.ptP+'60'; ctx.lineWidth=1; ctx.stroke();
      ctx.fillStyle=CLR.ptP; ctx.font='600 11px "JetBrains Mono",monospace';
      ctx.textAlign='left'; ctx.textBaseline='middle';
      const ab=(dist(P,pts.A)*dist(P,pts.B)/SCALE/SCALE).toFixed(2);
      ctx.fillText(`PA·PB = PC·PD = ${{ab}}`, cx2, cy2-3);
      ctx.restore();
    }}
    if (step>=6) {{
      const d=dist(P,{{x:CX,y:CY}});
      const power=(Math.abs(d*d-R*R)/SCALE/SCALE).toFixed(2);
      const cx2=P.x+30, cy2=P.y-96;
      ctx.save(); ctx.globalAlpha=step===6?et:1;
      ctx.fillStyle='rgba(200,240,96,0.1)';
      roundRect(ctx,cx2-4,cy2-14,200,22,6); ctx.fill();
      ctx.strokeStyle='rgba(200,240,96,0.4)'; ctx.lineWidth=1; ctx.stroke();
      ctx.fillStyle='#c8f060'; ctx.font='600 11px "JetBrains Mono",monospace';
      ctx.textAlign='left'; ctx.textBaseline='middle';
      ctx.fillText(`= |d²−r²| = ${{power}}`, cx2, cy2-3);
      ctx.restore();
    }}

    // P always on top
    drawDistLine();
    drawDot(P.x,P.y,CLR.ptP,'P',9);

    updateStats();

    if (t>=1) {{
      step++;
      stepStart=ts;
      if (step>=steps.length) {{ stopAnimation(); return; }}
    }}
    animRAF=requestAnimationFrame(frame);
  }}
  animRAF=requestAnimationFrame(frame);
}}

function stopAnimation() {{
  if (animRAF) {{ cancelAnimationFrame(animRAF); animRAF=null; }}
  const btn=document.getElementById('anim-btn');
  btn.textContent='▶ Animate proof';
  btn.onclick=startAnimation;
  draw();
}}

function roundRect(ctx, x, y, w, h, r) {{
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.arcTo(x+w,y,x+w,y+r,r);
  ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
  ctx.lineTo(x+r,y+h);   ctx.arcTo(x,y+h,x,y+h-r,r);
  ctx.lineTo(x,y+r);     ctx.arcTo(x,y,x+r,y,r);
  ctx.closePath();
}}

// ── Tooltip ───────────────────────────────────────────────────────────────────
const tip=document.getElementById('tooltip');
const TIPS={{
  P: `<b>P</b> — the power point<br>
      Power = |d²−r²|<br>
      <span class="dim">Drag anywhere. Cross the circle<br>boundary to switch cases.</span>`,
  A: `<b>A</b> — chord 1 endpoint<br><span class="dim">Constrained to circle.<br>Dragging rotates chord AB around P.</span>`,
  B: `<b>B</b> — chord 1 endpoint<br><span class="dim">Opposite end of chord AB.</span>`,
  C: `<b>C</b> — chord 2 endpoint<br><span class="dim">Constrained to circle.<br>Dragging rotates chord CD around P.</span>`,
  D: `<b>D</b> — chord 2 endpoint<br><span class="dim">Opposite end of chord CD.</span>`,
}};
let tipTarget=null, tipTimer=null;

function showTip(key, x, y) {{
  if (!TIPS[key]) return;
  if (tipTarget===key) return;
  tipTarget=key;
  clearTimeout(tipTimer);
  tip.innerHTML=TIPS[key];
  const bx=document.getElementById('canvas-box').getBoundingClientRect();
  const tx=Math.min(x+14, W-230);
  const ty=Math.max(y-60, 10);
  tip.style.left=tx+'px'; tip.style.top=ty+'px';
  tip.classList.add('visible');
}}
function hideTip() {{
  tipTarget=null;
  clearTimeout(tipTimer);
  tipTimer=setTimeout(()=>tip.classList.remove('visible'),200);
}}

// ── Drag ──────────────────────────────────────────────────────────────────────
const HIT=18;

function getPos(e) {{
  const rect=cv.getBoundingClientRect();
  const src=e.touches?e.touches[0]:e;
  return {{
    x:(src.clientX-rect.left)*(W/rect.width),
    y:(src.clientY-rect.top) *(H/rect.height),
  }};
}}

function hitTest(x, y) {{
  for (const k of ['P','A','B','C','D']) {{
    const p=pts[k]; if(!p) continue;
    if (dist({{x,y}},p)<HIT) return k;
  }}
  return null;
}}

cv.addEventListener('mousedown', e=>{{
  if (animRAF) return;
  e.preventDefault();
  const pos=getPos(e);
  const hit=hitTest(pos.x,pos.y);
  if (hit) {{ dragging=hit; }}
  else {{
    pts.P=clampP(pos.x,pos.y);
    recomputeChords(); draw();
  }}
}});

cv.addEventListener('mousemove', e=>{{
  e.preventDefault();
  const pos=getPos(e);
  const hit=hitTest(pos.x,pos.y);
  if (!dragging) {{
    cv.style.cursor=hit?'grab':'crosshair';
    if (hit) showTip(hit,pos.x,pos.y);
    else hideTip();
    return;
  }}
  cv.style.cursor='grabbing';
  if (dragging==='P') {{
    pts.P=clampP(pos.x,pos.y);
    recomputeChords();
  }} else {{
    const sn=snapToCircle(pos.x,pos.y);
    if (dragging==='A'||dragging==='B') {{
      angle1=Math.atan2(sn.y-pts.P.y, sn.x-pts.P.x);
      recomputeChords(); pts[dragging]=sn;
    }} else {{
      angle2=Math.atan2(sn.y-pts.P.y, sn.x-pts.P.x);
      recomputeChords(); pts[dragging]=sn;
    }}
  }}
  draw();
}});

cv.addEventListener('mouseup',    ()=>{{dragging=null;}});
cv.addEventListener('mouseleave', ()=>{{dragging=null; hideTip();}});

cv.addEventListener('touchstart', e=>{{
  e.preventDefault();
  const pos=getPos(e);
  dragging=hitTest(pos.x,pos.y);
  if (!dragging) {{ pts.P=clampP(pos.x,pos.y); recomputeChords(); draw(); }}
}},{{passive:false}});
cv.addEventListener('touchmove', e=>{{
  e.preventDefault();
  if (!dragging) return;
  const pos=getPos(e);
  if (dragging==='P') {{ pts.P=clampP(pos.x,pos.y); recomputeChords(); }}
  else {{
    const sn=snapToCircle(pos.x,pos.y);
    if (dragging==='A'||dragging==='B') {{
      angle1=Math.atan2(sn.y-pts.P.y,sn.x-pts.P.x);
      recomputeChords(); pts[dragging]=sn;
    }} else {{
      angle2=Math.atan2(sn.y-pts.P.y,sn.x-pts.P.x);
      recomputeChords(); pts[dragging]=sn;
    }}
  }}
  draw();
}},{{passive:false}});
cv.addEventListener('touchend', ()=>{{dragging=null;}});

// ── Keyboard shortcuts ────────────────────────────────────────────────────────
document.addEventListener('keydown', e=>{{
  if (e.key==='r'||e.key==='R') resetAll();
  if (e.key==='t'||e.key==='T') {{
    // toggle triangles in JS (sidebar already off)
  }}
  if (e.key===' ') {{ e.preventDefault(); /* cycle mode placeholder */ }}
}});

// ── Reset ─────────────────────────────────────────────────────────────────────
function resetAll(redraw=true) {{
  angle1=0.45; angle2=2.05;
  pts.P={{x:CX+Math.round(R*1.45), y:CY+22}};
  recomputeChords();
  if (redraw) draw();
}}

// ── Init ──────────────────────────────────────────────────────────────────────
function boot() {{
  resize(); resetAll();
}}

window.addEventListener('resize', ()=>{{
  resize();
  if (pts.P) {{
    pts.P=clampP(pts.P.x,pts.P.y);
    recomputeChords();
  }}
  draw();
}});

boot();
</script>
</body>
</html>"""

components.html(html, height=660, scrolling=False)

# ── Proof section ─────────────────────────────────────────────────────────────
if show_proof:
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Case 1 — Chords (P inside)")
        st.markdown(r"""
$\triangle PAD \sim \triangle PCB$ because:
- $\angle APD = \angle CPB$ (vertical angles)
- $\angle DAP = \angle BCP$ (same arc $DB$)

$$\frac{PA}{PC} = \frac{PD}{PB}$$
$$\boxed{PA \cdot PB = PC \cdot PD = r^2 - d^2}$$
        """)
    with c2:
        st.markdown("#### Case 2 — Secants (P outside)")
        st.markdown(r"""
$\triangle PAD \sim \triangle PCB$ because:
- $\angle P$ is shared
- $\angle PAD = \angle PCB$ (same arc $BD$)

$$\frac{PA}{PC} = \frac{PD}{PB}$$
$$\boxed{PA \cdot PB = PC \cdot PD = d^2 - r^2}$$
        """)
    with c3:
        st.markdown("#### Case 3 — Tangent (P on circle)")
        st.markdown(r"""
When chord $AB$ collapses to a tangent at $T$:

$$PA = PB = PT \implies PT^2 = PA \cdot PB$$

$$\boxed{PT^2 = d^2 - r^2}$$

As $P \to$ circle, power $\to 0$, tangent length $\to 0$.
        """)
