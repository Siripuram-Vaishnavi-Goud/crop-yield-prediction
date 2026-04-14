"""pages/soil_health.py — Soil Health Advisor"""
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Soil type data ─────────────────────────────────────────────────────────
SOIL_TYPES = {
    "Alluvial Soil": {
        "states": ["Uttar Pradesh", "Punjab", "Haryana", "Bihar", "West Bengal", "Assam"],
        "pH_range": (6.5, 8.0),
        "texture": "Loamy to Sandy-Loam",
        "fertility": "High",
        "best_crops": ["Rice", "Wheat", "Sugarcane", "Maize", "Potato"],
        "deficiencies": ["Zinc", "Iron", "Manganese"],
        "description": "Most fertile soil in India. Found in Indo-Gangetic plains. Well-drained and rich in minerals.",
    },
    "Black (Regur) Soil": {
        "states": ["Maharashtra", "Gujarat", "Madhya Pradesh", "Telangana", "Karnataka"],
        "pH_range": (7.5, 8.5),
        "texture": "Clayey",
        "fertility": "Medium-High",
        "best_crops": ["Cotton", "Soyabean", "Wheat", "Jowar", "Groundnut"],
        "deficiencies": ["Phosphorus", "Nitrogen", "Zinc"],
        "description": "Rich in calcium carbonate, magnesium, and lime. Excellent water retention. Ideal for cotton.",
    },
    "Red & Yellow Soil": {
        "states": ["Tamil Nadu", "Andhra Pradesh", "Odisha", "Jharkhand", "Chhattisgarh"],
        "pH_range": (5.5, 7.0),
        "texture": "Sandy-Loam",
        "fertility": "Low-Medium",
        "best_crops": ["Groundnut", "Rice", "Wheat", "Maize", "Tobacco"],
        "deficiencies": ["Nitrogen", "Phosphorus", "Humus"],
        "description": "Porous and friable. Low in nitrogen and humus. Good drainage but needs fertilizer supplements.",
    },
    "Laterite Soil": {
        "states": ["Kerala", "Karnataka (coast)", "Goa", "Meghalaya", "Arunachal Pradesh"],
        "pH_range": (4.5, 6.0),
        "texture": "Coarse & Porous",
        "fertility": "Low",
        "best_crops": ["Cashewnut", "Coconut", "Arecanut", "Tea", "Coffee"],
        "deficiencies": ["Nitrogen", "Phosphorus", "Calcium", "Magnesium"],
        "description": "Formed by intense leaching. High in iron oxide. Acidic and low in fertility. Good for plantation crops.",
    },
    "Sandy / Desert Soil": {
        "states": ["Rajasthan", "Gujarat (Kutch)", "Haryana (south)"],
        "pH_range": (7.0, 8.5),
        "texture": "Sandy",
        "fertility": "Very Low",
        "best_crops": ["Bajra", "Moth", "Guar seed", "Sesame", "Jowar"],
        "deficiencies": ["Nitrogen", "Phosphorus", "Organic Matter"],
        "description": "Low water retention and fertility. Needs irrigation and heavy fertilization. Drought-resistant crops best.",
    },
    "Mountain / Forest Soil": {
        "states": ["Himachal Pradesh", "Uttarakhand", "Jammu and Kashmir", "Sikkim", "Nagaland"],
        "pH_range": (5.0, 6.5),
        "texture": "Loamy",
        "fertility": "Medium",
        "best_crops": ["Apple", "Tea", "Coffee", "Potato", "Wheat"],
        "deficiencies": ["Phosphorus", "Potassium", "Zinc"],
        "description": "Found in Himalayan and other mountain regions. Acidic with good organic matter but thin layers.",
    },
}

