"""Review chrome for the documentation figures.

Plotly keeps its own layout. These pages set type, color, and one padding
around the diagram. The sizes are for the review pages only. They are not
an accepted Kit API.
"""

from __future__ import annotations

import math
import random

import plotly.graph_objects as go

FONT = '"Source Sans 3", "PingFang TC", "Noto Sans TC", sans-serif'

# Quarto Design Kit page colors, so a figure is not a white card on the page.
LIGHT = {
    "paper": "#faf8f8",
    "text": "#2b2b2b",
    "muted": "#5e5e5e",
    "axis": "#c8c8c8",
    "grid": "#e5e5e5",
    "colorway": ["#315E7D", "#4F8765", "#A36A43", "#746799", "#427D82", "#A0843D", "#9C5D6A", "#657080"],
}
DARK = {
    "paper": "#161618",
    "text": "#ebebec",
    "muted": "#b8b8b8",
    "axis": "#4a4a4e",
    "grid": "#393639",
    "colorway": ["#7DA9C4", "#86B396", "#C59A77", "#A79CC4", "#81B1B4", "#C3AF70", "#C28B97", "#A7B0BC"],
}

# Quarto Design Kit: body 16px, level-3 heading 18px, level-2 heading 22px.
# Tick numbers follow body. Axis titles follow level 3. The figure title follows level 2.
SCREEN = {"tick": 16, "axis": 18, "legend": 16, "title": 22}
PRINT = {"tick": 16, "axis": 18, "legend": 16, "title": 22}

# Diagram ink to the image edge.
OUTER = 16
STANDOFF = 15
# Empty line-box above the title letters, and ink below the baseline, at 22px.
# The gap under the title uses these so it matches the gap above the letters.
TITLE_LEADING = 8
TITLE_DESCENT = 5
# Colorbar padding between the heatmap and the bar.
COLORBAR_XPAD = 10
# Pixels from the plot edge to the colorbar numbers at that padding.
COLORBAR_BEFORE_TICKS = 53


def apply(fig: go.Figure, *, reading: str, appearance: str) -> go.Figure:
    colors = {"light": LIGHT, "dark": DARK}[appearance]
    metrics = {"screen": SCREEN, "print": PRINT}[reading]
    fig.update_layout(
        font={"family": FONT, "size": metrics["tick"], "color": colors["text"]},
        paper_bgcolor=colors["paper"],
        plot_bgcolor=colors["paper"],
        colorway=colors["colorway"],
        title_font={"family": FONT, "size": metrics["title"], "color": colors["text"]},
        legend_font={"family": FONT, "size": metrics["legend"], "color": colors["text"]},
        hovermode="x unified" if reading == "screen" else False,
        hoverlabel={
            "font": {"family": FONT, "size": metrics["tick"], "color": colors["text"]},
            "bgcolor": colors["paper"],
            "bordercolor": colors["axis"],
        },
    )
    styled_axis = {
        "title_font": {"family": FONT, "size": metrics["axis"], "color": colors["text"]},
        "tickfont": {"family": FONT, "size": metrics["tick"], "color": colors["muted"]},
        "gridcolor": colors["grid"],
        "linecolor": colors["axis"],
        "tickcolor": colors["axis"],
        "zeroline": False,
        "automargin": True,
        "title_standoff": STANDOFF,
    }
    fig.update_xaxes(**styled_axis)
    fig.update_yaxes(**styled_axis)
    _share_origin(fig)
    for trace in fig.data:
        colorbar = getattr(trace, "colorbar", None)
        if colorbar is None:
            continue
        colorbar.tickfont = {"family": FONT, "size": metrics["tick"], "color": colors["muted"]}
        colorbar.xpad = COLORBAR_XPAD
        colorbar.thickness = 30
        if colorbar.title:
            colorbar.title.font = {"family": FONT, "size": metrics["axis"], "color": colors["text"]}
    _frame(fig, metrics)
    fig.update_annotations(font={"family": FONT, "size": metrics["axis"], "color": colors["text"]})
    return fig


