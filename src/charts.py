from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.metrics import week_start

EMBER = "#ff4700"    # cumplido / serie principal
MUTED = "#4a443d"    # no cumplido
ASH = "#cccccc"
BONE = "#ffffff"
GRID = "rgba(204,204,204,0.12)"
FONT = "Helvetica Neue, Inter, system-ui, sans-serif"
DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _layout(fig: go.Figure, title: str, height: int = 320) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=BONE)),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=ASH, family=FONT, size=13),
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
    )
    return fig


def calendar_heatmap(df: pd.DataFrame, today: date, weeks: int = 26) -> go.Figure:
    """Una celda por día: ember cumplido, gris no cumplido, vacío sin registro."""
    start = week_start(today) - timedelta(weeks=weeks - 1)
    z = np.full((7, weeks), np.nan)
    hover = np.full((7, weeks), "", dtype=object)
    for r in df[df["log_date"] >= start].itertuples():
        col = (week_start(r.log_date) - start).days // 7
        z[r.log_date.weekday(), col] = 1 if r.met else 0
        hover[r.log_date.weekday(), col] = f"{r.log_date:%d/%m/%Y}: {r.value:g}"
    labels = [f"{start + timedelta(weeks=i):%d %b}" for i in range(weeks)]
    fig = go.Figure(
        go.Heatmap(
            z=z, x=labels, y=DAYS, text=hover, hoverinfo="text",
            zmin=0, zmax=1, colorscale=[[0, MUTED], [1, EMBER]],
            showscale=False, xgap=3, ygap=3,
        )
    )
    _layout(fig, "Calendario de cumplimiento", height=260)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(nticks=8, showgrid=False)
    return fig


def value_line(df: pd.DataFrame, unit: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["log_date"], y=df["value"], mode="lines+markers",
                             name=unit, line=dict(color=EMBER, width=2),
                             marker=dict(color=EMBER, size=6)))
    fig.add_trace(go.Scatter(x=df["log_date"], y=df["target"], mode="lines",
                             name="meta", line=dict(color=ASH, dash="dash", width=1, shape="hv")))
    fig.update_yaxes(title=unit, rangemode="tozero")
    return _layout(fig, "Valor diario vs meta")


def weekday_bar(df: pd.DataFrame) -> go.Figure:
    dow = df["log_date"].map(lambda d: d.weekday())
    pct = (df["met"].astype(float).groupby(dow).mean() * 100).reindex(range(7))
    fig = go.Figure(go.Bar(x=DAYS, y=pct.values, marker_color=EMBER))
    fig.update_yaxes(title="% cumplido", range=[0, 100])
    return _layout(fig, "Cumplimiento por día de la semana", height=260)


def weekly_bar(df: pd.DataFrame, unit: str) -> go.Figure:
    colors = [EMBER if m else MUTED for m in df["met"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["week_start"], y=df["total"], marker_color=colors, name=unit))
    fig.add_trace(go.Scatter(x=df["week_start"], y=df["target"], mode="lines",
                             name="meta", line=dict(color=ASH, dash="dash", width=1, shape="hv")))
    fig.update_yaxes(title=unit, rangemode="tozero")
    return _layout(fig, "Total por semana (lunes a domingo)")
