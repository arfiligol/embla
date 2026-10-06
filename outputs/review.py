"""Review chrome for the documentation figures.

Plotly keeps its own layout. These pages set type, color, and one padding
around the diagram. The sizes are for the review pages only. They are not
an accepted Kit API.
"""

from __future__ import annotations

import math
import random

import plotly.graph_objects as go
from design import SEQUENCES

from design import (CHROME, CONFIG, FONT, METRICS, OUTER, STANDOFF,
                    TITLE_LEADING, TITLE_DESCENT, apply_layout, _frame, _text_px)

LIGHT, DARK = CHROME["light"], CHROME["dark"]
SCREEN = PRINT = METRICS


def apply(fig: go.Figure, *, reading: str, appearance: str) -> go.Figure:
    _share_origin(fig)
    kind = "heatmap" if any(trace.type == "heatmap" for trace in fig.data) else "cartesian"
    apply_layout(fig, appearance, kind=kind)
    fig.update_layout(hovermode="x unified" if reading == "screen" else False)
    return fig


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


# name -> appearance -> paper, plot, ink, muted, axis, grid
THEME_CHROME = {
    "Embla": {
        "light": {"paper": "#faf8f8", "plot": "#faf8f8", "ink": "#2b2b2b", "muted": "#5e5e5e", "axis": "#c8c8c8", "grid": "#e5e5e5"},
        "dark": {"paper": "#161618", "plot": "#161618", "ink": "#ebebec", "muted": "#b8b8b8", "axis": "#4a4a4e", "grid": "#393639"},
    },
    "Tech Slate": {
        "light": {"paper": "#F7FAFC", "plot": "#EAF1F8", "ink": "#1F2937", "muted": "#66758A", "axis": "#D5E0EA", "grid": "#D5E0EA"},
        "dark": {"paper": "#101722", "plot": "#223146", "ink": "#EDF4FB", "muted": "#A9B8C9", "axis": "#34465F", "grid": "#34465F"},
    },
    "Spring Glass": {
        "light": {"paper": "#FBFFFB", "plot": "#EDF9EC", "ink": "#1F3428", "muted": "#647B68", "axis": "#D7EAD6", "grid": "#D7EAD6"},
        "dark": {"paper": "#121A15", "plot": "#23342A", "ink": "#EDF5EC", "muted": "#B2C3B1", "axis": "#3B5141", "grid": "#3B5141"},
    },
    "Nordic Calm": {
        "light": {"paper": "#FBFEFC", "plot": "#EAF8F2", "ink": "#20313A", "muted": "#62787D", "axis": "#CDE7DE", "grid": "#CDE7DE"},
        "dark": {"paper": "#111821", "plot": "#203244", "ink": "#E7F0F5", "muted": "#A9BBC4", "axis": "#354A5A", "grid": "#354A5A"},
    },
    "Coffee Terminal": {
        "light": {"paper": "#FFFAF3", "plot": "#F4EADF", "ink": "#30271F", "muted": "#74665B", "axis": "#E3D4C4", "grid": "#E3D4C4"},
        "dark": {"paper": "#17120F", "plot": "#32251D", "ink": "#F3EBE1", "muted": "#C5B6A6", "axis": "#4A3A2F", "grid": "#4A3A2F"},
    },
}

LINE_PALETTE_BANDS = {"6": "Six colors", "8": "Eight colors", "10": "Ten colors"}

