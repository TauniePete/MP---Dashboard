"""
app.py — Museum Visitor Analytics Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Museum Visitor Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import load_data
from utils.filters import render_sidebar_filters, apply_filters
from utils import metrics as m
from utils import charts as c

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

.kpi-card {
    background: #ffffff; border: 1px solid #E5E7EB;
    border-radius: 12px; padding: 20px 24px; text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-label {
    font-size: 0.70rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6B7280; margin-bottom: 6px;
}
.kpi-value { font-size: 1.65rem; font-weight: 700; color: #111827; line-height: 1.2; }
.kpi-sub   { font-size: 0.76rem; color: #9CA3AF; margin-top: 4px; }

.section-header {
    font-size: 1.0rem; font-weight: 700; color: #111827;
    border-left: 4px solid #1A56DB; padding-left: 12px;
    margin: 24px 0 14px 0;
}
.insight-box {
    background: #EFF6FF; border-left: 4px solid #1A56DB;
    border-radius: 8px; padding: 12px 16px;
    font-size: 0.86rem; color: #1E3A8A; margin-bottom: 10px;
}
.note-box {
    background: #FFF7ED; border-left: 4px solid #F97316;
    border-radius: 8px; padding: 12px 16px;
    font-size: 0.84rem; color: #9A3412; margin-bottom: 10px;
}
section[data-testid="stSidebar"] { background: #F3F4F6; border-right: 1px solid #E5E7EB; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 2px solid #E5E7EB; }
.stTabs [data-baseweb="tab"] { font-size: 0.84rem; font-weight: 500; padding: 8px 18px; border-radius: 6px 6px 0 0; }
.stTabs [aria-selected="true"] { background: #1A56DB !important; color: white !important; }
hr { border: none; border-top: 1px solid #E5E7EB; margin: 20px 0; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def kpi_card(label, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )

def section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def insight(text):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

def note(text):
    st.markdown(f'<div class="note-box">ℹ️ {text}</div>', unsafe_allow_html=True)

def chart_caption(text):
    """Subtle italic caption rendered below a chart to help readers interpret it."""
    st.markdown(
        f'<p style="font-size:0.76rem;color:#9CA3AF;margin:-6px 0 14px 4px;font-style:italic;">{text}</p>',
        unsafe_allow_html=True,
    )


# ── Load data ─────────────────────────────────────────────────────────────────
visitors_full, flow_full = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:12px 0 20px 0;">'
        '<div style="font-size:1.1rem;font-weight:700;color:#111827;">🏛️ Visitor Analytics</div>'
        '<div style="font-size:0.75rem;color:#6B7280;margin-top:2px;">MP Museum · Final Report</div>'
        '</div>',
        unsafe_allow_html=True,
    )

filters = render_sidebar_filters(visitors_full)
visitors, flow = apply_filters(visitors_full, flow_full, filters)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:6px 0 4px 0;">'
    '<h1 style="font-size:1.5rem;font-weight:800;color:#111827;margin:0;">Museum Visitor Analytics Dashboard</h1>'
    '<p style="color:#6B7280;font-size:0.86rem;margin:4px 0 0 0;">'
    'Visitor entries (Traffic In) · Business hours 8 AM–5 PM · Weekdays only'
    '</p></div>',
    unsafe_allow_html=True,
)

if visitors.empty:
    st.warning("⚠️ No data matches the current filters. Adjust the sidebar.")
    st.stop()

date_range_str = (
    f"{pd.Timestamp(filters['date_start']).strftime('%b %d, %Y')} — "
    f"{pd.Timestamp(filters['date_end']).strftime('%b %d, %Y')}"
)
st.markdown(
    f'<div style="font-size:0.77rem;color:#6B7280;margin-bottom:18px;">'
    f'Showing <b style="color:#1A56DB;">{len(visitors):,}</b> records &nbsp;·&nbsp; {date_range_str}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Executive Summary",
    "📈 Daily Trends",
    "🕐 Hourly Analysis",
    "📅 Weekday Analysis",
    "🔄 Occupancy Flow",
    "🗂️ Raw Data",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    kpis = m.compute_kpis(visitors, flow)

    section_header("Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Visitors", kpis["total_visitors"], "selected period")
    with c2: kpi_card("Avg Daily Visitors", kpis["avg_daily_visitors"], "per active open day")
    with c3: kpi_card("Peak Visitor Day", kpis["peak_day"], f"{kpis['peak_day_count']} visitors")
    with c4: kpi_card("Busiest Hour", kpis["peak_hour"], f"{kpis['peak_hour_visitors']} total")

    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5: kpi_card("Active Open Days", kpis["active_days"])
    with c6: kpi_card("Busiest Weekday", kpis["busiest_weekday"], "highest avg visitors")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        section_header("Visitor Trend Overview")
        daily = m.daily_visitor_series(visitors)
        st.plotly_chart(c.trend_overview(daily), use_container_width=True,
                        config={"displayModeBar": False})
        chart_caption("Bars show daily visitor count. The dotted line is a 7-day rolling average that smooths day-to-day variation to reveal the underlying trend.")
    with col_b:
        section_header("Summary Insights")
        st.markdown("<br>", unsafe_allow_html=True)
        insight(f"<b>{kpis['total_visitors']}</b> total visitors across "
                f"<b>{kpis['active_days']}</b> active open days in the selected period.")
        insight(f"Average of <b>{kpis['avg_daily_visitors']}</b> visitors per active open day in the selected period.")
        insight(f"Busiest single day was <b>{kpis['peak_day']}</b> with "
                f"<b>{kpis['peak_day_count']}</b> visitors.")
        insight(f"Peak visiting hour is <b>{kpis['peak_hour']}</b> — "
                f"plan staffing accordingly.")
        insight(f"<b>{kpis['busiest_weekday']}</b> consistently draws the most visitors "
                f"on average.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DAILY TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header("Daily Visitor Trends")

    view = st.radio("Aggregation", ["Daily", "Monthly"], horizontal=True, key="daily_view")
    daily_f = m.daily_visitor_series(visitors)

    if view == "Daily":
        st.plotly_chart(c.daily_visitors_chart(daily_f), use_container_width=True)
        chart_caption("Each bar is one active open day's total visitor count. The dotted orange line is a 7-day rolling average — hover over any bar for the exact date and count.")
    else:
        st.plotly_chart(c.monthly_visitors_chart(m.monthly_visitors(visitors)),
                        use_container_width=True)
        chart_caption("Each bar shows the total visitors recorded in that calendar month.")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Period Statistics")
    s1, s2, s3, s4 = st.columns(4)
    dv = daily_f["Visitors"]
    with s1: kpi_card("Total Visitors (filtered)", f"{int(dv.sum()):,}")
    with s2: kpi_card("Peak Day (filtered)", f"{int(dv.max()):,}", "visitors")
    with s3: kpi_card("Avg Daily (filtered)", f"{dv.mean():,.0f}", "visitors/day")
    with s4: kpi_card("Days in Selection", f"{len(daily_f):,}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HOURLY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section_header("Hourly Visitor Distribution")
    hourly_f = m.hourly_visitors(visitors)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(c.hourly_visitors_chart(hourly_f), use_container_width=True)
        chart_caption("Total visitors recorded at each hour, summed across all active open days. Taller bars indicate higher overall traffic at that hour.")
    with col2:
        st.plotly_chart(c.am_pm_donut(m.am_pm_visitors(visitors)), use_container_width=True)
        chart_caption("Share of all visitors arriving before noon (AM) vs. noon onward (PM).")

    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns([2, 3])
    with col3:
        section_header("Busiest Hours Ranking")
        st.plotly_chart(c.busiest_hours_bar(hourly_f), use_container_width=True)
        chart_caption("Hours ranked from quietest to busiest. The top 3 busiest hours are highlighted in blue.")
    with col4:
        section_header("Visitor Heatmap — Weekday × Hour")
        pivot = m.weekday_hour_pivot(visitors)
        st.plotly_chart(c.weekday_hour_heatmap(pivot), use_container_width=True)
        chart_caption("Darker blue = more visitors on average. Read across a row to see how a weekday's traffic builds through the day; read down a column to compare the same hour across weekdays.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WEEKDAY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section_header("Weekday Visitor Patterns")
    wkdf = m.weekday_summary(visitors)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.weekday_avg_bar(wkdf), use_container_width=True)
        chart_caption("Average visitors per active open day for each weekday. Excludes holidays and closure days.")
    with col2:
        st.plotly_chart(c.weekday_total_bar(wkdf), use_container_width=True)
        chart_caption("Cumulative visitors recorded on each weekday across the full monitoring period.")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Visitor Share by Weekday")
    st.plotly_chart(c.weekday_normalized_bar(wkdf), use_container_width=True)
    chart_caption("Each weekday's share of total visitors across the entire period. A perfectly even distribution would show 20% per day.")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Weekday Summary Table")
    disp = wkdf.copy()
    disp["Average"] = disp["Average"].round(1)
    disp.columns = ["Weekday", "Total Visitors", "Avg Visitors / Hour"]
    st.dataframe(disp.set_index("Weekday"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — OCCUPANCY FLOW
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section_header("Hourly Arrival vs Departure Flow")

    note(
        "This chart uses both counters: <b>Counter A (arrivals)</b> and "
        "<b>Counter B (departures)</b>. Net flow shows whether the museum is "
        "net-filling or net-emptying each hour on average — useful for staffing planning. "
        "Because monitoring starts at 8 AM, visitors who arrived before opening "
        "may appear as departures without a matching entry, so net values near "
        "opening time should be interpreted with care."
    )

    flow_avg = m.avg_flow_by_hour(flow)
    st.plotly_chart(c.occupancy_flow_chart(flow_avg), use_container_width=True)
    chart_caption("Blue bars = average arrivals per hour. Orange bars = average departures. Teal line = net flow (arrivals minus departures). A positive net means more people are entering than leaving — the museum is filling up. A negative net means it is emptying.")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Average Hourly Flow Table")

    flow_disp = flow_avg[["Time", "In", "Out", "Net"]].copy()
    flow_disp.columns = ["Hour", "Avg Arrivals", "Avg Departures", "Net Flow"]
    flow_disp["Net Flow"] = flow_disp["Net Flow"].apply(lambda v: f"{v:+.1f}")
    st.dataframe(flow_disp.set_index("Hour"), use_container_width=True)

    insight(
        "Hours with positive net flow (more arriving than leaving) indicate "
        "when occupancy is building — schedule extra floor staff during these windows."
    )
    insight(
        "Hours with negative net flow (more leaving than arriving) signal "
        "the crowd is thinning — useful for planning closing procedures."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — RAW DATA
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    section_header("Raw Visitor Data Explorer")

    search = st.text_input(
        "🔍 Search", placeholder="e.g. Maindoor, Monday, 11:00 AM …",
        key="raw_search",
    )

    disp_raw = visitors[["Date", "Time", "Count", "Position", "Day_Name"]].copy()
    disp_raw.rename(columns={"Day_Name": "Weekday", "Count": "Visitors"}, inplace=True)
    disp_raw["Date"] = disp_raw["Date"].dt.strftime("%B %d, %Y")

    if search.strip():
        mask = disp_raw.apply(
            lambda col: col.astype(str).str.contains(search.strip(), case=False, na=False)
        ).any(axis=1)
        disp_raw = disp_raw[mask]

    st.markdown(
        f'<div style="font-size:0.8rem;color:#6B7280;margin-bottom:8px;">'
        f'Showing <b>{len(disp_raw):,}</b> of <b>{len(visitors):,}</b> records</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(disp_raw, use_container_width=True, height=460, hide_index=True)

    st.download_button(
        "⬇️ Export to CSV",
        data=disp_raw.to_csv(index=False).encode("utf-8"),
        file_name="museum_visitors_export.csv",
        mime="text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<hr><div style="text-align:center;font-size:0.74rem;color:#9CA3AF;padding:6px 0;">'
    'Museum Visitor Analytics &nbsp;·&nbsp; Traffic In (Counter A) = Visitor Entries &nbsp;·&nbsp;'
    ' Business Hours 8 AM–5 PM &nbsp;·&nbsp; Weekdays Only'
    '</div>',
    unsafe_allow_html=True,
)