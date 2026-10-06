"""Copyable Embla presentation recipe; not an installed or accepted API.

Only appearance defaults belong here. Figures own data, units, geometry,
axis ranges, and any figure-specific layout. Invalid inputs use native errors.
"""

import math
import re

import plotly.graph_objects as go
import plotly.io as pio

_SPECTRUM_ANCHORS = {
    "light": ["#7770E7", "#22B8D0", "#59D47A", "#DED849", "#FFAC4A", "#F26B52"],
    "dark": ["#7977DD", "#43BDDC", "#76D878", "#DADD5D", "#F4A14B", "#DF633B"],
}

def _spectrum(anchors, count):
    """Sample the indigo-to-red family at equally spaced RGB positions."""
    rgb = [tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
           for color in anchors]
    result = []
    for index in range(count):
        position = index * (len(rgb) - 1) / (count - 1)
        left = min(int(position), len(rgb) - 2)
        fraction = position - left
        channels = [round(a + fraction * (b - a))
                    for a, b in zip(rgb[left], rgb[left + 1])]
        result.append("#" + "".join(f"{value:02X}" for value in channels))
    return result


# Three presentation sequences, not a limit on the number of figure traces.
SEQUENCES = {
    appearance: {size: _spectrum(anchors, size) for size in (5, 10, 20)}
    for appearance, anchors in _SPECTRUM_ANCHORS.items()
}
CHROME = {
    "light": {
        "paper": "#FAF8F8", "plot": "#FFFFFF", "text": "#2B2B2B",
        "muted": "#5E5E5E", "grid": "#E5E5E5", "axis": "#C8C8C8",
    },
    "dark": {
        "paper": "#161618", "plot": "#202023", "text": "#EBEBEC",
        "muted": "#B8B8B8", "grid": "#393639", "axis": "#4A4A4E",
    },
}

FONT = '"Source Sans 3", sans-serif'
METRICS = {"tick": 16, "axis": 18, "legend": 16, "title": 22}
OUTER = 16
STANDOFF = 15
TITLE_LEADING = 8
TITLE_DESCENT = 5
COLORBAR_XPAD = 10
COLORBAR_BEFORE_TICKS = 53

CONFIG = {
    "responsive": True,
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["sendDataToCloud"],
}


def template(appearance, colors=5):
    """Clone native light/dark defaults and apply presentation colors and type."""
    chrome = CHROME[appearance]
    base = {"light": "plotly_white", "dark": "plotly_dark"}[appearance]
    result = go.layout.Template(pio.templates[base].to_plotly_json())
    result.layout.update(
        paper_bgcolor=chrome["paper"],
        plot_bgcolor=chrome["plot"],
        title={"font": {"family": FONT, "size": METRICS["title"]}},
        legend={"font": {"family": FONT, "size": METRICS["legend"]}},
        font={
            "family": FONT,
            "size": 16,
            "color": chrome["text"],
        },
        colorway=SEQUENCES[appearance][colors],
        xaxis={"gridcolor": chrome["grid"], "automargin": True,
               "tickfont": {"color": chrome["muted"]},
               "title": {"font": {"size": METRICS["axis"]}, "standoff": STANDOFF},
               "linecolor": chrome["axis"], "zeroline": False},
        yaxis={"gridcolor": chrome["grid"], "automargin": True,
               "tickfont": {"color": chrome["muted"]},
               "title": {"font": {"size": METRICS["axis"]}, "standoff": STANDOFF},
               "linecolor": chrome["axis"], "zeroline": False},
    )
    for trace in result.data.scatter:
        trace.update(line={"width": 2}, marker={"size": 6})
    for trace in result.data.bar:
        trace.update(marker={"line": {"width": 0}})
    return result


def _numbers(values) -> list[float]:
    if values is None:
        return []
    return [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]


def _text_px(text: str, size: int) -> int:
    """Estimate English label advances; native automargin handles font differences."""
    text = re.sub(r"<[^>]*>", "", text)
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
    if fig.layout.yaxis.visible is False:
        return 0
    ink = 4 + (_tick_width(fig, "yaxis", metrics["tick"]) if fig.layout.yaxis.showticklabels is not False else 0)
    if fig.layout.yaxis.title and fig.layout.yaxis.title.text:
        ink += STANDOFF + (metrics["axis"] + 6)
    return ink


def _bottom_ink(fig: go.Figure, metrics: dict) -> int:
    if fig.layout.xaxis.visible is False:
        return 0
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




