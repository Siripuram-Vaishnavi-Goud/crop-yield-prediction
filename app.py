import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="CropSight",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session defaults
for k, v in {"logged_in": False, "username": "", "page": "home", "dark_mode": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# CSS - inline to avoid file encoding issues
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
.stApp { background: #f8fffe !important; }

[data-testid="stSidebar"] { background: #1a472a !important; }
[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #d4edda !important;
    text-align: left !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.75rem !important;
    border-radius: 8px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: white !important;
    transform: none !important;
    box-shadow: none !important;
}
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 1.25rem 1.5rem !important;
}
[data-testid="stMetricValue"] { color: #1a472a !important; font-size: 1.8rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #718096 !important; font-size: 0.8rem !important; }
.stButton > button {
    background: linear-gradient(135deg, #2d6a4f, #1a472a) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(45,106,79,0.3) !important;
}
.stTabs [data-baseweb="tab-list"] { background: #f0faf3 !important; border-radius: 10px !important; padding: 4px !important; }
.stTabs [aria-selected="true"] { background: white !important; color: #1a472a !important; font-weight: 600 !important; }
.page-hero {
    background: linear-gradient(135deg, #1a472a, #2d6a4f);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
}
.page-hero h1 { color: white !important; font-family: Lora,serif; font-size: 1.9rem; margin: 0 0 .3rem; }
.page-hero p  { color: rgba(255,255,255,0.78) !important; margin: 0; font-size: 0.95rem; }
.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.card-green {
    background: #f0faf3;
    border: 1px solid #52b788;
    border-radius: 16px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
}
.section-title { font-family: Lora,serif; font-size: 1.4rem; font-weight: 600; color: #1a472a; margin-bottom: .2rem; }
.section-sub   { color: #718096; font-size: .88rem; margin-bottom: 1.25rem; }
</style>
""", unsafe_allow_html=True)

if st.session_state.dark_mode:
    st.markdown("""<style>
    .stApp { background: #121c17 !important; }
    .card  { background: #1e2d24 !important; border-color: #2d4a3e !important; }
    .card-green { background: #162820 !important; }
    [data-testid="stMetric"] { background: #1e2d24 !important; border-color: #2d4a3e !important; }
    [data-testid="stMetricValue"] { color: #74c69d !important; }
    p, label { color: #c8e6c9 !important; }
    .section-title { color: #74c69d !important; }
    .stSelectbox > div > div, .stTextInput > div > div > input,
    .stNumberInput > div > div > input, .stTextArea textarea {
        background: #1e2d24 !important; border-color: #2d4a3e !important; color: #e8f5e9 !important; }
    </style>""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.25rem 0 1rem;'>
        <div style='font-size:2.5rem;'>&#127807;</div>
        <div style='font-family:Lora,serif;font-size:1.35rem;font-weight:600;color:#e8f5e9;margin-top:.3rem;'>CropSight</div>
        <div style='font-size:.7rem;color:#81c784;text-transform:uppercase;letter-spacing:.1em;'>Yield Intelligence</div>
    </div>
    <hr style='border:none;border-top:1px solid rgba(255,255,255,.15);margin:0 0 .75rem;'/>
    """, unsafe_allow_html=True)

    def go(label, key):
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("<div style='color:#95d5b2;font-size:.68rem;font-weight:700;letter-spacing:.12em;padding:.1rem .5rem .3rem;'>MAIN</div>", unsafe_allow_html=True)
    go("Home",              "home")
    go("Dashboard",         "dashboard")

    st.markdown("<div style='color:#95d5b2;font-size:.68rem;font-weight:700;letter-spacing:.12em;padding:.6rem .5rem .3rem;'>TOOLS</div>", unsafe_allow_html=True)
    go("Prediction",        "prediction")
    go("Recommendation",    "recommendation")
    go("Dataset Analysis",  "dataset_analysis")

    st.markdown("<div style='color:#95d5b2;font-size:.68rem;font-weight:700;letter-spacing:.12em;padding:.6rem .5rem .3rem;'>INSIGHTS</div>", unsafe_allow_html=True)
    go("Weather",           "weather")
    go("Crop Calendar",     "crop_calendar")
    go("Price Forecast",    "price_forecast")
    go("Soil Health",       "soil_health")

    st.markdown("<div style='color:#95d5b2;font-size:.68rem;font-weight:700;letter-spacing:.12em;padding:.6rem .5rem .3rem;'>OTHER</div>", unsafe_allow_html=True)
    go("Admin Panel",       "admin")
    go("Contact",           "contact")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.15);margin:.75rem 0;'/>", unsafe_allow_html=True)

    dm = "Light Mode" if st.session_state.dark_mode else "Dark Mode"
    if st.button(dm, key="dark_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("<div style='height:.4rem;'></div>", unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.markdown(f"""
        <div style='background:rgba(82,183,136,0.15);border:1px solid rgba(82,183,136,0.3);
                    border-radius:10px;padding:.75rem;text-align:center;margin:.25rem 0;'>
            <div style='color:#e8f5e9;font-weight:600;font-size:.9rem;'>&#128100; {st.session_state.username}</div>
            <div style='color:#81c784;font-size:.72rem;'>Logged in</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:.3rem;'></div>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            from pages.auth import do_logout
            do_logout()
            st.session_state.page = "home"
            st.rerun()
    else:
        st.markdown("<div style='text-align:center;color:rgba(255,255,255,.45);font-size:.75rem;margin-bottom:.4rem;'>Sign in to unlock Dashboard</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login",    key="sidebar_login_btn",    use_container_width=True):
                st.session_state.page = "login"; st.rerun()
        with c2:
            if st.button("Register", key="sidebar_register_btn", use_container_width=True):
                st.session_state.page = "register"; st.rerun()

    st.markdown("<div style='text-align:center;color:rgba(255,255,255,.2);font-size:.62rem;margin-top:1rem;'>CropSight v2.0</div>", unsafe_allow_html=True)

# ── Router ─────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    from my_pages.home import render; render()

elif page == "dashboard":
    from pages.auth import is_logged_in
    if is_logged_in():
        from pages.dashboard import render; render()
    else:
        st.markdown('<div class="page-hero"><h1>Dashboard</h1><p>Login required to view analytics</p></div>', unsafe_allow_html=True)
        st.warning("Please log in to access the Dashboard.")
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            if st.button("Login",    key="dash_login_btn",    use_container_width=True): st.session_state.page="login";    st.rerun()
        with c2:
            if st.button("Register", key="dash_register_btn", use_container_width=True): st.session_state.page="register"; st.rerun()

elif page == "prediction":      from pages.prediction       import render; render()
elif page == "recommendation":  from pages.recommendation   import render; render()
elif page == "dataset_analysis":from pages.dataset_analysis import render; render()
elif page == "weather":         from pages.weather          import render; render()
elif page == "crop_calendar":   from pages.crop_calendar    import render; render()
elif page == "price_forecast":  from pages.price_forecast   import render; render()
elif page == "soil_health":     from pages.soil_health      import render; render()
elif page == "contact":         from pages.contact          import render; render()
elif page == "login":           from pages.login            import render; render()
elif page == "register":        from pages.register         import render; render()
elif page == "admin":
    from pages.auth import is_logged_in
    if is_logged_in():
        from pages.admin import render; render()
    else:
        st.warning("Admin panel requires login.")
        if st.button("Login", key="admin_login_btn"): st.session_state.page="login"; st.rerun()
