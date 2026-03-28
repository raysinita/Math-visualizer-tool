import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Power of a Point", layout="wide")

st.title("Power of a Point")
st.markdown("Drag the sliders to move point **P** and watch **PA · PB = PC · PD** hold invariant.")

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    R = st.slider("Circle radius", 1.0, 5.0, 3.0, 0.1)
    px = st.slider("Point P — x", -8.0, 8.0, 4.5, 0.05)
    py = st.slider("Point P — y", -8.0, 8.0, 0.5, 0.05)
    angle1_deg = st.slider("Chord 1 angle (°)", 0, 170, 25, 1)
    angle2_deg = st.slider("Chord 2 angle (°)", 0, 170, 110, 1)
    st.divider()
    show_similar = st.checkbox("Show similar triangles", value=False)
    show_proof   = st.checkbox("Show proof sketch", value=False)

# ── Geometry helpers ──────────────────────────────────────────────────────────
def chord_intersect(px, py, angle_deg, R):
    """Return two circle-intersection points for the line through (px,py) at angle."""
    dx, dy = np.cos(np.radians(angle_deg)), np.sin(np.radians(angle_deg))
    a = dx**2 + dy**2
    b = 2*(px*dx + py*dy)
    c = px**2 + py**2 - R**2
    disc = b**2 - 4*a*c
    if disc < 0:
        return None, None
    sq = np.sqrt(disc)
    t1, t2 = (-b - sq)/(2*a), (-b + sq)/(2*a)
    A = np.array([px + dx*t1, py + dy*t1])
    B = np.array([px + dx*t2, py + dy*t2])
    return A, B

def seg_len(P, Q):
    return np.linalg.norm(np.array(P) - np.array(Q))

# ── Compute geometry ──────────────────────────────────────────────────────────
P = np.array([px, py])
inside = px**2 + py**2 < R**2

A, B = chord_intersect(px, py, angle1_deg, R)
C, D = chord_intersect(px, py, angle2_deg, R)

valid = A is not None and C is not None

power = abs(px**2 + py**2 - R**2)

if valid:
    PA = seg_len(P, A); PB = seg_len(P, B)
    PC = seg_len(P, C); PD = seg_len(P, D)
    prod_AB = PA * PB
    prod_CD = PC * PD
    # Use signed products for inside case (t1*t2 is negative inside, abs gives power)
    # For display always show absolute values
    match_pct = 100 * (1 - abs(prod_AB - prod_CD) / max(prod_AB, 1e-9))

# ── Metric cards ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    mode = "Inside circle" if inside else "Outside circle"
    st.metric("Mode", mode)
with col2:
    st.metric("Power of P  |d²−r²|", f"{power:.3f}")
with col3:
    if valid:
        st.metric("PA · PB", f"{prod_AB:.3f}")
with col4:
    if valid:
        delta = prod_CD - prod_AB
        st.metric("PC · PD", f"{prod_CD:.3f}", delta=f"{delta:+.4f}", delta_color="off")

# ── Build Plotly figure ───────────────────────────────────────────────────────
fig = go.Figure()

