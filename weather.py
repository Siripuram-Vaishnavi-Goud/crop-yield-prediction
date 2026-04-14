"""pages/weather.py — Weather Integration (Open-Meteo free API, no key needed)"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from pages.helpers import STATES

# State → (lat, lon, display city)
STATE_COORDS = {
    "Andhra Pradesh":     (15.9129, 79.7400, "Vijayawada"),
    "Arunachal Pradesh":  (27.0844, 93.6053, "Itanagar"),
    "Assam":              (26.2006, 92.9376, "Guwahati"),
    "Bihar":              (25.0961, 85.3131, "Patna"),
    "Chhattisgarh":       (21.2787, 81.8661, "Raipur"),
    "Delhi":              (28.6139, 77.2090, "New Delhi"),
    "Goa":                (15.2993, 74.1240, "Panaji"),
    "Gujarat":            (23.2156, 72.6369, "Ahmedabad"),
    "Haryana":            (29.0588, 76.0856, "Chandigarh"),
    "Himachal Pradesh":   (31.1048, 77.1734, "Shimla"),
    "Jammu and Kashmir":  (34.0837, 74.7973, "Srinagar"),
    "Jharkhand":          (23.6102, 85.2799, "Ranchi"),
    "Karnataka":          (12.9716, 77.5946, "Bengaluru"),
    "Kerala":             (8.5241,  76.9366, "Thiruvananthapuram"),
    "Madhya Pradesh":     (23.2599, 77.4126, "Bhopal"),
    "Maharashtra":        (19.0760, 72.8777, "Mumbai"),
    "Manipur":            (24.6637, 93.9063, "Imphal"),
    "Meghalaya":          (25.5788, 91.8933, "Shillong"),
    "Mizoram":            (23.1645, 92.9376, "Aizawl"),
    "Nagaland":           (25.6751, 94.1086, "Kohima"),
    "Odisha":             (20.2961, 85.8245, "Bhubaneswar"),
    "Puducherry":         (11.9416, 79.8083, "Puducherry"),
    "Punjab":             (30.7333, 76.7794, "Chandigarh"),
    "Sikkim":             (27.3389, 88.6065, "Gangtok"),
    "Tamil Nadu":         (13.0827, 80.2707, "Chennai"),
    "Telangana":          (17.3850, 78.4867, "Hyderabad"),
    "Tripura":            (23.9408, 91.9882, "Agartala"),
    "Uttar Pradesh":      (26.8467, 80.9462, "Lucknow"),
    "Uttarakhand":        (30.3165, 78.0322, "Dehradun"),
    "West Bengal":        (22.5726, 88.3639, "Kolkata"),
}

WMO_CODES = {
    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Fog", 48:"Icy fog", 51:"Light drizzle", 53:"Drizzle", 55:"Heavy drizzle",
    61:"Light rain", 63:"Moderate rain", 65:"Heavy rain",
    71:"Light snow", 73:"Moderate snow", 75:"Heavy snow",
    80:"Light showers", 81:"Showers", 82:"Heavy showers",
    95:"Thunderstorm", 96:"Thunderstorm+hail", 99:"Severe thunderstorm",
}

WEATHER_ICONS = {
    0:"☀️", 1:"🌤️", 2:"⛅", 3:"☁️",
    45:"🌫️", 48:"🌫️", 51:"🌦️", 53:"🌦️", 55:"🌧️",
    61:"🌧️", 63:"🌧️", 65:"🌧️",
    71:"❄️", 73:"❄️", 75:"❄️",
    80:"🌦️", 81:"🌧️", 82:"⛈️",
    95:"⛈️", 96:"⛈️", 99:"⛈️",
}


@st.cache_data(ttl=1800)  # cache 30 min
def fetch_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,"
            f"wind_speed_10m,weather_code,apparent_temperature"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            f"weather_code,wind_speed_10m_max"
            f"&timezone=Asia%2FKolkata&forecast_days=7"
        )
        r = requests.get(url, timeout=8)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_rainfall_history(lat, lon):
    try:
        end   = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=precipitation_sum"
            f"&timezone=Asia%2FKolkata"
            f"&start_date={start}&end_date={end}"
        )
        r = requests.get(url, timeout=8)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>🌦️ Weather & Rainfall</h1>
        <p>Live weather conditions and 90-day rainfall history for any Indian state</p>
    </div>
    """, unsafe_allow_html=True)

    # ── State picker ───────────────────────────────────────────────────────
    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        sel_state = st.selectbox("Select State", sorted(STATE_COORDS.keys()))

    lat, lon, city = STATE_COORDS[sel_state]

    with col_info:
        st.markdown(f"""
        <div class="card-green" style="padding:1rem 1.5rem; margin-top:1.75rem;">
            📍 Showing weather for <b>{city}, {sel_state}</b>
            &nbsp;·&nbsp; Lat {lat:.2f}° N, Lon {lon:.2f}° E
            &nbsp;·&nbsp; <span style="color:#718096;font-size:.85rem;">
            Data: Open-Meteo (no API key needed)</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Fetch ──────────────────────────────────────────────────────────────
    with st.spinner("Fetching live weather data..."):
        data = fetch_weather(lat, lon)

    if not data or "current" not in data:
        st.error("⚠️ Could not fetch weather data. Check your internet connection.")
        _show_static_fallback(sel_state)
        return

    cur = data["current"]
    daily = data.get("daily", {})

    # ── Current conditions ─────────────────────────────────────────────────
    wcode = cur.get("weather_code", 0)
    icon  = WEATHER_ICONS.get(wcode, "🌡️")
    desc  = WMO_CODES.get(wcode, "Unknown")

    st.markdown(f"""
    <div class="page-hero" style="padding:2rem 2.5rem; margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap;">
            <div style="font-size:4rem;">{icon}</div>
            <div>
                <div style="font-family:Lora,serif;font-size:2.8rem;font-weight:700;
                            color:white;line-height:1;">
                    {cur.get('temperature_2m','--')}°C
                </div>
                <div style="color:rgba(255,255,255,.8);font-size:1rem;">{desc}</div>
                <div style="color:rgba(255,255,255,.6);font-size:.85rem;margin-top:.25rem;">
                    Feels like {cur.get('apparent_temperature','--')}°C
                </div>
            </div>
            <div style="margin-left:auto;text-align:right;">
                <div style="color:rgba(255,255,255,.85);font-size:.9rem;">
                    💧 Humidity: {cur.get('relative_humidity_2m','--')}%
                </div>
                <div style="color:rgba(255,255,255,.85);font-size:.9rem;margin-top:.3rem;">
                    🌬️ Wind: {cur.get('wind_speed_10m','--')} km/h
                </div>
                <div style="color:rgba(255,255,255,.85);font-size:.9rem;margin-top:.3rem;">
                    🌧️ Precipitation: {cur.get('precipitation','--')} mm
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperature",    f"{cur.get('temperature_2m','--')}°C")
    c2.metric("Humidity",       f"{cur.get('relative_humidity_2m','--')}%")
    c3.metric("Wind Speed",     f"{cur.get('wind_speed_10m','--')} km/h")
    c4.metric("Precipitation",  f"{cur.get('precipitation','--')} mm")

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── 7-day forecast ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>📅 7-Day Forecast</div>",
                unsafe_allow_html=True)

    if daily.get("time"):
        cols = st.columns(7)
        for i, (col, date_str) in enumerate(zip(cols, daily["time"])):
            try:
                d    = datetime.strptime(date_str, "%Y-%m-%d")
                day  = d.strftime("%a")
                wc   = daily.get("weather_code", [0]*7)[i]
                tmax = daily.get("temperature_2m_max", ["--"]*7)[i]
                tmin = daily.get("temperature_2m_min", ["--"]*7)[i]
                rain = daily.get("precipitation_sum", [0]*7)[i]
                ic   = WEATHER_ICONS.get(wc, "🌡️")
                with col:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;padding:1rem .5rem;">
                        <div style="font-weight:600;font-size:.85rem;color:#718096;">{day}</div>
                        <div style="font-size:1.8rem;margin:.3rem 0;">{ic}</div>
                        <div style="font-weight:700;color:#1a472a;font-size:.9rem;">{tmax}°</div>
                        <div style="color:#718096;font-size:.8rem;">{tmin}°</div>
                        <div style="color:#3b82f6;font-size:.75rem;margin-top:.3rem;">
                            💧 {rain} mm</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception:
                pass

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── 90-day rainfall chart ──────────────────────────────────────────────
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>🌧️ 90-Day Rainfall History</div>",
                unsafe_allow_html=True)

    with st.spinner("Loading rainfall history..."):
        hist = fetch_rainfall_history(lat, lon)

    if hist and "daily" in hist:
        import pandas as pd
        import plotly.express as px
        hdf = pd.DataFrame({
            "Date": pd.to_datetime(hist["daily"]["time"]),
            "Rainfall (mm)": hist["daily"]["precipitation_sum"],
        })
        fig = px.bar(hdf, x="Date", y="Rainfall (mm)",
                     color_discrete_sequence=["#52b788"])
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10,b=10,l=0,r=0), height=280,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f0f4f0"),
            font=dict(family="DM Sans"),
        )
        total = hdf["Rainfall (mm)"].sum()
        avg   = hdf["Rainfall (mm)"].mean()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total (90 days)", f"{total:.1f} mm")
        m2.metric("Daily Average",   f"{avg:.1f} mm")
        m3.metric("Rainy Days",      f"{(hdf['Rainfall (mm)'] > 1).sum()} days")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Rainfall history unavailable offline.")

    # ── Agricultural advisory ──────────────────────────────────────────────
    _show_advisory(cur.get("temperature_2m", 25),
                   cur.get("relative_humidity_2m", 60),
                   cur.get("precipitation", 0))