# Matplotlib tab10, exposed by Plotly as D3. Same cycle as the built-in scales
# used on the heatmaps. On the light plot, colors that fall under 3:1 are one
# step darker in the same hue.
THEME_LINES: dict = {
    "Embla": {
        "light": {
            "6": {
                "colors": [
                    "#1F77B4",
                    "#E36A00",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B"
                ],
                "minContrast": 3.1
            },
            "8": {
                "colors": [
                    "#1F77B4",
                    "#E36A00",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B",
                    "#C96AAD",
                    "#7F7F7F"
                ],
                "minContrast": 3.1
            },
            "10": {
                "colors": [
                    "#1F77B4",
                    "#E36A00",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B",
                    "#C96AAD",
                    "#7F7F7F",
                    "#8C8E14",
                    "#149AAB"
                ],
                "minContrast": 3.1
            }
        },
        "dark": {
            "6": {
                "colors": [
                    "#1F77B4",
                    "#FF7F0E",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B"
                ],
                "minContrast": 8.48
            },
            "8": {
                "colors": [
                    "#1F77B4",
                    "#FF7F0E",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B",
                    "#E377C2",
                    "#7F7F7F"
                ],
                "minContrast": 8.11
            },
            "10": {
                "colors": [
                    "#1F77B4",
                    "#FF7F0E",
                    "#2CA02C",
                    "#D62728",
                    "#9467BD",
                    "#8C564B",
                    "#E377C2",
                    "#7F7F7F",
                    "#BCBD22",
                    "#17BECF"
                ],
                "minContrast": 8.14
            }
        }
    },
    "Tech Slate": {
        "light": {
            "6": {
                "colors": [
                    "#305888",
                    "#106078",
                    "#505090",
                    "#5078A8",
                    "#2080A0",
                    "#7070B8"
                ],
                "minContrast": 3.92
            },
            "8": {
                "colors": [
                    "#006070",
                    "#185880",
                    "#385090",
                    "#585088",
                    "#388090",
                    "#4880A8",
                    "#6078B0",
                    "#7870B0"
                ],
                "minContrast": 3.74
            },
            "10": {
                "colors": [
                    "#006068",
                    "#006080",
                    "#305888",
                    "#485090",
                    "#604890",
                    "#308088",
                    "#3080A0",
                    "#5078A8",
                    "#6870B0",
                    "#8068B0"
                ],
                "minContrast": 3.91
            }
        },
        "dark": {
            "6": {
                "colors": [
                    "#88B0E0",
                    "#68B8D8",
                    "#A0A8F0",
                    "#B0D0F8",
                    "#88D8F8",
                    "#C8C8F8"
                ],
                "minContrast": 5.85
            },
            "8": {
                "colors": [
                    "#58C0D8",
                    "#78B8E8",
                    "#98B0E8",
                    "#B0A8E8",
                    "#80E0F8",
                    "#B0D8F8",
                    "#C0D0F8",
                    "#C8C0F8"
                ],
                "minContrast": 6.02
            },
            "10": {
                "colors": [
                    "#70C0C8",
                    "#70B8D8",
                    "#88B0E0",
                    "#A0A8E8",
                    "#B8A0F0",
                    "#90E0E8",
                    "#98D8F8",
                    "#B0D0F8",
                    "#C0C8F8",
                    "#D0C0F8"
                ],
                "minContrast": 5.8
            }
        }
    },
    "Spring Glass": {
        "light": {
            "6": {
                "colors": [
                    "#206028",
                    "#485818",
                    "#006848",
                    "#508850",
                    "#688028",
                    "#308868"
                ],
                "minContrast": 3.89
            },
            "8": {
                "colors": [
                    "#505808",
                    "#386020",
                    "#006838",
                    "#206050",
                    "#707828",
                    "#588040",
                    "#388858",
                    "#208870"
                ],
                "minContrast": 4.01
            },
            "10": {
                "colors": [
                    "#605808",
                    "#486018",
                    "#206028",
                    "#086848",
                    "#286058",
                    "#807828",
                    "#688038",
                    "#508850",
                    "#188860",
                    "#008878"
                ],
                "minContrast": 3.89
            }
        },
        "dark": {
            "6": {
                "colors": [
                    "#80C080",
                    "#A0B860",
                    "#68C8A0",
                    "#A0E8A0",
                    "#C0D880",
                    "#88E8C0"
                ],
                "minContrast": 5.96
            },
            "8": {
                "colors": [
                    "#B0B860",
                    "#90C070",
                    "#78C090",
                    "#50C8A8",
                    "#D0D880",
                    "#B0E090",
                    "#98E8B0",
                    "#78E8C8"
                ],
                "minContrast": 6.1
            },
            "10": {
                "colors": [
                    "#B8B058",
                    "#98B860",
                    "#80C080",
                    "#68C098",
                    "#60C0B0",
                    "#D8D078",
                    "#C0E088",
                    "#A0E8A0",
                    "#80E8B8",
                    "#90E8D8"
                ],
                "minContrast": 5.86
            }
        }
    },
    "Nordic Calm": {
        "light": {
            "6": {
                "colors": [
                    "#006850",
                    "#186030",
                    "#006060",
                    "#388870",
                    "#388850",
                    "#008888"
                ],
                "minContrast": 3.9
            },
            "8": {
                "colors": [
                    "#286028",
                    "#086040",
                    "#006858",
                    "#006870",
                    "#508848",
                    "#288860",
                    "#108878",
                    "#008890"
                ],
                "minContrast": 3.88
            },
            "10": {
                "colors": [
                    "#386020",
                    "#106838",
                    "#006850",
                    "#006860",
                    "#006070",
                    "#588040",
                    "#408858",
                    "#388870",
                    "#008880",
                    "#288090"
                ],
                "minContrast": 3.9
            }
        },
        "dark": {
            "6": {
                "colors": [
                    "#58C0A0",
                    "#78C088",
                    "#58C0C0",
                    "#88E8C8",
                    "#98E8A8",
                    "#78E8E8"
                ],
                "minContrast": 5.91
            },
            "8": {
                "colors": [
                    "#80C078",
                    "#70C098",
                    "#68C0B0",
                    "#60C0C8",
                    "#A0E098",
                    "#88E8B8",
                    "#90E8D8",
                    "#80E8F0"
                ],
                "minContrast": 6.05
            },
            "10": {
                "colors": [
                    "#90C070",
                    "#70C088",
                    "#58C0A0",
                    "#50C8C0",
                    "#70C0D0",
                    "#B0E090",
                    "#90E8A8",
                    "#88E8C8",
                    "#78E8E0",
                    "#90E0F0"
                ],
                "minContrast": 5.91
            }
        }
    },
    "Coffee Terminal": {
        "light": {
            "6": {
                "colors": [
                    "#784008",
                    "#804030",
                    "#705000",
                    "#A06028",
                    "#B05840",
                    "#907020"
                ],
                "minContrast": 3.91
            },
            "8": {
                "colors": [
                    "#883830",
                    "#784020",
                    "#704810",
                    "#605008",
                    "#A85850",
                    "#A86038",
                    "#986828",
                    "#807028"
                ],
                "minContrast": 4.02
            },
            "10": {
                "colors": [
                    "#883840",
                    "#803820",
                    "#784008",
                    "#705008",
                    "#605800",
                    "#B05860",
                    "#A85840",
                    "#A06028",
                    "#907030",
                    "#807820"
                ],
                "minContrast": 3.82
            }
        },
        "dark": {
            "6": {
                "colors": [
                    "#E09858",
                    "#F09078",
                    "#D0A850",
                    "#F8B880",
                    "#F8B8A8",
                    "#F0C870"
                ],
                "minContrast": 6.21
            },
            "8": {
                "colors": [
                    "#F09088",
                    "#E09870",
                    "#D8A058",
                    "#C8B050",
                    "#F8B0A8",
                    "#F8B088",
                    "#F8C078",
                    "#E8D070"
                ],
                "minContrast": 6.27
            },
            "10": {
                "colors": [
                    "#F08890",
                    "#F09070",
                    "#E09858",
                    "#D0A858",
                    "#B8B050",
                    "#F8B0B0",
                    "#F8B098",
                    "#F8B880",
                    "#F0C878",
                    "#D8D070"
                ],
                "minContrast": 6.09
            }
        }
    }
}