def _text_px(text: str, size: int) -> int:
    """Source Sans 3 width. ponytail: average advances, not the real font.

    Ceiling: a much wider glyph, such as CJK, is underestimated and automargin
    then eats OUTER. Upgrade path: measure the font.
    """
    width = 0.0
    for ch in text:
        if ch.isdigit():
            width += 0.50
        elif ch == ".":
            width += 0.25
        elif ch == " ":
            width += 0.28
        elif ch == "/":
            width += 0.33
        elif ch in "()":
            width += 0.35
        else:
            width += 0.53
    return math.ceil(width * size)


def _nice_step(span: float) -> float:
    raw = span / 5 if span else 1
    exp = math.floor(math.log10(raw)) if raw > 0 else 0
    frac = raw / 10**exp
    nice = 1 if frac <= 1 else 2 if frac <= 2 else 5 if frac <= 5 else 10
    return nice * 10**exp


def _fmt_tick(value: float, step: float) -> str:
    if abs(value) < 1e-8:
        value = 0.0
    if step >= 1 and abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    decimals = max(0, -math.floor(math.log10(step))) if step > 0 else 0
    return f"{value:.{decimals}f}"


def _span(fig: go.Figure, axis: str) -> tuple[float, float] | None:
    ax = fig.layout[axis]
    if ax.range is not None:
        return float(ax.range[0]), float(ax.range[1])
    attr = "x" if axis.startswith("x") else "y"
    values: list[float] = []
    for trace in fig.data:
        if getattr(trace, "type", None) == "heatmap":
            values.extend(_numbers(getattr(trace, attr)))
        else:
            values.extend(_numbers(getattr(trace, attr, None)))
    if not values:
        return None
    return min(values), max(values)


def _tick_width(fig: go.Figure, axis: str, size: int) -> int:
    span = _span(fig, axis)
    if span is None:
        return 0
    lo, hi = span
    step = _nice_step(hi - lo)
    start = math.ceil(lo / step - 1e-9) * step
    labels = []
    value = start
    while value <= hi + step * 1e-6 and len(labels) < 12:
        labels.append(_fmt_tick(value, step))
        value += step
    if not labels:
        return 0
    return max(_text_px(label, size) for label in labels)


def _left_ink(fig: go.Figure, metrics: dict) -> int:
    # 4px axis-to-tick, then the tick label, standoff, then the rotated title box.
    ink = 4 + _tick_width(fig, "yaxis", metrics["tick"])
    if fig.layout.yaxis.title and fig.layout.yaxis.title.text:
        ink += STANDOFF + (metrics["axis"] + 6)
    return ink


def _bottom_ink(fig: go.Figure, metrics: dict) -> int:
    ink = 4 + (metrics["tick"] + 5)
    if fig.layout.xaxis.title and fig.layout.xaxis.title.text:
        ink += 9 + (metrics["axis"] + 6)
    return ink


def _legend_names(fig: go.Figure) -> list[str]:
    if fig.layout.showlegend is False:
        return []
    names = []
    for trace in fig.data:
        if getattr(trace, "type", None) == "heatmap":
            continue
        if trace.showlegend is False or not getattr(trace, "name", None):
            continue
        names.append(trace.name)
    return names


def _z_tick_width(trace, size: int) -> int:
    values = [float(item) for row in trace.z for item in row]
    if not values:
        return 0
    lo, hi = min(values), max(values)
    step = _nice_step(hi - lo)
    start = math.ceil(lo / step - 1e-9) * step
    labels = []
    value = start
    while value <= hi + step * 1e-6 and len(labels) < 12:
        labels.append(_fmt_tick(value, step))
        value += step
    if not labels:
        return 0
    return max(_text_px(label, size) for label in labels)


def _place_legend(fig: go.Figure) -> None:
    """Horizontal legend under the plot. Plotly grows the bottom margin when it wraps."""
    if not _legend_names(fig):
        return
    fig.update_layout(legend={
        "orientation": "h",
        "yanchor": "top",
        "y": -0.28,
        "xanchor": "left",
        "x": 0,
        "xref": "paper",
        "yref": "paper",
        "bgcolor": "rgba(0,0,0,0)",
        "borderwidth": 0,
    })


