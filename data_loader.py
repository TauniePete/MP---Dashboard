"""
metrics.py — Museum Visitor Analytics
All functions operate on:
  visitors : Counter A (Traffic In) only — visitor entries, position unified
  flow     : merged hourly In/Out frame  — occupancy flow analysis

Active days definition:
  Days where total visitor count > 0 (excludes Saturday artifacts that
  slipped through data cleaning, and holiday/closure zero-count days).
  53,960 total visitors / 421 active days = 128 avg daily visitors.
"""

from __future__ import annotations
import pandas as pd

_WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def compute_kpis(visitors: pd.DataFrame, flow: pd.DataFrame) -> dict:
    """Executive KPIs — all based on visitor entries (Counter A)."""
    if visitors.empty:
        return {k: "N/A" for k in [
            "total_visitors", "avg_daily_visitors", "peak_day", "peak_day_count",
            "peak_hour", "peak_hour_visitors", "active_days", "busiest_weekday",
        ]}

    # Sum per day first — then derive all day-level stats
    daily  = visitors.groupby("Date_Only")["Count"].sum()
    active = daily[daily > 0]          # exclude zero-visitor days (closures/artifacts)
    hourly = visitors.groupby("Time")["Count"].sum()
    wk_avg = visitors.groupby("Day_Name")["Count"].mean()

    return {
        "total_visitors":     f"{int(active.sum()):,}",
        "avg_daily_visitors": f"{active.sum() / len(active):,.0f}",   # 53960 / 421 = 128
        "peak_day":           pd.Timestamp(active.idxmax()).strftime("%B %d, %Y"),
        "peak_day_count":     f"{int(active.max()):,}",
        "peak_hour":          hourly.idxmax(),
        "peak_hour_visitors": f"{int(hourly.max()):,}",
        "active_days":        f"{len(active):,}",
        "busiest_weekday":    wk_avg.idxmax(),
    }


def daily_visitor_series(visitors: pd.DataFrame) -> pd.DataFrame:
    """Daily visitor totals with 7-day rolling average. Excludes zero days from rolling."""
    if visitors.empty:
        return pd.DataFrame(columns=["Date_Only", "Visitors", "Rolling_Avg"])
    daily = (visitors.groupby("Date_Only")["Count"].sum()
             .reset_index().rename(columns={"Count": "Visitors"})
             .sort_values("Date_Only"))
    # Only include active days in trend chart — zeros distort rolling avg
    daily = daily[daily["Visitors"] > 0].copy()
    daily["Rolling_Avg"] = daily["Visitors"].rolling(7, min_periods=1).mean()
    return daily


def monthly_visitors(visitors: pd.DataFrame) -> pd.DataFrame:
    """Monthly visitor totals."""
    if visitors.empty:
        return pd.DataFrame(columns=["Month", "Visitors"])
    return (visitors.groupby("Month")["Count"].sum()
            .reset_index().rename(columns={"Count": "Visitors"})
            .sort_values("Month"))


def hourly_visitors(visitors: pd.DataFrame) -> pd.DataFrame:
    """Total visitors per hour slot, sorted by hour."""
    if visitors.empty:
        return pd.DataFrame(columns=["Time", "Hour_Num", "Visitors"])
    return (visitors.groupby(["Time", "Hour_Num"])["Count"].sum()
            .reset_index().rename(columns={"Count": "Visitors"})
            .sort_values("Hour_Num"))


def am_pm_visitors(visitors: pd.DataFrame) -> pd.DataFrame:
    """Visitor counts split AM vs PM."""
    if visitors.empty:
        return pd.DataFrame(columns=["AM_PM", "Visitors"])
    return (visitors.groupby("AM_PM")["Count"].sum()
            .reset_index().rename(columns={"Count": "Visitors"}))


def weekday_summary(visitors: pd.DataFrame) -> pd.DataFrame:
    """Average and total visitors per weekday (active days only), Mon–Fri ordered."""
    if visitors.empty:
        return pd.DataFrame(columns=["Day_Name", "Total", "Average"])
    # Use only active days for per-day averages
    active = visitors[visitors["Count"] > 0]
    grp = (active.groupby(["Date_Only", "Day_Name"])["Count"]
           .sum().reset_index()
           .groupby("Day_Name")["Count"]
           .agg(Total="sum", Average="mean").reset_index())
    grp["Day_Name"] = pd.Categorical(grp["Day_Name"], categories=_WEEKDAY_ORDER, ordered=True)
    return grp.sort_values("Day_Name")


def weekday_hour_pivot(visitors: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows=weekday, cols=time slot, values=avg visitors. For heatmap."""
    if visitors.empty:
        return pd.DataFrame()
    pdata = (visitors.groupby(["Day_Name", "Time", "Hour_Num"])["Count"]
             .mean().reset_index().sort_values("Hour_Num"))
    hour_order = pdata.drop_duplicates("Time").set_index("Time")["Hour_Num"].to_dict()
    pivot = pdata.pivot_table(index="Day_Name", columns="Time", values="Count", aggfunc="mean")
    col_order = sorted(pivot.columns, key=lambda t: hour_order.get(t, 99))
    row_order  = [d for d in _WEEKDAY_ORDER if d in pivot.index]
    return pivot[col_order].reindex(row_order)


def position_summary(visitors: pd.DataFrame) -> pd.DataFrame:
    """Visitor totals by entry point (position already unified in data_loader)."""
    if visitors.empty:
        return pd.DataFrame(columns=["Position", "Total", "Average", "Records"])
    return (visitors.groupby("Position")["Count"]
            .agg(Total="sum", Average="mean", Records="count")
            .reset_index().sort_values("Total", ascending=False))


def avg_flow_by_hour(flow: pd.DataFrame) -> pd.DataFrame:
    """Average hourly arrivals, departures, and net flow across all active days."""
    if flow.empty:
        return pd.DataFrame(columns=["Hour_Num", "Time", "In", "Out", "Net"])
    avg = (flow.groupby(["Hour_Num", "Time"])[["In", "Out", "Net"]]
           .mean().round(1).reset_index().sort_values("Hour_Num"))
    return avg