NUTRIENTS = {
    "Nitrogen (N)": {
        "unit": "kg/ha", "low": 280, "medium": 560, "high": 840,
        "role": "Leaf growth, photosynthesis, protein synthesis",
        "deficiency_signs": "Yellowing of older leaves, stunted growth",
        "sources": ["Urea (46% N)", "DAP (18% N)", "Ammonium Sulphate", "Compost"],
    },
    "Phosphorus (P)": {
        "unit": "kg/ha", "low": 10, "medium": 25, "high": 50,
        "role": "Root development, flowering, energy transfer",
        "deficiency_signs": "Purple coloration of leaves, poor root growth",
        "sources": ["DAP (46% P₂O₅)", "SSP (16% P₂O₅)", "Rock Phosphate"],
    },
    "Potassium (K)": {
        "unit": "kg/ha", "low": 120, "medium": 280, "high": 500,
        "role": "Disease resistance, water regulation, fruit quality",
        "deficiency_signs": "Brown scorching of leaf edges, weak stems",
        "sources": ["MOP (60% K₂O)", "SOP (50% K₂O)", "Wood ash"],
    },
    "Zinc (Zn)": {
        "unit": "ppm", "low": 0.5, "medium": 1.5, "high": 3.0,
        "role": "Enzyme activation, auxin production, grain filling",
        "deficiency_signs": "White bud, stunted growth, chlorosis",
        "sources": ["Zinc Sulphate (21%)", "Chelated Zinc EDTA"],
    },
    "Organic Carbon": {
        "unit": "%", "low": 0.5, "medium": 0.75, "high": 1.5,
        "role": "Soil structure, water retention, microbial activity",
        "deficiency_signs": "Hard soil, poor water holding, low productivity",
        "sources": ["FYM / Compost", "Green Manure", "Crop Residue incorporation"],
    },
}