def _right_margin(fig: go.Figure, metrics: dict) -> int:
    stacks = []
    for trace in fig.data:
        if getattr(trace, "type", None) == "heatmap" and trace.showscale is not False:
            stacks.append(_z_tick_width(trace, metrics["tick"]) + COLORBAR_BEFORE_TICKS + OUTER)
    if not stacks:
        stacks.append(_tick_width(fig, "xaxis", metrics["tick"]) // 2 + OUTER)
    return max(stacks)


def _frame(fig: go.Figure, metrics: dict, color: str | None = None) -> None:
    """Pad the diagram ink from the image edge. The modebar is not part of that ink."""
    _place_legend(fig)
    _title_inside(fig, size=metrics["title"], color=color)
    text = fig.layout.title.text if fig.layout.title else None
    title_gap = OUTER + TITLE_LEADING + TITLE_DESCENT
    top = OUTER + metrics["title"] + title_gap if text else OUTER
    fig.update_layout(
        margin={
            "l": _left_ink(fig, metrics) + OUTER,
            "r": _right_margin(fig, metrics),
            "t": top,
            "b": _bottom_ink(fig, metrics) + OUTER,
            "autoexpand": True,
        },
        title_automargin=False,
    )


def _title_inside(fig: go.Figure, *, size: int, color: str | None = None) -> None:
    """Keep the title inside the diagram, above the plot."""
    text = fig.layout.title.text if fig.layout.title else None
    if not text:
        return
    font = {"family": FONT, "size": size, "color": color or fig.layout.title.font.color}
    fig.update_layout(
        title={
            "text": text,
            "font": font,
            "xref": "container",
            "x": 0,
            "xanchor": "left",
            "yref": "paper",
            "y": 1,
            "yanchor": "bottom",
            "pad": {"b": OUTER + TITLE_LEADING + TITLE_DESCENT, "l": OUTER, "t": 0},
        },
    )


def _shot(rng: random.Random, p: float, n: int = 2000) -> float:
    """Gaussian approximation to binomial readout noise, n repetitions."""
    p = min(1.0, max(0.0, p))
    sigma = math.sqrt(p * (1.0 - p) / n)
    return min(1.0, max(0.0, p + rng.gauss(0.0, sigma)))


def _numbers(values) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]


def _share_origin(fig: go.Figure) -> None:
    """If an axis never goes below zero, start it at zero and drop the extra zero line."""
    xs: list[float] = []
    ys: list[float] = []
    for trace in fig.data:
        if getattr(trace, "type", None) == "heatmap":
            xs.extend(_numbers(trace.x))
            ys.extend(_numbers(trace.y))
        else:
            xs.extend(_numbers(trace.x))
            ys.extend(_numbers(trace.y))
    fig.update_xaxes(zeroline=False)
    fig.update_yaxes(zeroline=False)
    if xs and min(xs) >= 0:
        fig.update_xaxes(range=[0, max(xs)])
    if ys and min(ys) >= 0:
        hi = max(ys)
        hi = 1 if hi <= 1 else hi * 1.08
        fig.update_yaxes(range=[0, hi])


def for_renderings(draw) -> None:
    """Draw light, then dark. The cell needs `#| renderings: [light, dark]`."""
    for appearance in ("light", "dark"):
        draw(appearance)


def show(fig: go.Figure, *, reading: str, appearance: str) -> go.Figure:
    apply(fig, reading=reading, appearance=appearance)
    config = {"staticPlot": True, "displayModeBar": False} if reading == "print" else {"displaylogo": False}
    fig.show(config=config)
    return fig


def lines() -> go.Figure:
    """Ramsey fringes. P = 1/2 + 1/2 exp(-t/T2*) cos(2π δ t), plus shot noise."""
    rng = random.Random(7)
    t2 = 3.0
    ts = [i * 0.04 for i in range(120)]
    detunings = (0.35, 0.7, 1.15, 1.8)
    fig = go.Figure()
    for delta in detunings:
        ys = []
        for t in ts:
            p = 0.5 + 0.5 * math.exp(-t / t2) * math.cos(2 * math.pi * delta * t)
            ys.append(_shot(rng, p))
        fig.add_trace(go.Scatter(x=ts, y=ys, mode="lines", name=f"δ/2π = {delta} MHz", line={"width": 2}))
    fig.update_layout(title_text="Ramsey")
    fig.update_xaxes(title_text="t (µs)")
    fig.update_yaxes(title_text="P(|1⟩)")
    return fig


