"""
Forecast View Component
Renders 7-Day Forecast Cards and 24-Hour Interactive Plotly Line & Bar Charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import format_temp, format_speed, WEATHER_ICONS

def render_forecast_view(data: dict, unit: str):
    st.markdown("### 📅 7-Day Weather Forecast")
    
    daily_list = data.get("daily_forecast", [])
    cols = st.columns(len(daily_list))

    for i, day in enumerate(daily_list):
        icon = WEATHER_ICONS.get(day["condition"], "🌤️")
        max_t = format_temp(day["max_temp_c"], unit)
        min_t = format_temp(day["min_temp_c"], unit)

        with cols[i]:
            st.markdown(
                f"""
                <div class="forecast-card">
                    <div style="font-weight:700; font-size:1.1rem; color:#38BDF8;">{day['day_name']}</div>
                    <div style="font-size:0.8rem; color:#94A3B8;">{day['date']}</div>
                    <div style="font-size:2.4rem; margin: 8px 0;">{icon}</div>
                    <div style="font-size:0.9rem; font-weight:600;">{day['condition']}</div>
                    <div style="margin-top:8px; font-size:1.1rem; font-weight:700;">{max_t}</div>
                    <div style="font-size:0.85rem; color:#94A3B8;">Min: {min_t}</div>
                    <div style="margin-top:6px; font-size:0.8rem; color:#60A5FA;">💧 Rain: {day['rain_chance_pct']}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### 🕒 24-Hour Interactive Hourly Forecast")

    hourly_list = data.get("hourly_forecast", [])
    df_hourly = pd.DataFrame(hourly_list)

    if not df_hourly.empty:
        if unit == "°F":
            df_hourly["display_temp"] = df_hourly["temp_c"].apply(lambda x: (x * 9/5) + 32)
            temp_unit_label = "°F"
        else:
            df_hourly["display_temp"] = df_hourly["temp_c"]
            temp_unit_label = "°C"

        tab1, tab2, tab3 = st.tabs(["🌡️ Temperature Trajectory", "💧 Humidity & Rain Probability", "🌬️ Wind Speed & Pressure"])

        with tab1:
            fig_temp = px.line(
                df_hourly,
                x="time",
                y="display_temp",
                title=f"24-Hour Temperature Profile ({temp_unit_label})",
                labels={"time": "Time of Day", "display_temp": f"Temperature ({temp_unit_label})"},
                markers=True,
                line_shape="spline"
            )
            fig_temp.update_traces(line_color="#38BDF8", line_width=3, marker=dict(size=7, color="#60A5FA"))
            fig_temp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                height=340
            )
            st.plotly_chart(fig_temp, use_container_width=True)

        with tab2:
            fig_hum_rain = go.Figure()
            fig_hum_rain.add_trace(go.Bar(
                x=df_hourly["time"],
                y=df_hourly["rain_prob_pct"],
                name="Rain Probability (%)",
                marker_color="#3B82F6",
                opacity=0.7
            ))
            fig_hum_rain.add_trace(go.Scatter(
                x=df_hourly["time"],
                y=df_hourly["humidity"],
                name="Humidity (%)",
                mode="lines+markers",
                line=dict(color="#00E676", width=3)
            ))
            fig_hum_rain.update_layout(
                title="Hourly Humidity vs Rain Probability",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_hum_rain, use_container_width=True)

        with tab3:
            fig_wind = px.area(
                df_hourly,
                x="time",
                y="wind_kmh",
                title="Hourly Wind Speed Trend (km/h)",
                labels={"time": "Time of Day", "wind_kmh": "Wind Speed (km/h)"}
            )
            fig_wind.update_traces(line_color="#F59E0B", fillcolor="rgba(245, 158, 11, 0.2)")
            fig_wind.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                height=340
            )
            st.plotly_chart(fig_wind, use_container_width=True)
