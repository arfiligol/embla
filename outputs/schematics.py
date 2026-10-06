"""Scientific schematic specimens; coordinates are presentation geometry."""
import math
import plotly.graph_objects as go
from design import CHROME, SEQUENCES, apply_layout

def canvas(dark, height):
    mode = "dark" if dark else "light"
    ink = CHROME[mode]["text"]
    sequence = SEQUENCES[mode][10]
    colors = [sequence[1], sequence[0], sequence[8], sequence[4]]
    fig = go.Figure()
    fig.update_layout(height=height, showlegend=False)
    apply_layout(fig, mode, kind="diagram")
    fig.update_xaxes(visible=False,range=[0,10],fixedrange=True)
    fig.update_yaxes(visible=False,range=[0,6],fixedrange=True)
    return fig, colors, ink

def label(fig,x,y,text,color=None,size=15,**kwargs):
    fig.add_annotation(x=x,y=y,text=text,showarrow=False,font=dict(size=size,color=color),**kwargs)

def arrow(fig,x0,y0,x1,y1,color,double=False):
    fig.add_annotation(x=x1,y=y1,ax=x0,ay=y0,axref="x",ayref="y",text="",showarrow=True,
        arrowhead=2,startarrowhead=2,arrowside="end+start" if double else "end",arrowcolor=color,arrowwidth=2)

def control_sequence(dark=True):
    fig,c,ink=canvas(dark,440)
    for i,name in enumerate(["q1 · pseudomode","q1–q2 coupler","q2 · waveguide","q2–q3 coupler","q3 · qubit"]):
        y=5.3-i
        fig.add_shape(type="line",x0=2.1,x1=9.8,y0=y,y1=y,line=dict(color=ink,width=1),opacity=.15)
        label(fig,.05,y,name,xanchor="left")
    blocks=[(2.2,3.6,5.3,"Z pulse · 40 ns",0),(2.2,3.6,4.3,"θΛ amplitude",1),
        (4.25,5.65,2.3,"θΓ amplitude",1),(4.25,5.65,1.3,"Z pulse · 40 ns",3),
        (6.25,8.25,3.3,"Parametric reset",2),(8.8,9.95,1.3,"Stark tone",3)]
    for x0,x1,y,text,k in blocks:
        outline=text=="Stark tone"
        fig.add_shape(type="rect",x0=x0,x1=x1,y0=y-.28,y1=y+.28,
            fillcolor="rgba(0,0,0,0)" if outline else c[k],line=dict(color=c[k],width=2,dash="dash" if outline else "solid"))
        label(fig,(x0+x1)/2,y,text,ink if outline else "#15252F",13)
    for x,text in [(2.9,"Swap 1"),(3.9,"Gap"),(4.95,"Swap 2"),(5.95,"Gap"),(7.25,"Reset waveguide"),(8.55,"Gap"),(9.4,"Phase")]:
        label(fig,x,.45,text,size=13)
    return fig

def photon_diagram(dark=True):
    fig,c,ink=canvas(dark,520)
    blue,green=c[0],c[3]
    x=[1+3*i/100 for i in range(101)]
    fig.add_trace(go.Scatter(x=x,y=[3.8+1.35/(1+((v-2.5)/.3)**2) for v in x],mode="lines",line=dict(color=blue,width=4),hoverinfo="skip"))
    label(fig,2.5,5.65,"Photon spectrum",size=18)
    arrow(fig,.9,3.8,4.2,3.8,ink)
    label(fig,4.4,3.8,"f")
    label(fig,2.5,3.5,"fₚ")
    arrow(fig,2.2,4.45,2.8,4.45,blue,True)
    label(fig,3.05,4.45,"Λ",blue,20)
    theta=[2*math.pi*i/100 for i in range(101)]
    fig.add_trace(go.Scatter(x=[7.7+.8*math.cos(t) for t in theta],y=[4.35+.8*math.sin(t) for t in theta],mode="lines",line=dict(color=green,width=4),hoverinfo="skip"))
    for y in [4.1,4.6]:
        fig.add_shape(type="line",x0=7.3,x1=8.1,y0=y,y1=y,line=dict(color=ink,width=3))
    label(fig,7.7,5.5,"Qubit",green,19)
    for y in [1.3,.95]:
        fig.add_shape(type="line",x0=.8,x1=9,y0=y,y1=y,line=dict(color=ink,width=3))
    t=[.95+4.4*i/100 for i in range(101)]
    y=[1.35+1.35*math.exp((v-5.35)/1.15) for v in t]
    fig.add_trace(go.Scatter(x=t+[5.35,.95],y=y+[1.35,1.35],mode="lines",fill="toself",fillcolor="rgba(130,180,225,.13)",line=dict(color=blue,width=4),hoverinfo="skip"))
    label(fig,3,2.65,"Rising temporal envelope")
    label(fig,5.6,2.6,"t = 0",xanchor="left")
    arrow(fig,1.2,1.12,6.3,1.12,blue)
    arrow(fig,7.7,1.45,7.7,3.4,blue,True)
    label(fig,8.05,2.4,"Γ",blue,20)
    label(fig,5,.35,"A wave packet propagates toward a two-level receiver",size=17)
    fig.update_yaxes(scaleanchor="x",scaleratio=1)
    return fig
