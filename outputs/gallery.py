"""Declared illustrative inputs for comparing presentation, not measurement."""
import math
import plotly.graph_objects as go
from design import apply_layout, CONFIG, SEQUENCES, CHROME
from review import display_figure

def dense():
    fig=go.Figure()
    for i in range(6):
        x=list(range(61))
        y=[.03+.025*math.exp(-t/9)+.005*math.sin(t*1.7+i)+.004*math.cos(t*.8+i*2) for t in x]
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines+markers",name=f"Series {i+1}"))
    fig.update_layout(height=450)
    fig.update_xaxes(title="Step N")
    fig.update_yaxes(title="Illustrative amplitude")
    return fig

def bars():
    fig=go.Figure()
    for i,values in enumerate([[4,7,5,8],[6,3,7,5],[5,6,4,7]]):
        fig.add_trace(go.Bar(x=["A","B","C","D"],y=values,name=f"Series {i+1}"))
    fig.update_layout(height=380,barmode="group")
    fig.update_yaxes(title="Illustrative value")
    return fig

def heatmap():
    axis=[i/10 for i in range(31)]
    fig=go.Figure(go.Heatmap(x=axis,y=axis,z=[[math.sin(x)*math.cos(y) for x in axis] for y in axis],colorscale="RdBu",zmid=0,colorbar=dict(title="sin x cos y")))
    fig.update_layout(height=400)
    fig.update_xaxes(title="x")
    fig.update_yaxes(title="y")
    return fig

def table(appearance="light",custom=True):
    chrome=CHROME[appearance]
    options={}
    if custom:
        options=dict(header=dict(fill_color=SEQUENCES[appearance][5][0],font=dict(color="white"),height=32),
                     cells=dict(fill_color=chrome["plot"],font=dict(color=chrome["text"]),height=30))
    fig=go.Figure(go.Table(header=dict(values=["Category","Value","Status"],**options.get("header",{})),
        cells=dict(values=[["A","B","C"],[4,7,5],["Example"]*3],**options.get("cells",{}))))
    fig.update_layout(height=230)
    return fig

def show(kind,appearance="light",custom=True):
    fig=table(appearance,custom) if kind=="table" else {"dense":dense,"bars":bars,"heatmap":heatmap}[kind]()
    if custom:
        apply_layout(fig, appearance, kind={"dense": "cartesian", "bars": "cartesian", "heatmap": "heatmap", "table": "table"}[kind])
    else:
        fig.update_layout(template="plotly")
    display_figure(fig, config=CONFIG)