def _show_advisory(temp, humidity, rain):
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>🌾 Agricultural Advisory</div>",
                unsafe_allow_html=True)

    tips = []
    if temp > 35:
        tips.append(("🌡️ High Temperature", "Consider drought-resistant varieties. Irrigate in early morning or evening.", "#e74c3c"))
    elif temp < 10:
        tips.append(("❄️ Cold Alert", "Protect sensitive crops from frost. Avoid planting warm-season crops.", "#3b82f6"))
    else:
        tips.append(("✅ Optimal Temperature", f"{temp}°C is suitable for most crop varieties.", "#2ecc71"))

    if humidity > 80:
        tips.append(("💧 High Humidity", "Risk of fungal diseases. Ensure good airflow and consider fungicide.", "#e67e22"))
    elif humidity < 30:
        tips.append(("🏜️ Low Humidity", "Crops may need additional irrigation. Monitor soil moisture.", "#f39c12"))

    if rain > 10:
        tips.append(("🌧️ Heavy Rain", "Ensure good drainage to prevent waterlogging. Delay fertilizer application.", "#3b82f6"))
    elif rain == 0:
        tips.append(("☀️ No Rain", "Check soil moisture and irrigate if needed.", "#d4a017"))

    cols = st.columns(len(tips))
    for col, (title, msg, color) in zip(cols, tips):
        with col:
            st.markdown(f"""
            <div class="card" style="border-top:3px solid {color};padding:1.25rem;">
                <div style="font-weight:700;color:{color};margin-bottom:.5rem;">{title}</div>
                <div style="color:#718096;font-size:.88rem;line-height:1.5;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)


def _show_static_fallback(state):
    st.markdown("""
    <div class="card-gold">
        <b>📡 Offline Mode</b><br/>
        <span style="color:#4a5568;font-size:.9rem;">
        Weather data requires internet. Here are typical monsoon averages for Indian states.
        Install the app with internet access for live data.
        </span>
    </div>
    """, unsafe_allow_html=True)