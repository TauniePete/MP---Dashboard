"""
data_loader.py
--------------
Loads the finalized sensor CSV and produces two clean DataFrames:
  - visitors : Counter A rows only (Traffic In = visitor entries)
  - flow     : merged hourly In/Out for occupancy flow analysis

Business rules applied here:
  - Maindoor and 156 are the same physical entrance → unified as "Main Entrance"
  - Zero-visitor days (Saturdays that slipped through + holidays/closures) excluded
    from active-day calculations via the 'is_active' flag on the daily series
  - Counter A = Traffic In  (visitor entries) — PRIMARY metric
  - Counter B = Traffic Out (visitor exits)   — flow analysis only
"""

from __future__ import annotations
import os
import streamlit as st
import pandas as pd

_HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_HERE, "..", "data", "finalized_sensor_data.csv")

_DAY_MAP = {2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday"}
_HOUR_MAP = {
    "8:00 AM": 8,  "9:00 AM": 9,  "10:00 AM": 10, "11:00 AM": 11,
    "12:00 PM": 12, "1:00 PM": 13, "2:00 PM": 14,  "3:00 PM": 15,
    "4:00 PM": 16,  "5:00 PM": 17,
}

# Unify both position labels — same physical door, relabelled mid-project
_POSITION_MAP = {"Maindoor": "Main Entrance", "156": "Main Entrance"}


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Parse types, unify position label, add all derived columns."""
    df["Date"]      = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Date_Only"] = df["Date"].dt.date
    df["Day_Name"]  = df["Day"].map(_DAY_MAP).fillna("Unknown")
    df["Hour_Num"]  = df["Time"].map(_HOUR_MAP).fillna(0).astype(int)
    df["Month"]     = df["Date"].dt.to_period("M").astype(str)
    df["AM_PM"]     = df["Time"].apply(lambda t: "AM" if "AM" in str(t) else "PM")
    # Unify position — Maindoor and 156 are the same entrance
    df["Position"]  = df["Position"].astype(str).str.strip().map(_POSITION_MAP).fillna("Main Entrance")
    return df


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        visitors -- Counter A rows only, enriched; position unified to 'Main Entrance'
        flow     -- hourly In vs Out merged per date/hour (for occupancy flow tab)
    """
    if not os.path.exists(DATA_PATH):
        st.error(f"Data file not found: {DATA_PATH}")
        st.stop()

    raw = pd.read_csv(DATA_PATH)
    raw = _enrich(raw)

    # Visitor frame: Counter A only
    visitors = (raw[raw["Type"] == "Counter A"]
                .copy()
                .sort_values(["Date", "Hour_Num"])
                .reset_index(drop=True))

    # Flow frame: hourly In vs Out merged
    in_grp  = (raw[raw["Type"] == "Counter A"]
               .groupby(["Date_Only", "Time", "Hour_Num", "Day_Name"])["Count"]
               .sum().reset_index().rename(columns={"Count": "In"}))
    out_grp = (raw[raw["Type"] == "Counter B"]
               .groupby(["Date_Only", "Time", "Hour_Num"])["Count"]
               .sum().reset_index().rename(columns={"Count": "Out"}))

    flow = (pd.merge(in_grp, out_grp, on=["Date_Only", "Time", "Hour_Num"], how="outer")
            .fillna(0)
            .sort_values(["Date_Only", "Hour_Num"])
            .reset_index(drop=True))
    flow["Net"] = flow["In"] - flow["Out"]

    return visitors, flow


def get_date_bounds(visitors: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    return visitors["Date"].min(), visitors["Date"].max()
