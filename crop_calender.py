"""pages/crop_calendar.py — Crop Calendar: when to sow, grow & harvest"""

import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime

# ── Crop calendar data ─────────────────────────────────────────────────────
# Format: {crop: {state_group: [(activity, start_month, end_month, color)]}}
# Months: 1=Jan … 12=Dec

CALENDAR = {
    "Rice": {
        "North India (Punjab, Haryana, UP)": [
            ("Nursery Sowing",  5, 6,  "#95d5b2"),
            ("Transplanting",   6, 7,  "#52b788"),
            ("Growing",         7, 10, "#2d6a4f"),
            ("Harvesting",     10, 11, "#d4a017"),
        ],
        "South India (AP, Telangana, Karnataka)": [
            ("Kharif Sowing",   6, 7,  "#95d5b2"),
            ("Growing",         7, 10, "#2d6a4f"),
            ("Harvesting",     10, 11, "#d4a017"),
            ("Rabi Sowing",    11, 12, "#52b788"),
            ("Rabi Harvest",    3, 4,  "#d4a017"),
        ],
        "West Bengal, Assam": [
            ("Boro (Winter)",   1, 2,  "#95d5b2"),
            ("Boro Harvest",    5, 6,  "#d4a017"),
            ("Aman Sowing",     6, 7,  "#52b788"),
            ("Aman Harvest",   10, 12, "#d4a017"),
        ],
    },
    "Wheat": {
        "North India (Punjab, Haryana, UP, MP)": [
            ("Sowing",         10, 11, "#95d5b2"),
            ("Growing",        11, 3,  "#2d6a4f"),
            ("Harvesting",      3, 4,  "#d4a017"),
        ],
        "Bihar, West Bengal": [
            ("Sowing",         11, 12, "#95d5b2"),
            ("Growing",        12, 3,  "#2d6a4f"),
            ("Harvesting",      3, 4,  "#d4a017"),
        ],
    },
    "Sugarcane": {
        "Maharashtra, Karnataka": [
            ("Planting",        2, 3,  "#95d5b2"),
            ("Growing",         3, 12, "#2d6a4f"),
            ("Harvesting",     11, 3,  "#d4a017"),
        ],
        "UP, Bihar": [
            ("Spring Planting", 2, 3,  "#95d5b2"),
            ("Autumn Planting", 9, 10, "#52b788"),
            ("Growing",         3, 12, "#2d6a4f"),
            ("Harvesting",     11, 4,  "#d4a017"),
        ],
    },
    "Cotton": {
        "Gujarat, Maharashtra, Telangana": [
            ("Sowing",          5, 6,  "#95d5b2"),
            ("Growing",         6, 11, "#2d6a4f"),
            ("Picking",        10, 2,  "#d4a017"),
        ],
    },
    "Maize": {
        "Kharif (All India)": [
            ("Sowing",          6, 7,  "#95d5b2"),
            ("Growing",         7, 9,  "#2d6a4f"),
            ("Harvesting",      9, 10, "#d4a017"),
        ],
        "Rabi (South & Central)": [
            ("Sowing",         10, 11, "#95d5b2"),
            ("Growing",        11, 2,  "#2d6a4f"),
            ("Harvesting",      2, 3,  "#d4a017"),
        ],
    },
    "Potato": {
        "North India": [
            ("Sowing",         10, 11, "#95d5b2"),
            ("Growing",        11, 1,  "#2d6a4f"),
            ("Harvesting",      1, 2,  "#d4a017"),
        ],
        "West Bengal, Bihar": [
            ("Sowing",         10, 11, "#95d5b2"),
            ("Growing",        11, 2,  "#2d6a4f"),
            ("Harvesting",      2, 3,  "#d4a017"),
        ],
    },
    "Groundnut": {
        "Kharif (All India)": [
            ("Sowing",          6, 7,  "#95d5b2"),
            ("Growing",         7, 10, "#2d6a4f"),
            ("Harvesting",     10, 11, "#d4a017"),
        ],
        "Rabi (AP, Karnataka)": [
            ("Sowing",         10, 11, "#95d5b2"),
            ("Growing",        11, 2,  "#2d6a4f"),
            ("Harvesting",      2, 3,  "#d4a017"),
        ],
    },
    "Soyabean": {
        "MP, Maharashtra, Rajasthan": [
            ("Sowing",          6, 7,  "#95d5b2"),
            ("Growing",         7, 10, "#2d6a4f"),
            ("Harvesting",     10, 10, "#d4a017"),
        ],
    },
    "Onion": {
        "Maharashtra, Karnataka": [
            ("Nursery",        10, 11, "#95d5b2"),
            ("Transplanting",  11, 12, "#52b788"),
            ("Growing",        12, 3,  "#2d6a4f"),
            ("Harvesting",      3, 5,  "#d4a017"),
        ],
    },
}

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