def palette_lines(theme: str, size: str, appearance: str, reading: str = "screen") -> go.Figure:
    """Offset curves in the theme's own hues, on that plot."""
    colors = THEME_LINES[theme][appearance][size]["colors"]
    chrome = THEME_CHROME[theme][appearance]
    metrics = {"screen": SCREEN, "print": PRINT}[reading]
    xs = [i / 48 for i in range(49)]
    fig = go.Figure()
    for i, color in enumerate(colors):
        shift = len(colors) - i
        ys = [shift + 0.28 * math.sin(2 * math.pi * (x * 1.5 + i * 0.015)) for x in xs]
        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=str(i + 1),
            line={"color": color, "width": 2},
            showlegend=False,
        ))
    fig.update_layout(
        title_text=LINE_PALETTE_BANDS[size],
        height=150 + 22 * len(colors),
        showlegend=False,
        font={"family": FONT, "size": metrics["tick"], "color": chrome["ink"]},
        paper_bgcolor=chrome["paper"],
        plot_bgcolor=chrome["plot"],
        hovermode="closest" if reading == "screen" else False,
    )
    styled = {
        "title_font": {"family": FONT, "size": metrics["axis"], "color": chrome["ink"]},
        "tickfont": {"family": FONT, "size": metrics["tick"], "color": chrome["muted"]},
        "gridcolor": chrome["grid"],
        "linecolor": chrome["axis"],
        "tickcolor": chrome["axis"],
        "zeroline": False,
        "automargin": True,
        "title_standoff": STANDOFF,
    }
    fig.update_xaxes(title_text="t", range=[0, 1], **styled)
    fig.update_yaxes(showticklabels=len(colors) <= 10, **styled)
    lo = min(min(trace.y) for trace in fig.data)
    hi = max(max(trace.y) for trace in fig.data)
    fig.update_yaxes(range=[lo - 0.4, hi + 0.4])
    _frame(fig, metrics, color=chrome["ink"])
    return fig