def apply_layout(fig, appearance="light", colors=5, kind="cartesian"):
    """Apply one presentation layout after setting figure data, titles and geometry.

    Text-based margins differ by content so the intended outer ink padding stays
    16 px. Native automargin accommodates actual font metrics and wrapped legends.
    Pulse breakpoint layouts travel with the figure for the HTML observer.
    """
    chrome = CHROME[appearance]
    fig.update_layout(template=template(appearance, colors),
                      paper_bgcolor=chrome["paper"], plot_bgcolor=chrome["plot"],
                      font=dict(family=FONT, size=METRICS["tick"], color=chrome["text"]),
                      title_font=dict(family=FONT, size=METRICS["title"], color=chrome["text"]),
                      legend_font=dict(family=FONT, size=METRICS["legend"], color=chrome["text"]),
                      hoverlabel=dict(bgcolor=chrome["plot"], bordercolor=chrome["axis"],
                                      font=dict(family=FONT, size=METRICS["tick"], color=chrome["text"])))
    fig.update_xaxes(title_font=dict(family=FONT, size=METRICS["axis"], color=chrome["text"]),
                     tickfont=dict(size=METRICS["tick"], color=chrome["muted"]),
                     title_standoff=STANDOFF, gridcolor=chrome["grid"], linecolor=chrome["axis"],
                     tickcolor=chrome["axis"], zeroline=False, automargin=True)
    fig.update_yaxes(title_font=dict(family=FONT, size=METRICS["axis"], color=chrome["text"]),
                     tickfont=dict(size=METRICS["tick"], color=chrome["muted"]),
                     title_standoff=STANDOFF, gridcolor=chrome["grid"], linecolor=chrome["axis"],
                     tickcolor=chrome["axis"], zeroline=False, automargin=True)
    # Layout profiles reserve content space without owning data or coordinate ranges.
    {"cartesian": _cartesian_layout, "heatmap": _cartesian_layout,
     "pulse": _pulse_layout, "three-d": _three_d_layout,
     "diagram": _diagram_layout, "table": _table_layout}[kind](fig, chrome)
    return fig


def _cartesian_layout(fig, chrome):
    for trace in fig.data:
        colorbar = getattr(trace, "colorbar", None)
        if colorbar is not None:
            colorbar.update(tickfont=dict(size=METRICS["tick"], color=chrome["muted"]),
                            xpad=COLORBAR_XPAD, thickness=30,
                            title_font=dict(size=METRICS["axis"], color=chrome["text"]))
    _frame(fig, METRICS)
    # Let HTML containers grow for wrapped legends instead of shrinking the axes.
    meta = dict(fig.layout.meta or {})
    meta["embla_sizing"] = dict(height=fig.layout.height or 450,
        itemWidths=[30 + _text_px(name, METRICS["legend"]) for name in _legend_names(fig)],
        rowHeight=METRICS["legend"] + 8,
        sideMargins=fig.layout.margin.l + fig.layout.margin.r,
        toolbarBreakpoint=540, toolbarTop=fig.layout.margin.t)
    fig.update_layout(meta=meta)


def _pulse_layout(fig, chrome):
    _cartesian_layout(fig, chrome)
    base = fig.layout.margin.to_plotly_json()
    names = _legend_names(fig)
    legend_width = max((_text_px(name, METRICS["legend"]) for name in names), default=0) + 40
    wide = {"legend.orientation": "v", "legend.x": 1.02, "legend.y": 1,
            "legend.xanchor": "left", "legend.yanchor": "top",
            "margin.r": OUTER + legend_width, "margin.b": base["b"]}
    narrow = {"legend.orientation": "h", "legend.x": 0, "legend.y": -0.28,
              "legend.xanchor": "left", "legend.yanchor": "top",
              "margin.r": base["r"], "margin.b": base["b"] + 2 * (METRICS["legend"] + 8)}
    meta = dict(fig.layout.meta or {})
    meta.pop("embla_sizing", None)
    meta["embla_responsive"] = dict(breakpoint=540, narrow=narrow, wide=wide)
    fig.update_layout(meta=meta)
    fig.update_layout(wide)


def _three_d_layout(fig, chrome):
    _title_inside(fig, size=METRICS["title"])
    top = OUTER + METRICS["title"] + OUTER + TITLE_LEADING + TITLE_DESCENT if fig.layout.title.text else OUTER
    bottom = OUTER + 144 if fig.layout.sliders or fig.layout.updatemenus else OUTER
    fig.update_layout(margin=dict(l=OUTER, r=OUTER, t=top, b=bottom),
                      scene_bgcolor=chrome["plot"])
    for name in ("xaxis", "yaxis", "zaxis"):
        getattr(fig.layout.scene, name).update(backgroundcolor=chrome["plot"], gridcolor=chrome["grid"],
            linecolor=chrome["axis"], tickfont=dict(size=METRICS["tick"], color=chrome["muted"]),
            title_font=dict(size=METRICS["axis"], color=chrome["text"]))


def _diagram_layout(fig, chrome):
    fig.update_layout(margin=dict(l=OUTER, r=OUTER, t=OUTER, b=OUTER))
    # Figure annotations own their semantic colors and positions.


def _table_layout(fig, chrome):
    fig.update_layout(margin=dict(l=OUTER, r=OUTER, t=OUTER, b=OUTER))
    table = next(trace for trace in fig.data if trace.type == "table")
    row_count = len(table.cells.values[0])
    fig.update_layout(height=2 * OUTER + (table.header.height or 32) + row_count * (table.cells.height or 30))