ACTIVITY_TIPS = {
    "Sowing": "Prepare well-tilled seedbed. Ensure soil moisture is adequate.",
    "Nursery Sowing": "Use healthy certified seeds. Treat with fungicide before sowing.",
    "Transplanting": "Transplant 25–30 day old seedlings. Maintain proper spacing.",
    "Nursery": "Maintain nursery in raised beds. Water daily, avoid waterlogging.",
    "Planting": "Select disease-free setts/cuttings. Apply basal fertilizer.",
    "Spring Planting": "Plant in furrows 90 cm apart. Apply FYM before planting.",
    "Autumn Planting": "Good option for ratoon crop. Irrigation is critical.",
    "Growing": "Monitor for pests/diseases. Apply fertilizer in splits.",
    "Harvesting": "Harvest at physiological maturity. Use proper moisture content.",
    "Picking": "Pick bolls after boll burst. Multiple pickings needed.",
    "Boro Harvest": "Drain fields 10 days before harvest. Use combine if possible.",
    "Aman Sowing": "Flash flood-resistant varieties recommended for low-lying areas.",
    "Aman Harvest": "Harvest before dewfall to reduce shattering losses.",
    "Kharif Sowing": "Sow after first monsoon rains when soil moisture is assured.",
    "Rabi Sowing": "Ensure residual moisture or first irrigation before sowing.",
    "Rabi Harvest": "Harvest in early morning to avoid grain shattering.",
}