def bars() -> go.Figure:
    """Per-qubit coherence summary. Measured values carry cooldown scatter."""
    rng = random.Random(11)
    qubits = ["Q1", "Q2", "Q3", "Q4"]
    t1 = [22.4, 27.1, 18.6, 33.8]
    measured_t1 = [value + rng.gauss(0, 1.4) for value in t1]
    measured_t2 = [min(2 * value, value * 0.62 + rng.gauss(0, 0.8)) for value in t1]
    simulated = [value * 0.94 for value in t1]
    limit = [2 * value for value in t1]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=qubits, y=measured_t1, name="measured T1"))
    fig.add_trace(go.Bar(x=qubits, y=measured_t2, name="measured T2*"))
    fig.add_trace(go.Scatter(x=qubits, y=simulated, mode="markers", name="simulation", marker={"size": 11, "symbol": "square", "color": "#5AB96A"}))
    fig.add_trace(go.Scatter(x=qubits, y=limit, mode="markers", name="2 T1 limit", marker={"size": 11, "symbol": "diamond", "color": "#B46A3C"}))
    fig.update_layout(title_text="Coherence", barmode="group")
    fig.update_yaxes(title_text="time (µs)")
    return fig


def _drive(delta_mhz: float, t_ns: float, omega_mhz: float = 20.0, gamma_per_ns: float = 1 / 180) -> float:
    omega = 2 * math.pi * omega_mhz * 1e-3
    delta = 2 * math.pi * delta_mhz * 1e-3
    orabi = math.sqrt(omega * omega + delta * delta)
    if orabi == 0:
        return 0.0
    return (omega / orabi) ** 2 * math.sin(0.5 * orabi * t_ns) ** 2 * math.exp(-gamma_per_ns * t_ns)


def heatmaps() -> list[go.Figure]:
    """Rabi chevron for P(|1⟩), and the same drive as ⟨Z⟩ = 1 − 2P."""
    rng = random.Random(13)
    deltas = [-40 + i * 2 for i in range(41)]
    times = [i * 3 for i in range(41)]
    population = []
    bloch = []
    for delta in deltas:
        row_p = []
        row_z = []
        for t in times:
            p = _shot(rng, _drive(delta, t))
            row_p.append(p)
            row_z.append(1 - 2 * p)
        population.append(row_p)
        bloch.append(row_z)
    figures = []
    for name, z, scale, zmid in (
        ("Rabi chevron", population, "Blues", None),
        ("⟨Z⟩ chevron", bloch, "RdBu", 0),
    ):
        fig = go.Figure(go.Heatmap(z=z, x=times, y=deltas, colorscale=scale, zmid=zmid, showscale=True))
        fig.update_layout(title_text=name)
        fig.update_xaxes(title_text="t (ns)")
        fig.update_yaxes(title_text="δ/2π (MHz)")
        figures.append(fig)
    return figures


def table(appearance: str, reading: str = "screen") -> go.Figure:
    colors = {"light": LIGHT, "dark": DARK}[appearance]
    metrics = {"screen": SCREEN, "print": PRINT}[reading]
    header_fill = colors["text"]
    header_font = colors["paper"]
    fig = go.Figure(data=[go.Table(
        header={"values": ["Qubit", "f01 (GHz)", "T1 (µs)", "T2* (µs)"], "fill_color": header_fill, "font": {"family": FONT, "color": header_font, "size": metrics["axis"]}, "align": "left", "height": 36 if reading == "screen" else 28, "line_color": colors["axis"]},
        cells={"values": [
            ["Q1", "Q2", "Q3", "Q4"],
            ["4.812", "5.046", "4.673", "5.221"],
            ["22.4", "27.1", "18.6", "33.8"],
            ["13.9", "16.8", "11.5", "21.0"],
        ], "fill_color": colors["paper"], "font": {"family": FONT, "color": colors["text"], "size": metrics["tick"]}, "align": "left", "height": 32 if reading == "screen" else 26, "line_color": colors["grid"]},
    )])
    fig.update_layout(paper_bgcolor=colors["paper"])
    return fig


