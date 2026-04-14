"""pages/admin.py — Admin Panel (login required)"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from pages.auth import get_all_users, DB_PATH
from pages.helpers import load_data


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>🛡️ Admin Panel</h1>
        <p>User management and platform statistics — admin access only</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["👥 Users", "📊 Platform Stats", "🗄️ Database"])

    # ─────────────────────────────────────────────────────────────────────
    # TAB 1: Users
    # ─────────────────────────────────────────────────────────────────────
    with tabs[0]:
        rows = get_all_users()

        if not rows:
            st.info("No users registered yet.")
        else:
            udf = pd.DataFrame(rows, columns=["ID","Username","Email","Registered"])
            udf["Registered"] = pd.to_datetime(udf["Registered"]).dt.strftime("%b %d, %Y %H:%M")

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Users",      len(udf))
            c2.metric("Latest Signup",    udf["Registered"].iloc[-1] if len(udf) > 0 else "—")
            c3.metric("DB Path",          os.path.basename(DB_PATH))

            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("<div class='section-title' style='font-size:1rem;'>👥 Registered Users</div>",
                        unsafe_allow_html=True)
            st.dataframe(udf, use_container_width=True, hide_index=True, height=320)

            csv = udf.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export Users CSV", csv, "users.csv", "text/csv")

            # Delete user
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("<div class='section-title' style='font-size:1rem;'>🗑️ Delete User</div>",
                        unsafe_allow_html=True)
            del_user = st.selectbox("Select user to delete",
                                    [u for u in udf["Username"] if u != st.session_state.get("username")])
            if st.button(f"🗑️ Delete '{del_user}'", type="primary"):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM users WHERE username=?", (del_user,))
                    conn.commit()
                    conn.close()
                    st.success(f"User '{del_user}' deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # TAB 2: Platform Stats
    # ─────────────────────────────────────────────────────────────────────
    with tabs[1]:
        df = load_data()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Dataset Records",   f"{len(df):,}")
        c2.metric("Unique Crops",      df["Crop"].nunique())
        c3.metric("States",            df["State"].nunique())
        c4.metric("Avg Yield",         f"{df['Yield'].mean():.4f} t/ha")

        st.markdown("<br/>", unsafe_allow_html=True)

        import plotly.express as px
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Records per State**")
            state_counts = df["State"].value_counts().reset_index()
            state_counts.columns = ["State","Records"]
            fig = px.bar(state_counts.head(15), x="State", y="Records",
                         color="Records", color_continuous_scale=["#d8f3dc","#1a472a"])
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(t=10,b=10,l=0,r=0), height=320,
                              coloraxis_showscale=False, xaxis_tickangle=-45,
                              font=dict(family="DM Sans"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Records per Season**")
            season_counts = df["Season"].value_counts().reset_index()
            season_counts.columns = ["Season","Records"]
            fig2 = px.pie(season_counts, names="Season", values="Records",
                          color_discrete_sequence=["#1a472a","#2d6a4f","#52b788",
                                                   "#95d5b2","#d8f3dc","#d4a017"],
                          hole=0.4)
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(t=10,b=10,l=0,r=0), height=320,
                               font=dict(family="DM Sans"))
            st.plotly_chart(fig2, use_container_width=True)

        # Model results
        st.markdown("<div class='section-title' style='font-size:1rem;'>🤖 Model Performance</div>",
                    unsafe_allow_html=True)
        try:
            import pickle
            model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
            with open(os.path.join(model_dir, "model_results.pkl"), "rb") as f:
                results = pickle.load(f)
            with open(os.path.join(model_dir, "model.pkl"), "rb") as f:
                meta    = pickle.load(f)

            rdf = pd.DataFrame([
                {"Model": k, "R²": v["R2"], "RMSE": v["RMSE"], "MAE": v["MAE"]}
                for k, v in results.items()
            ]).round(4)
            rdf["Best"] = rdf["Model"] == meta["best"]

            st.dataframe(
                rdf.style.apply(
                    lambda row: ["background:#d8f3dc" if row["Best"] else "" for _ in row], axis=1
                ),
                use_container_width=True, hide_index=True
            )
            st.success(f"✅ Active model: **{meta['best']}** (R²={rdf[rdf['Model']==meta['best']]['R²'].values[0]:.4f})")
        except Exception as e:
            st.info(f"Model results not available: {e}")

    # ─────────────────────────────────────────────────────────────────────
    # TAB 3: Database info
    # ─────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("<div class='section-title' style='font-size:1rem;'>🗄️ Database Info</div>",
                    unsafe_allow_html=True)

        if os.path.exists(DB_PATH):
            size_kb = os.path.getsize(DB_PATH) / 1024
            c1, c2 = st.columns(2)
            c1.metric("DB Size",  f"{size_kb:.1f} KB")
            c2.metric("DB Path",  DB_PATH)

            try:
                conn = sqlite3.connect(DB_PATH)
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                conn.close()
                st.markdown("**Tables:**")
                for (t,) in tables:
                    st.markdown(f"- `{t}`")
            except Exception as e:
                st.error(str(e))
        else:
            st.info("Database not created yet. Register a user to create it.")

        # Model files
        st.markdown("<div class='section-title' style='font-size:1rem;'>📦 Model Files</div>",
                    unsafe_allow_html=True)
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
        if os.path.exists(model_dir):
            files = [f for f in os.listdir(model_dir) if f.endswith(".pkl")]
            mdf   = pd.DataFrame([{
                "File": f,
                "Size (KB)": round(os.path.getsize(os.path.join(model_dir, f)) / 1024, 1)
            } for f in sorted(files)])
            st.dataframe(mdf, use_container_width=True, hide_index=True)