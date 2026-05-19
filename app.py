"""
charts.py
---------
All Plotly chart functions for the museum visitor dashboard.
Visitor charts use Counter A (Traffic In) data only.
Occupancy flow chart uses the merged In/Out flow frame.
"""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go

BLUE    = "#1A56DB"
ORANGE  = "#FF5A1F"
PURPLE  = "#7E3AF2"
TEAL    = "#0E9F6E"
NEUTRAL = "#6B7280"
GRID    = "#E5E7EB"

_WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _layout(title: str = "", height: int = 400) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=15, color="#111827"), x=0),
        height=height,
        margin=dict(l=16, r=16, t=48 if title else 20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color="#374151"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, linecolor=GRID, linewidth=1, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor=GRID, linecolor=GRID, zeroline=False,
                   tickfont=dict(size=11)),
    )


# ── Executive trend ───────────────────────────────────────────────────────────
def trend_overview(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["Date_Only"], y=daily["Visitors"], name="Daily visitors",
        marker_color=BLUE, opacity=0.25,
        hovertemplate="<b>%{x}</b><br>Visitors: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date_Only"], y=daily["Rolling_Avg"], name="7-day avg",
        mode="lines", line=dict(color=BLUE, width=2.5, shape="spline"),
        hovertemplate="<b>%{x}</b><br>7-day avg: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout("Daily Visitor Trend", height=300))
    fig.update_yaxes(title_text="Visitors")
    return fig


# ── Daily trends ──────────────────────────────────────────────────────────────
def daily_visitors_chart(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["Date_Only"], y=daily["Visitors"], name="Daily visitors",
        marker_color=BLUE, opacity=0.6,
        hovertemplate="<b>%{x}</b><br>Visitors: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date_Only"], y=daily["Rolling_Avg"], name="7-day avg",
        mode="lines", line=dict(color=ORANGE, width=2, dash="dot", shape="spline"),
        hovertemplate="<b>%{x}</b><br>7-day avg: %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout("Daily Visitor Count", height=400))
    fig.update_yaxes(title_text="Visitors")
    return fig


def monthly_visitors_chart(monthly: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=monthly["Month"], y=monthly["Visitors"],
        marker_color=PURPLE, opacity=0.85, borderRadius=3,
        hovertemplate="<b>%{x}</b><br>Visitors: %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_layout("Monthly Visitor Totals", height=360))
    fig.update_xaxes(tickangle=-30)
    fig.update_yaxes(title_text="Visitors")
    return fig


# ── Hourly analysis ───────────────────────────────────────────────────────────
def hourly_visitors_chart(hourly: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=hourly["Time"], y=hourly["Visitors"],
        marker_color=TEAL, opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Visitors: %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_layout("Hourly Visitor Distribution", height=360))
    fig.update_yaxes(title_text="Total Visitors")
    return fig


def am_pm_donut(ampm: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=ampm["AM_PM"], values=ampm["Visitors"], hole=0.55,
        marker=dict(colors=[BLUE, ORANGE], line=dict(color="white", width=2)),
        hovertemplate="<b>%{label}</b><br>Visitors: %{value:,}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**_layout("AM vs PM Visitors", height=340))
    return fig


def busiest_hours_bar(hourly: pd.DataFrame) -> go.Figure:
    ranked = hourly.sort_values("Visitors", ascending=True)
    colors = [BLUE if i >= len(ranked) - 3 else NEUTRAL for i in range(len(ranked))]
    fig = go.Figure(go.Bar(
        x=ranked["Visitors"], y=ranked["Time"], orientation="h",
        marker_color=colors, opacity=0.9,
        hovertemplate="<b>%{y}</b><br>Visitors: %{x:,}<extra></extra>",
    ))
    fig.update_layout(**_layout("Busiest Hours Ranking", height=340))
    fig.update_xaxes(title_text="Total Visitors")
    return fig


def weekday_hour_heatmap(pivot: pd.DataFrame) -> go.Figure:
    if pivot.empty:
        return go.Figure()
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0, "#EFF6FF"], [0.5, "#3B82F6"], [1, "#1E3A8A"]],
        hovertemplate="<b>%{y} — %{x}</b><br>Avg visitors: %{z:.1f}<extra></extra>",
        colorbar=dict(title="Avg visitors", thickness=12, len=0.8),
    ))
    fig.update_layout(**_layout("Visitor Heatmap — Weekday × Hour", height=300))
    fig.update_xaxes(tickangle=-30)
    return fig