def show_palette(theme: str, size: str, *, reading: str, appearance: str) -> None:
    fig = palette_lines(theme, size, appearance, reading)
    config = {"staticPlot": True, "displayModeBar": False} if reading == "print" else CONFIG
    display_figure(fig, config=config)


def display_figure(fig, *, config=CONFIG):
    """Embed Plotly in Quarto without loading a second document math engine."""
    from IPython.display import HTML, display
    display(HTML(fig.to_html(full_html=False, include_plotlyjs="cdn",
                             include_mathjax=False, auto_play=False, config=config)))


def for_renderings(draw) -> None:
    """Draw light, then dark. The cell needs `#| renderings: [light, dark]`."""
    for appearance in ("light", "dark"):
        draw(appearance)


def show(fig: go.Figure, *, reading: str, appearance: str) -> go.Figure:
    apply(fig, reading=reading, appearance=appearance)
    config = {"staticPlot": True, "displayModeBar": False} if reading == "print" else CONFIG
    display_figure(fig, config=config)
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
    fig.add_trace(go.Scatter(x=qubits, y=simulated, mode="markers", name="simulation", marker={"size": 11, "symbol": "square"}))
    fig.add_trace(go.Scatter(x=qubits, y=limit, mode="markers", name="2 T1 limit", marker={"size": 11, "symbol": "diamond"}))
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
    return apply_layout(fig, appearance, kind="table")


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
    sample = palette_lines("Embla", "6", "light")
    assert len(sample.data) == 6
    assert sample.data[0].line.color == THEME_LINES["Embla"]["light"]["6"]["colors"][0]
    assert sample.layout.paper_bgcolor == "#faf8f8"
    dark = palette_lines("Embla", "6", "dark")
    assert len(dark.data) == 6
    assert dark.layout.paper_bgcolor == "#161618"
    assert palette_lines("Embla", "10", "light").data[0].line.color == "#1F77B4"


if __name__ == "__main__":
    _check()
