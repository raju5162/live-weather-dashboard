"""
Historical Trends & SQLite Persistence Component
Queries SQLite database records to display multi-day time-series weather trends.
"""

import streamlit as st
import plotly.express as px
from services.db_service import get_historical_logs, seed_sample_history_if_empty

def render_historical_view(city: str, unit: str):
    st.markdown("### 📜 Historical Trends & Database Logs (SQLite)")

    # Ensure database has seed data for city if first time loading
    seed_sample_history_if_empty(city)

    days_filter = st.slider("Select Historical Lookback Period (Days):", min_value=1, max_value=30, value=7)
    df_hist = get_historical_logs(city=city, days=days_filter)

    if df_hist.empty:
        st.info(f"No historical records found in SQLite for {city}. Run live queries to accumulate hourly log data.")
        return

    st.markdown(f"Displaying **{len(df_hist)}** database entries logged for **{city}**.")

    if unit == "°F":
        df_hist["temp_display"] = df_hist["temp_c"].apply(lambda t: (t * 9/5) + 32)
        unit_label = "°F"
    else:
        df_hist["temp_display"] = df_hist["temp_c"]
        unit_label = "°C"

    tab_temp, tab_hum, tab_wind, tab_table = st.tabs(["🌡️ Temperature Trend", "💧 Humidity Drift", "🌬️ Wind & Pressure", "🗄️ SQLite Raw Table"])

    with tab_temp:
        fig_t = px.line(
            df_hist,
            x="timestamp",
            y="temp_display",
            title=f"Historical Temperature Trajectory for {city} ({unit_label})",
            markers=True
        )
        fig_t.update_traces(line_color="#38BDF8", line_width=2)
        fig_t.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=350)
        st.plotly_chart(fig_t, use_container_width=True)

    with tab_hum:
        fig_h = px.area(
            df_hist,
            x="timestamp",
            y="humidity",
            title=f"Historical Humidity Curve for {city} (%)"
        )
        fig_h.update_traces(line_color="#00E676", fillcolor="rgba(0, 230, 118, 0.2)")
        fig_h.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=350)
        st.plotly_chart(fig_h, use_container_width=True)

    with tab_wind:
        fig_w = px.line(
            df_hist,
            x="timestamp",
            y=["wind_kmh", "pressure_mb"],
            title=f"Historical Wind Speed & Atmospheric Pressure for {city}"
        )
        fig_w.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"), height=350)
        st.plotly_chart(fig_w, use_container_width=True)

    with tab_table:
        st.dataframe(df_hist, use_container_width=True)