def gauge_chart(value, low, high, label, unit):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": label, "font": {"size": 13, "family": "DM Sans"}},
        number={"suffix": f" {unit}", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, high * 1.3], "tickwidth": 1},
            "bar": {"color": "#2d6a4f", "thickness": 0.3},
            "steps": [
                {"range": [0, low],      "color": "#ffe0e0"},
                {"range": [low, high],   "color": "#d8f3dc"},
                {"range": [high, high*1.3], "color": "#fff3cd"},
            ],
            "threshold": {
                "line": {"color": "#d4a017", "width": 3},
                "thickness": 0.8, "value": value,
            },
        },
    ))
    fig.update_layout(
        height=200, margin=dict(t=40, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans"),
    )
    return fig


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>🪱 Soil Health Advisor</h1>
        <p>Enter your soil test results for instant fertilizer recommendations and crop suitability</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🧪 Soil Test Analyzer", "🗺️ Soil Type Guide", "💊 Fertilizer Calculator"])

    # ─────────────────────────────────────────────────────────────────────
    # TAB 1: Soil Test Analyzer
    # ─────────────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown("""
        <div class='section-title'>Enter Your Soil Test Values</div>
        <div class='section-sub'>Get values from your Soil Health Card or nearest Krishi Vigyan Kendra</div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Basic Parameters**")
            ph    = st.slider("Soil pH", 3.5, 9.5, 6.8, 0.1)
            ec    = st.number_input("Electrical Conductivity (dS/m)", 0.0, 10.0, 0.5, 0.1)
            oc    = st.number_input("Organic Carbon (%)", 0.0, 5.0, 0.65, 0.05)
            sand  = st.slider("Sand %", 0, 100, 40)
            silt  = st.slider("Silt %", 0, 100 - sand, 35)
            clay  = 100 - sand - silt
            st.markdown(f"**Clay %:** {clay} *(auto-calculated)*")

        with col2:
            st.markdown("**Macronutrients (NPK)**")
            nitrogen = st.number_input("Nitrogen (kg/ha)", 0, 1200, 350, 10)
            phosphorus = st.number_input("Phosphorus (kg/ha)", 0, 100, 18, 1)
            potassium  = st.number_input("Potassium (kg/ha)", 0, 700, 200, 10)
            st.markdown("**Micronutrients**")
            zinc = st.number_input("Zinc (ppm)", 0.0, 10.0, 0.8, 0.1)
            iron = st.number_input("Iron (ppm)", 0.0, 50.0, 8.0, 0.5)

        st.markdown("<br/>", unsafe_allow_html=True)

        if st.button("🔬 Analyze Soil Health", use_container_width=False):
            # ── pH status ──────────────────────────────────────────────
            if ph < 5.5:
                ph_status, ph_color, ph_advice = "Strongly Acidic", "#e74c3c", "Apply agricultural lime (CaCO₃) @ 2–4 tonnes/ha to raise pH."
            elif ph < 6.5:
                ph_status, ph_color, ph_advice = "Moderately Acidic", "#e67e22", "Apply lime @ 1–2 t/ha. Suitable for tea, groundnut, rice."
            elif ph < 7.5:
                ph_status, ph_color, ph_advice = "Neutral (Ideal)", "#2ecc71", "Optimal for most crops. Maintain with organic matter."
            elif ph < 8.5:
                ph_status, ph_color, ph_advice = "Alkaline", "#e67e22", "Apply gypsum or sulphur @ 1–2 t/ha. Avoid for acid-loving crops."
            else:
                ph_status, ph_color, ph_advice = "Strongly Alkaline", "#e74c3c", "Apply sulphur + gypsum. Reclamation crop (dhaincha) recommended."

            # ── Texture class ──────────────────────────────────────────
            if clay > 40:
                texture = "Clay"
            elif clay > 25 and silt > 25:
                texture = "Clay Loam"
            elif sand > 70:
                texture = "Sandy"
            elif silt > 80:
                texture = "Silty"
            else:
                texture = "Loam"

            # ── Overall score (0-100) ──────────────────────────────────
            score = 0
            score += 25 if 6.0 <= ph <= 7.5 else (15 if 5.5 <= ph <= 8.0 else 5)
            score += 20 if oc >= 0.75 else (12 if oc >= 0.5 else 5)
            score += 15 if nitrogen >= 280 else (8 if nitrogen >= 140 else 3)
            score += 15 if phosphorus >= 10 else (8 if phosphorus >= 5 else 3)
            score += 15 if potassium >= 120 else (8 if potassium >= 60 else 3)
            score += 10 if 0.0 <= ec <= 1.0 else (5 if ec <= 2.0 else 0)

            if score >= 80: health_label, health_color = "Excellent", "#27ae60"
            elif score >= 60: health_label, health_color = "Good", "#2ecc71"
            elif score >= 40: health_label, health_color = "Moderate", "#f1c40f"
            else: health_label, health_color = "Poor", "#e74c3c"

            st.markdown(f"""
            <div class="card-green" style="text-align:center;padding:2rem;">
                <div style="color:#4a5568;font-size:.8rem;font-weight:600;
                            text-transform:uppercase;letter-spacing:.1em;">Soil Health Score</div>
                <div style="font-family:Lora,serif;font-size:3.5rem;font-weight:700;
                            color:{health_color};line-height:1.1;">{score}/100</div>
                <span class="yield-badge" style="background:{health_color}20;
                      color:{health_color};border:1.5px solid {health_color}50;">
                    {health_label}
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br/>", unsafe_allow_html=True)

            # ── Gauge charts ───────────────────────────────────────────
            st.markdown("<div class='section-title' style='font-size:1rem;'>📊 Nutrient Gauges</div>",
                        unsafe_allow_html=True)
            g1, g2, g3, g4 = st.columns(4)
            with g1: st.plotly_chart(gauge_chart(nitrogen,   280, 560,  "Nitrogen",   "kg/ha"), use_container_width=True)
            with g2: st.plotly_chart(gauge_chart(phosphorus, 10,  25,   "Phosphorus", "kg/ha"), use_container_width=True)
            with g3: st.plotly_chart(gauge_chart(potassium,  120, 280,  "Potassium",  "kg/ha"), use_container_width=True)
            with g4: st.plotly_chart(gauge_chart(zinc,       0.5, 1.5,  "Zinc",       "ppm"),   use_container_width=True)

            # ── pH card ────────────────────────────────────────────────
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {ph_color};">
                <div style="font-weight:700;color:{ph_color};margin-bottom:.4rem;">
                    pH {ph} — {ph_status}
                </div>
                <div style="color:#4a5568;font-size:.9rem;">{ph_advice}</div>
                <div style="color:#718096;font-size:.82rem;margin-top:.4rem;">
                    Texture: <b>{texture}</b> · EC: <b>{ec} dS/m</b> ·
                    {'⚠️ Saline soil — leach with good quality water' if ec > 2 else '✅ EC normal'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Recommendations ────────────────────────────────────────
            st.markdown("<div class='section-title' style='font-size:1rem;'>💊 Fertilizer Recommendations</div>",
                        unsafe_allow_html=True)
            recs = []
            if nitrogen < 280:
                deficit = 280 - nitrogen
                recs.append(("Nitrogen", f"Apply Urea @ {int(deficit/0.46):.0f} kg/ha or DAP @ {int(deficit/0.18):.0f} kg/ha", "#e74c3c"))
            if phosphorus < 10:
                recs.append(("Phosphorus", f"Apply DAP @ {int((10-phosphorus)/0.46):.0f} kg/ha or SSP @ {int((10-phosphorus)/0.16):.0f} kg/ha", "#e67e22"))
            if potassium < 120:
                recs.append(("Potassium", f"Apply MOP (Muriate of Potash) @ {int((120-potassium)/0.60):.0f} kg/ha", "#f39c12"))
            if zinc < 0.5:
                recs.append(("Zinc", "Apply Zinc Sulphate @ 25 kg/ha as basal dose", "#9b59b6"))
            if oc < 0.5:
                recs.append(("Organic Matter", "Apply FYM @ 10–15 tonnes/ha or compost @ 5 tonnes/ha", "#2d6a4f"))
            if not recs:
                st.success("✅ All major nutrients are at adequate levels! Continue with maintenance doses.")
            else:
                for nutrient, advice, color in recs:
                    st.markdown(f"""
                    <div class="cal-card">
                        <div class="month">DEFICIENT</div>
                        <div class="activity" style="color:{color};">⚠️ {nutrient}</div>
                        <div style="color:#718096;font-size:.85rem;margin-top:.3rem;">{advice}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Suitable crops ─────────────────────────────────────────
            st.markdown("<div class='section-title' style='font-size:1rem;'>🌾 Suitable Crops for Your Soil</div>",
                        unsafe_allow_html=True)
            suitable = []
            if 6.0 <= ph <= 7.5 and nitrogen >= 200:
                suitable.extend(["Rice", "Wheat", "Maize", "Sugarcane"])
            if ph >= 5.5 and ph <= 7.0:
                suitable.extend(["Groundnut", "Potato", "Soyabean", "Cotton"])
            if ph >= 6.5:
                suitable.extend(["Gram", "Arhar/Tur", "Moong(Green Gram)"])
            if not suitable:
                suitable = ["Bajra", "Jowar", "Sorghum"]  # hardy crops
            suitable = list(dict.fromkeys(suitable))[:8]
            cols = st.columns(4)
            for i, crop in enumerate(suitable):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="background:#f0faf3;border:1px solid #52b788;border-radius:8px;
                                padding:.6rem;text-align:center;margin-bottom:.5rem;
                                font-weight:600;color:#1a472a;font-size:.88rem;">
                        🌿 {crop}
                    </div>
                    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # TAB 2: Soil Type Guide
    # ─────────────────────────────────────────────────────────────────────
    with tabs[1]:
        sel_soil = st.selectbox("Select Soil Type", list(SOIL_TYPES.keys()))
        soil     = SOIL_TYPES[sel_soil]

        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(f"""
            <div class="card-green">
                <div style="font-family:Lora,serif;font-size:1.3rem;font-weight:600;
                            color:#1a472a;margin-bottom:.75rem;">{sel_soil}</div>
                <div style="color:#4a5568;font-size:.92rem;line-height:1.7;margin-bottom:1rem;">
                    {soil['description']}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;">
                    <div><span style="color:#718096;font-size:.8rem;">pH Range</span><br/>
                         <b style="color:#1a472a;">{soil['pH_range'][0]} – {soil['pH_range'][1]}</b></div>
                    <div><span style="color:#718096;font-size:.8rem;">Texture</span><br/>
                         <b style="color:#1a472a;">{soil['texture']}</b></div>
                    <div><span style="color:#718096;font-size:.8rem;">Fertility</span><br/>
                         <b style="color:#1a472a;">{soil['fertility']}</b></div>
                    <div><span style="color:#718096;font-size:.8rem;">States</span><br/>
                         <b style="color:#1a472a;font-size:.82rem;">{', '.join(soil['states'][:3])}...</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("**✅ Best Crops**")
            for crop in soil["best_crops"]:
                st.markdown(f"<div style='padding:.4rem .75rem;margin:.25rem 0;background:#f0faf3;border-radius:6px;font-size:.9rem;color:#1a472a;'>🌿 {crop}</div>", unsafe_allow_html=True)

            st.markdown("**⚠️ Common Deficiencies**")
            for d in soil["deficiencies"]:
                st.markdown(f"<div style='padding:.4rem .75rem;margin:.25rem 0;background:#fff3cd;border-radius:6px;font-size:.9rem;color:#856404;'>⚠️ {d}</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # TAB 3: Fertilizer Calculator
    # ─────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("""
        <div class='section-title'>Fertilizer Dose Calculator</div>
        <div class='section-sub'>Calculate exact quantities of fertilizer bags needed for your field</div>
        """, unsafe_allow_html=True)

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_crop = st.selectbox("Crop", ["Rice","Wheat","Maize","Cotton","Groundnut",
                                           "Sugarcane","Potato","Soyabean"])
        with fc2:
            f_area = st.number_input("Field Area (hectares)", 0.1, 100.0, 1.0, 0.1)
        with fc3:
            f_soil_n = st.selectbox("Soil Nitrogen Status", ["Low (<280)","Medium (280–560)","High (>560)"])

        # Recommended NPK doses (kg/ha) per crop
        NPK_DOSES = {
            "Rice":      {"Low": (120,60,60), "Medium": (100,50,50), "High": (80,40,40)},
            "Wheat":     {"Low": (120,60,40), "Medium": (100,50,30), "High": (80,40,20)},
            "Maize":     {"Low": (150,75,75), "Medium": (120,60,60), "High": (100,50,50)},
            "Cotton":    {"Low": (120,60,60), "Medium": (100,50,50), "High": (80,40,40)},
            "Groundnut": {"Low": (25,50,75),  "Medium": (20,40,60),  "High": (15,30,50)},
            "Sugarcane": {"Low": (250,85,115),"Medium": (200,70,100),"High": (150,60,85)},
            "Potato":    {"Low": (180,80,150),"Medium": (150,60,120),"High": (120,50,100)},
            "Soyabean":  {"Low": (30,60,40),  "Medium": (25,50,30),  "High": (20,40,20)},
        }

        soil_key = "Low" if "Low" in f_soil_n else ("Medium" if "Medium" in f_soil_n else "High")
        n, p, k  = NPK_DOSES[f_crop][soil_key]

        # Fertilizer quantities (50 kg bags)
        urea_ha     = round(n / 0.46, 1)      # Urea 46% N
        dap_ha      = round(p / 0.46, 1)      # DAP 46% P₂O₅
        mop_ha      = round(k / 0.60, 1)      # MOP 60% K₂O
        urea_total  = round(urea_ha * f_area, 1)
        dap_total   = round(dap_ha  * f_area, 1)
        mop_total   = round(mop_ha  * f_area, 1)
        urea_bags   = int(np.ceil(urea_total / 50))
        dap_bags    = int(np.ceil(dap_total  / 50))
        mop_bags    = int(np.ceil(mop_total  / 50))

        # Approx cost (₹/bag of 50 kg)
        PRICES = {"Urea": 266, "DAP": 1350, "MOP": 1700}
        cost = urea_bags*PRICES["Urea"] + dap_bags*PRICES["DAP"] + mop_bags*PRICES["MOP"]

        st.markdown(f"""
        <div class="card-green" style="text-align:center;padding:1.5rem;">
            <div style="font-family:Lora,serif;font-size:1.2rem;font-weight:600;color:#1a472a;margin-bottom:1rem;">
                Recommended Fertilizer for {f_crop} — {f_area} ha
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
                <div style="background:white;border-radius:12px;padding:1rem;">
                    <div style="font-size:.75rem;color:#718096;font-weight:600;text-transform:uppercase;">Urea (46% N)</div>
                    <div style="font-size:1.6rem;font-weight:700;color:#1a472a;">{urea_total} kg</div>
                    <div style="font-size:.85rem;color:#52b788;">{urea_bags} bags × 50kg</div>
                    <div style="font-size:.8rem;color:#718096;">₹{urea_bags*PRICES['Urea']:,}</div>
                </div>
                <div style="background:white;border-radius:12px;padding:1rem;">
                    <div style="font-size:.75rem;color:#718096;font-weight:600;text-transform:uppercase;">DAP (18-46-0)</div>
                    <div style="font-size:1.6rem;font-weight:700;color:#1a472a;">{dap_total} kg</div>
                    <div style="font-size:.85rem;color:#52b788;">{dap_bags} bags × 50kg</div>
                    <div style="font-size:.8rem;color:#718096;">₹{dap_bags*PRICES['DAP']:,}</div>
                </div>
                <div style="background:white;border-radius:12px;padding:1rem;">
                    <div style="font-size:.75rem;color:#718096;font-weight:600;text-transform:uppercase;">MOP (0-0-60)</div>
                    <div style="font-size:1.6rem;font-weight:700;color:#1a472a;">{mop_total} kg</div>
                    <div style="font-size:.85rem;color:#52b788;">{mop_bags} bags × 50kg</div>
                    <div style="font-size:.8rem;color:#718096;">₹{mop_bags*PRICES['MOP']:,}</div>
                </div>
            </div>
            <div style="margin-top:1rem;font-size:1rem;color:#1a472a;">
                💰 Estimated Total Cost: <b style="font-size:1.2rem;">₹{cost:,}</b>
                <span style="color:#718096;font-size:.8rem;">(at subsidized govt. rates)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-gold" style="margin-top:1rem;">
            <b>📋 Recommended NPK Dose for {f_crop} ({soil_key} N soil)</b><br/>
            <span style="color:#4a5568;font-size:.9rem;">
            N: <b>{n} kg/ha</b> · P₂O₅: <b>{p} kg/ha</b> · K₂O: <b>{k} kg/ha</b><br/>
            Apply 50% N + full P + full K as basal dose at sowing.
            Remaining 50% N in 1–2 top-dressings during crop growth.
            </span>
        </div>
        """, unsafe_allow_html=True)