fig.update_layout(
    height=580,
    margin=dict(l=10, r=10, t=10, b=10),
    showlegend=True,
    legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(
        range=[-9, 9], scaleanchor="y", scaleratio=1,
        gridcolor="#e8e8e8", zerolinecolor="#cccccc",
        title="x"
    ),
    yaxis=dict(
        range=[-9, 9],
        gridcolor="#e8e8e8", zerolinecolor="#cccccc",
        title="y"
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
)

# Circle
theta = np.linspace(0, 2*np.pi, 400)
fig.add_trace(go.Scatter(
    x=R*np.cos(theta), y=R*np.sin(theta),
    mode="lines",
    line=dict(color="#1D9E75", width=2.5),
    name="Circle",
    hoverinfo="skip"
))

# Center
fig.add_trace(go.Scatter(
    x=[0], y=[0], mode="markers",
    marker=dict(color="#1D9E75", size=6, symbol="circle"),
    name="Center O", hovertemplate="O (0, 0)"
))

# Radius label
fig.add_annotation(x=R/2, y=0.15, text=f"r = {R:.1f}", showarrow=False,
                   font=dict(size=12, color="#1D9E75"))

if valid:
    # Chord 1 (blue)  A–B
    fig.add_trace(go.Scatter(
        x=[A[0], B[0]], y=[A[1], B[1]],
        mode="lines",
        line=dict(color="#185FA5", width=2),
        name="Chord AB",
        hoverinfo="skip"
    ))
    # Chord 2 (red)  C–D
    fig.add_trace(go.Scatter(
        x=[C[0], D[0]], y=[C[1], D[1]],
        mode="lines",
        line=dict(color="#993C1D", width=2),
        name="Chord CD",
        hoverinfo="skip"
    ))

    # Segment labels along chords
    def midpt(P, Q, t=0.5):
        return (P + Q*t*(1-t))  # just use lerp

    for pts, label, color in [
        ((P, A), "PA", "#185FA5"),
        ((P, B), "PB", "#185FA5"),
        ((P, C), "PC", "#993C1D"),
        ((P, D), "PD", "#993C1D"),
    ]:
        mid = (pts[0] + pts[1]) / 2
        fig.add_annotation(
            x=mid[0], y=mid[1],
            text=label,
            showarrow=False,
            font=dict(size=11, color=color),
            bgcolor="rgba(255,255,255,0.7)",
            borderpad=2
        )

    # Intersection points A, B, C, D
    for pt, lbl, col in [(A,"A","#185FA5"),(B,"B","#185FA5"),
                          (C,"C","#993C1D"),(D,"D","#993C1D")]:
        fig.add_trace(go.Scatter(
            x=[pt[0]], y=[pt[1]],
            mode="markers+text",
            marker=dict(color=col, size=9),
            text=[lbl], textposition="top right",
            textfont=dict(size=13, color=col),
            showlegend=False,
            hovertemplate=f"{lbl} ({pt[0]:.2f}, {pt[1]:.2f})"
        ))

    # Similar triangles overlay
    if show_similar and inside:
        # Draw triangles PAD and PCB (similar triangles proof)
        tri1_x = [P[0], A[0], D[0], P[0]]
        tri1_y = [P[1], A[1], D[1], P[1]]
        tri2_x = [P[0], C[0], B[0], P[0]]
        tri2_y = [P[1], C[1], B[1], P[1]]
        fig.add_trace(go.Scatter(x=tri1_x, y=tri1_y, fill="toself",
            fillcolor="rgba(24,95,165,0.1)", line=dict(color="#185FA5", width=1, dash="dot"),
            name="△PAD", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=tri2_x, y=tri2_y, fill="toself",
            fillcolor="rgba(153,60,29,0.1)", line=dict(color="#993C1D", width=1, dash="dot"),
            name="△PCB", hoverinfo="skip"))

# Point P
p_color = "#534AB7"
fig.add_trace(go.Scatter(
    x=[px], y=[py],
    mode="markers+text",
    marker=dict(color=p_color, size=13, line=dict(color="#3C3489", width=2)),
    text=["P"], textposition="top right",
    textfont=dict(size=14, color=p_color),
    name="Point P",
    hovertemplate=f"P ({px:.2f}, {py:.2f})<br>d = {np.sqrt(px**2+py**2):.3f}"
))

# Distance line from O to P
fig.add_trace(go.Scatter(
    x=[0, px], y=[0, py],
    mode="lines",
    line=dict(color=p_color, width=1, dash="dot"),
    name=f"d = {np.sqrt(px**2+py**2):.2f}",
    hoverinfo="skip"
))

# Power invariant annotation box
if valid:
    fig.add_annotation(
        x=0.98, y=0.02,
        xref="paper", yref="paper",
        xanchor="right", yanchor="bottom",
        text=(
            f"<b>PA · PB</b> = {prod_AB:.3f}<br>"
            f"<b>PC · PD</b> = {prod_CD:.3f}<br>"
            f"<b>Power</b> = {power:.3f}<br>"
            f"Match: {match_pct:.2f}%"
        ),
        showarrow=False,
        bgcolor="rgba(238,237,254,0.95)",
        bordercolor="#534AB7",
        borderwidth=1,
        font=dict(size=12, color="#3C3489"),
        align="left"
    )

st.plotly_chart(fig, use_container_width=True)

# ── Proof sketch ──────────────────────────────────────────────────────────────
if show_proof:
    st.divider()
    if inside:
        st.subheader("Proof — intersecting chords (P inside)")
        st.markdown(r"""
Triangles **△PAD** and **△PCB** are similar because:
- ∠APD = ∠CPB (vertical angles)
- ∠DAP = ∠BCP (both inscribed in the same arc DB)

From similarity: $\dfrac{PA}{PC} = \dfrac{PD}{PB}$

Cross-multiplying: $PA \cdot PB = PC \cdot PD$

This common value equals $r^2 - d^2$ where $d = |OP|$.
        """)
    else:
        st.subheader("Proof — secant-secant (P outside)")
        st.markdown(r"""
Triangles **△PAD** and **△PCB** are similar because:
- ∠P is shared
- ∠PAD = ∠PCB (both subtend arc BD, same side)

From similarity: $\dfrac{PA}{PC} = \dfrac{PD}{PB}$

Cross-multiplying: $PA \cdot PB = PC \cdot PD$

This common value equals $d^2 - r^2$ where $d = |OP|$.

Special case — **tangent**: when the chord collapses to a tangent point T, $PT^2 = d^2 - r^2$.
        """)

# ── Explore more ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Explore")
ec1, ec2, ec3 = st.columns(3)
with ec1:
    st.info("**Move P to the circle boundary**\nPower → 0, products → 0")
with ec2:
    st.info("**Rotate both chord angles together**\nProducts stay equal — that's the theorem")
with ec3:
    st.info("**Set P at origin**\nPA · PB = r² for every chord through center")