def month_bar(activities):
    """Render a 12-month visual bar for activities."""
    cells = [""] * 12
    colors = ["#f0faf3"] * 12

    for activity, start, end, color in activities:
        s, e = start - 1, end - 1
        if s <= e:
            for i in range(s, e + 1):
                cells[i] = activity[:3]
                colors[i] = color
        else:  # wraps year
            for i in range(s, 12):
                cells[i] = activity[:3]
                colors[i] = color
            for i in range(0, e + 1):
                cells[i] = activity[:3]
                colors[i] = color
    return cells, colors


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>📅 Crop Calendar</h1>
        <p>Month-by-month sowing, growing, and harvesting schedules for major Indian crops</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Crop selector ──────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 3])
    with col1:
        sel_crop = st.selectbox("Select Crop", sorted(CALENDAR.keys()))
    with col2:
        current_month = datetime.now().month
        st.markdown(f"""
        <div class="card-green" style="padding:.75rem 1.25rem;margin-top:1.75rem;">
            📅 Today: <b>{datetime.now().strftime('%B %d, %Y')}</b>
            &nbsp;·&nbsp; Current month: <b style="color:#1a472a;">{MONTHS[current_month-1]}</b>
        </div>
        """, unsafe_allow_html=True)

    crop_data = CALENDAR[sel_crop]

    # ── Legend ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;gap:1.5rem;margin:.75rem 0 1.5rem;flex-wrap:wrap;">
        <span><span style="display:inline-block;width:14px;height:14px;border-radius:3px;
              background:#95d5b2;margin-right:6px;vertical-align:middle;"></span>Sowing / Nursery</span>
        <span><span style="display:inline-block;width:14px;height:14px;border-radius:3px;
              background:#2d6a4f;margin-right:6px;vertical-align:middle;"></span>Growing</span>
        <span><span style="display:inline-block;width:14px;height:14px;border-radius:3px;
              background:#d4a017;margin-right:6px;vertical-align:middle;"></span>Harvesting</span>
        <span><span style="display:inline-block;width:14px;height:14px;border-radius:3px;
              background:#52b788;margin-right:6px;vertical-align:middle;"></span>Transplanting</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Calendar grid for each region ─────────────────────────────────────
    for region, activities in crop_data.items():
        st.markdown(f"<div class='section-title' style='font-size:1rem;'>📍 {region}</div>",
                    unsafe_allow_html=True)

        cells, colors = month_bar(activities)

        # Build HTML grid
        month_html = "<div style='display:grid;grid-template-columns:repeat(12,1fr);gap:4px;margin-bottom:1rem;'>"
        for i, (month, cell, color) in enumerate(zip(MONTHS, cells, colors)):
            is_current = (i + 1) == current_month
            border = "2px solid #1a472a" if is_current else "1px solid #e2e8f0"
            month_html += f"""
            <div style="text-align:center;border-radius:8px;overflow:hidden;border:{border};">
                <div style="background:#1a472a;color:white;font-size:.65rem;
                            font-weight:700;padding:3px 0;">{month}</div>
                <div style="background:{color};padding:8px 2px;font-size:.7rem;
                            font-weight:600;color:white;min-height:36px;
                            display:flex;align-items:center;justify-content:center;">
                    {cell if cell else ""}
                </div>
            </div>"""
        month_html += "</div>"
        st.markdown(month_html, unsafe_allow_html=True)

        # Activity strips with tips
        for activity, start, end, color in activities:
            end_label = MONTHS[end - 1]
            start_label = MONTHS[start - 1]
            tip = ACTIVITY_TIPS.get(activity, "Follow standard agronomic practices.")
            st.markdown(f"""
            <div class="cal-card">
                <div class="month">{start_label} → {end_label}</div>
                <div class="activity">
                    <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                          background:{color};margin-right:6px;"></span>
                    {activity}
                </div>
                <div style="color:#718096;font-size:.82rem;margin-top:.3rem;">{tip}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── What to do this month ──────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title' style='font-size:1.1rem;'>🗓️ What to do in {MONTHS[current_month-1]}</div>",
                unsafe_allow_html=True)

    this_month_tasks = []
    for region, activities in crop_data.items():
        for activity, start, end, color in activities:
            in_range = (start <= end and start <= current_month <= end) or \
                       (start > end and (current_month >= start or current_month <= end))
            if in_range:
                this_month_tasks.append((region, activity, color))

    if this_month_tasks:
        cols = st.columns(min(len(this_month_tasks), 3))
        for col, (region, activity, color) in zip(cols, this_month_tasks):
            with col:
                st.markdown(f"""
                <div class="card" style="border-top:3px solid {color};padding:1.25rem;">
                    <div style="font-size:.75rem;color:#718096;font-weight:600;
                                text-transform:uppercase;letter-spacing:.06em;">{region}</div>
                    <div style="font-weight:700;font-size:1rem;color:#1a472a;
                                margin-top:.4rem;">{activity}</div>
                    <div style="color:#718096;font-size:.82rem;margin-top:.4rem;">
                        {ACTIVITY_TIPS.get(activity,'Follow standard practices.')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card-gold">
            <b>😴 Off-Season</b> — No major activities for this crop in the current month.
            Plan and prepare for the next sowing season.
        </div>
        """, unsafe_allow_html=True)

    # ── All crops quick view ───────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("📋 All Crops — Harvest Months Quick Reference"):
        harvest_info = {
            "Rice (Kharif)": "Oct–Nov", "Rice (Rabi)": "Mar–Apr",
            "Wheat": "Mar–Apr", "Sugarcane": "Nov–Mar",
            "Cotton": "Oct–Feb", "Maize (Kharif)": "Sep–Oct",
            "Maize (Rabi)": "Feb–Mar", "Potato": "Jan–Mar",
            "Groundnut (Kharif)": "Oct–Nov", "Groundnut (Rabi)": "Feb–Mar",
            "Soyabean": "Oct", "Onion": "Mar–May",
            "Tomato": "Dec–Feb / Jun–Aug", "Chilli": "Dec–Mar",
            "Turmeric": "Jan–Mar", "Ginger": "Dec–Feb",
        }
        hdf = pd.DataFrame(harvest_info.items(), columns=["Crop", "Harvest Months"])
        st.dataframe(hdf, use_container_width=True, hide_index=True, height=320)