# ── Occupancy flow ────────────────────────────────────────────────────────────
def occupancy_flow_chart(flow_avg: pd.DataFrame) -> go.Figure:
    """
    Side-by-side avg arrivals vs departures per hour, with net flow line.
    Positive net = museum filling; negative = emptying.
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=flow_avg["Time"], y=flow_avg["In"], name="Avg arrivals",
        marker_color=BLUE, opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Avg arrivals: %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=flow_avg["Time"], y=flow_avg["Out"], name="Avg departures",
        marker_color=ORANGE, opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Avg departures: %{y:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=flow_avg["Time"], y=flow_avg["Net"], name="Net flow",
        mode="lines+markers", line=dict(color=TEAL, width=2.5),
        marker=dict(size=7, color=[TEAL if n >= 0 else ORANGE for n in flow_avg["Net"]]),
        hovertemplate="<b>%{x}</b><br>Net: %{y:+.1f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=NEUTRAL, line_width=1)
    fig.update_layout(
        **_layout("Hourly Arrival vs Departure Flow", height=400),
        barmode="group",
    )
    fig.update_yaxes(title_text="Avg visitors per hour")
    return fig


# ── Weekday analysis ──────────────────────────────────────────────────────────
def weekday_avg_bar(weekday_df: pd.DataFrame) -> go.Figure:
    order = [d for d in _WEEKDAY_ORDER if d in weekday_df["Day_Name"].values]
    w = weekday_df.set_index("Day_Name").reindex(order).reset_index()
    fig = go.Figure(go.Bar(
        x=w["Day_Name"], y=w["Average"].round(1),
        marker_color=BLUE, opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Avg visitors/hr: %{y:,.1f}<extra></extra>",
    ))
    fig.update_layout(**_layout("Avg Visitors per Hour by Weekday", height=340))
    fig.update_yaxes(title_text="Avg visitors / hour")
    return fig


def weekday_total_bar(weekday_df: pd.DataFrame) -> go.Figure:
    order = [d for d in _WEEKDAY_ORDER if d in weekday_df["Day_Name"].values]
    w = weekday_df.set_index("Day_Name").reindex(order).reset_index()
    fig = go.Figure(go.Bar(
        x=w["Day_Name"], y=w["Total"],
        marker_color=PURPLE, opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Total visitors: %{y:,}<extra></extra>",
    ))
    fig.update_layout(**_layout("Total Visitors by Weekday", height=340))
    fig.update_yaxes(title_text="Total visitors")
    return fig


def weekday_normalized_bar(weekday_df: pd.DataFrame) -> go.Figure:
    order = [d for d in _WEEKDAY_ORDER if d in weekday_df["Day_Name"].values]
    w = weekday_df.set_index("Day_Name").reindex(order).reset_index()
    total = w["Total"].sum()
    w["Pct"] = (w["Total"] / total * 100).round(1) if total > 0 else 0
    fig = go.Figure(go.Bar(
        x=w["Day_Name"], y=w["Pct"],
        marker_color=TEAL, opacity=0.85,
        text=w["Pct"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
        hovertemplate="<b>%{x}</b><br>Share: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**_layout("Visitor Share by Weekday (%)", height=360))
    fig.update_yaxes(title_text="% of total visitors", ticksuffix="%")
    return fig


# ── Position breakdown ────────────────────────────────────────────────────────
def position_bar(pos_df: pd.DataFrame) -> go.Figure:
    sorted_df = pos_df.sort_values("Total", ascending=True)
    fig = go.Figure(go.Bar(
        x=sorted_df["Total"], y=sorted_df["Position"].astype(str),
        orientation="h", marker_color=TEAL, opacity=0.85,
        hovertemplate="<b>%{y}</b><br>Visitors: %{x:,}<extra></extra>",
    ))
    fig.update_layout(**_layout("Visitors by Entry Position", height=max(280, len(pos_df) * 70)))
    fig.update_xaxes(title_text="Total visitors")
    return fig


def daily_by_position_chart(visitors: pd.DataFrame) -> go.Figure:
    """Daily visitor trend split by position."""
    pos_daily = (
        visitors.groupby(["Date_Only", "Position"])["Count"]
        .sum().reset_index().sort_values("Date_Only")
    )
    colors = [BLUE, ORANGE, PURPLE, TEAL]
    fig = go.Figure()
    for i, pos in enumerate(pos_daily["Position"].unique()):
        pdf = pos_daily[pos_daily["Position"] == pos]
        fig.add_trace(go.Scatter(
            x=pdf["Date_Only"], y=pdf["Count"], name=str(pos),
            mode="lines", line=dict(color=colors[i % len(colors)], width=2, shape="spline"),
            hovertemplate=f"<b>{pos}</b><br>%{{x}}<br>Visitors: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(**_layout("Daily Visitors by Entry Position", height=360))
    fig.update_yaxes(title_text="Visitors")
    return fig
