"""Illustrative figures for visual review; no consumer data or device model.

Geometry and analytic rotations belong to these named examples. Appearance
choices are candidates, not an accepted Embla API.
"""

import math
import plotly.graph_objects as go
from design import SEQUENCES, CHROME, apply_layout

def appearance(fig, style, dark, kind="cartesian"):
    if style == "default":
        fig.update_layout(template="plotly")
        return fig
    return apply_layout(fig, "dark" if dark else "light", kind=kind)


def pulse(style="reference", dark=True):
    """Schematic normalized frequency tracks; a 40 ns interaction window."""
    fig = go.Figure()
    for label, idle, active in [("Coupler", 2.7, 2.2), ("Qᵢ", 1.7, 1.1), ("Qⱼ", 1.1, 1.1)]:
        fig.add_trace(go.Scatter(x=[0, 20, 20, 60, 60, 100],
            y=[idle, idle, active, active, idle, idle], mode="lines", name=label,
            line=dict(width=3), hovertemplate=label + "<br>t = %{x} ns<extra></extra>"))
    fig.add_vrect(x0=20, x1=60, fillcolor="#7BAED0", opacity=.12, line_width=0)
    fig.add_annotation(x=40, y=3.15, text="Interaction · 40 ns", showarrow=False)
    fig.update_layout(height=350, hovermode="x unified", meta=dict(embla_kind="pulse"))
    fig.update_xaxes(title="Time (ns)", range=[0, 100])
    fig.update_yaxes(title="Frequency · schematic", showticklabels=False, range=[.7, 3.4])
    return appearance(fig, style, dark, kind="pulse")


def bloch(style="reference", dark=True, axes=False):
    """Ideal Rₓ(α)|0⟩: Bloch vector (0, −sin α, cos α)."""
    fig = go.Figure()
    angles = [2 * math.pi * i / 96 for i in range(97)]
    mode = "dark" if dark else "light"
    ink = SEQUENCES[mode][10][1]
    wire = CHROME[mode]["axis"]
    for plane in ("xy", "xz", "yz"):
        coords = {key: [0.0] * len(angles) for key in "xyz"}
        coords[plane[0]] = [math.cos(t) for t in angles]
        coords[plane[1]] = [math.sin(t) for t in angles]
        fig.add_trace(go.Scatter3d(**coords, mode="lines", line=dict(color=wire, width=2),
                                 hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode="lines+text",
        text=["|1⟩", "|0⟩"], textposition="top center", line=dict(color=wire, width=2),
        hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0]*len(angles), y=[-math.sin(t) for t in angles],
        z=[math.cos(t) for t in angles], mode="lines", line=dict(color=ink, width=4),
        hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], mode="lines+markers",
        line=dict(color=ink, width=7), marker=dict(color=ink, size=[3, 7]),
        hoverinfo="skip", showlegend=False))
    frames = []
    for i in range(65):
        alpha = 2 * math.pi * i / 64
        # Keep geometry and slider state in the same native animation frame.
        frames.append(go.Frame(name=str(i), traces=[5], layout=dict(sliders=[dict(active=i)]), data=[go.Scatter3d(
            x=[0, 0], y=[0, -math.sin(alpha)], z=[0, math.cos(alpha)])]))
    fig.frames = frames
    controls = dict(frame=dict(duration=55, redraw=True), transition=dict(duration=0), fromcurrent=True)
    fig.update_layout(height=590, meta=dict(embla_kind="bloch"),
        scene=dict(aspectmode="cube", camera=dict(eye=dict(x=1.35, y=1.1, z=.7))),
        updatemenus=[dict(type="buttons", direction="left", x=0, y=0, xanchor="left", yanchor="top", active=-1, showactive=False,
            buttons=[dict(label="▶ Play", method="animate", args=[None, controls]),
                     dict(label="Ⅱ Pause", method="animate", args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False))])])],
        sliders=[dict(x=.02, len=.96, y=-.12, minorticklen=0,
            currentvalue=dict(prefix="Rotation α: ", suffix="°"),
            steps=[dict(label=str(round(i*360/64)), method="animate", args=[[str(i)],
                dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]) for i in range(65)])])
    appearance(fig, style, dark, kind="three-d")
    if style != "default":
        fig.layout.updatemenus[0].update(bgcolor="#A6CEF1", bordercolor=wire,
            font=dict(color="#111A20"))
        fig.layout.sliders[0].update(bgcolor="#A6CEF1", activebgcolor="#43BDDC", bordercolor=wire)
        fig.update_layout(scene=dict(bgcolor=CHROME[mode]["plot"],
            **{key: dict(visible=axes, range=[-1.15, 1.15], title=key[0],
                        backgroundcolor=CHROME[mode]["plot"],
                        gridcolor=CHROME[mode]["grid"]) for key in ("xaxis", "yaxis", "zaxis")}))
    return fig


def curves(style="reference", dark=True):
    """Analytical envelope family for judging overlapping line colors."""
    fig = go.Figure()
    x = list(range(61))
    for i, tau in enumerate([19, 14, 10, 8, 6, 4]):
        y = [.3*(t/tau)*math.exp(1-t/tau) for t in x]
        colors = SEQUENCES["dark" if dark else "light"][5]
        color = colors[i % len(colors)]
        line = dict(width=2.5)
        if style != "default":
            line["color"] = color
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"τ = {tau}", line=line))
    fig.update_layout(height=400, hovermode="x unified")
    fig.update_xaxes(title="Step N")
    fig.update_yaxes(title="Illustrative envelope")
    return appearance(fig, style, dark)
