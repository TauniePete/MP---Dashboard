"""
filters.py — Sidebar filter rendering and visitor DataFrame filtering.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def render_sidebar_filters(visitors: pd.DataFrame) -> dict:
    st.sidebar.markdown("## 🎛️ Filters")
    st.sidebar.markdown("---")

    min_date = visitors["Date"].min().date()
    max_date = visitors["Date"].max().date()

    st.sidebar.markdown("**Date Range**")
    date_start = st.sidebar.date_input("From", value=min_date, min_value=min_date, max_value=max_date, key="filter_date_start")
    date_end   = st.sidebar.date_input("To",   value=max_date, min_value=min_date, max_value=max_date, key="filter_date_end")
    st.sidebar.markdown("---")

    st.sidebar.markdown("**Weekdays**")
    available = [d for d in WEEKDAYS if d in visitors["Day_Name"].unique()]
    selected_days = st.sidebar.multiselect("Select days", options=available, default=available, key="filter_days")
    st.sidebar.markdown("---")

    st.sidebar.markdown("**Position**")
    all_pos = sorted(visitors["Position"].dropna().unique().tolist())
    selected_pos = st.sidebar.multiselect("Select positions", options=all_pos, default=all_pos, key="filter_positions")
    st.sidebar.markdown("---")
    st.sidebar.caption("Visitor charts use Counter A (entries) only. Occupancy uses both counters.")

    return {"date_start": date_start, "date_end": date_end, "days": selected_days, "positions": selected_pos}


def apply_filters(visitors: pd.DataFrame, flow: pd.DataFrame, filters: dict) -> tuple:
    """
    Apply filters to both visitor (Counter A) and flow DataFrames.
    Returns (filtered_visitors, filtered_flow).
    """
    start = pd.Timestamp(filters["date_start"])
    end   = pd.Timestamp(filters["date_end"])

    fv = visitors[(visitors["Date"] >= start) & (visitors["Date"] <= end)].copy()
    ff = flow[(pd.to_datetime(flow["Date_Only"]) >= start) & (pd.to_datetime(flow["Date_Only"]) <= end)].copy()

    if filters["days"]:
        fv = fv[fv["Day_Name"].isin(filters["days"])]
        ff = ff[ff["Day_Name"].isin(filters["days"])]

    if filters["positions"]:
        fv = fv[fv["Position"].isin(filters["positions"])]
        # flow doesn't have Position — filter not applied (position is a visitor-frame concept)

    return fv.reset_index(drop=True), ff.reset_index(drop=True)