def anchors(appearance: str, reading: str = "screen") -> list[go.Figure]:
    """Slide background is the paper. The slide surface is the plot area."""
    metrics = {"screen": SCREEN, "print": PRINT}[reading]
    # name, paper, plot, ink, muted, accent, line
    themes = {
        "light": (
            ("Tech Slate", "#F7FAFC", "#EAF1F8", "#1F2937", "#66758A", "#2F80D8", "#D5E0EA"),
            ("Spring Glass", "#FBFFFB", "#EDF9EC", "#1F3428", "#647B68", "#67BF6B", "#D7EAD6"),
            ("Nordic Calm", "#FBFEFC", "#EAF8F2", "#20313A", "#62787D", "#3FBF9B", "#CDE7DE"),
            ("Coffee Terminal", "#FFFAF3", "#F4EADF", "#30271F", "#74665B", "#9A6B43", "#E3D4C4"),
        ),
        "dark": (
            ("Tech Slate", "#101722", "#223146", "#EDF4FB", "#A9B8C9", "#5AA7FF", "#34465F"),
            ("Spring Glass", "#121A15", "#23342A", "#EDF5EC", "#B2C3B1", "#8BD58D", "#3B5141"),
            ("Nordic Calm", "#111821", "#203244", "#E7F0F5", "#A9BBC4", "#79BCE8", "#354A5A"),
            ("Coffee Terminal", "#17120F", "#32251D", "#F3EBE1", "#C5B6A6", "#D39B63", "#4A3A2F"),
        ),
    }
    figures = []
    for name, paper, plot, ink, muted, accent, line in themes[appearance]:
        times = [i * 4 for i in range(50)]
        population = [_drive(0.0, t, omega_mhz=25.0, gamma_per_ns=1 / 200) for t in times]
        fig = go.Figure(go.Scatter(
            x=times,
            y=population,
            mode="lines",
            name=name,
            line={"color": accent, "width": 2},
            showlegend=False,
        ))
        fig.update_layout(
            title_text=name,
            font={"family": FONT, "size": metrics["tick"], "color": ink},
            paper_bgcolor=paper,
            plot_bgcolor=plot,
        )
        fig.update_xaxes(title_text="t (ns)", title_font={"family": FONT, "size": metrics["axis"], "color": ink}, tickfont={"family": FONT, "size": metrics["tick"], "color": muted}, linecolor=line, gridcolor=line, zeroline=False, automargin=True, title_standoff=STANDOFF)
        fig.update_yaxes(title_text="P(|1⟩)", title_font={"family": FONT, "size": metrics["axis"], "color": ink}, tickfont={"family": FONT, "size": metrics["tick"], "color": muted}, linecolor=line, gridcolor=line, zeroline=False, automargin=True, title_standoff=STANDOFF)
        _share_origin(fig)
        _frame(fig, metrics, color=ink)
        figures.append(fig)
    return figures


def _check() -> None:
    fig = lines()
    apply(fig, reading="screen", appearance="light")
    assert fig.data[0].name.startswith("δ/2π")
    assert 0 <= min(fig.data[0].y) and max(fig.data[0].y) <= 1
    assert fig.layout.paper_bgcolor == "#faf8f8"
    assert fig.layout.yaxis.range[0] == 0
    assert fig.layout.xaxis.range[0] == 0
    assert fig.layout.font.size == 16
    assert fig.layout.title.font.size == 22
    assert fig.layout.legend.orientation == "h"
    assert fig.layout.legend.y == -0.28
    assert fig.layout.title.pad.b == OUTER + TITLE_LEADING + TITLE_DESCENT
    assert fig.layout.title.pad.l == OUTER
    assert _text_px("0.8", 16) == 20
    assert _text_px("δ/2π = 0.35 MHz", 16) == 106
    assert fig.layout.margin.l == 4 + 20 + STANDOFF + (18 + 6) + OUTER
    assert fig.layout.margin.t == OUTER + 22 + fig.layout.title.pad.b
    heat = heatmaps()[0]
    apply(heat, reading="screen", appearance="light")
    assert heat.data[0].colorbar.len is None
    assert heat.layout.margin.b == fig.layout.margin.b
    assert fig.layout.margin.r < heat.layout.margin.r
    assert heat.layout.yaxis.range is None
    anchor = anchors("light")[0]
    assert anchor.layout.paper_bgcolor != anchor.layout.plot_bgcolor
    assert anchor.layout.title.font.size == 22
    assert anchors("dark")[0].layout.paper_bgcolor == "#101722"
    fig = lines()
    apply(fig, reading="print", appearance="dark")
    assert fig.layout.font.size == 16
    assert fig.layout.paper_bgcolor == "#161618"
    assert fig.layout.hovermode is False


if __name__ == "__main__":
    _check()
