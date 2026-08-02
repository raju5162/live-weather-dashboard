"""
Weather Analytics & Insights Component
Calculates high-level statistical distributions, variances, and renders rule-based smart observations.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from config import format_temp, format_speed
from services.ml_service import WeatherMLService

def render_analytics_view(data: dict, unit: str):
    st.markdown("### 📊 Atmospheric Data Analytics & Statistical Distributions")

    hourly = data.get("hourly_forecast", [])
    df_h = pd.DataFrame(hourly)

    if not df_h.empty:
        max_temp = df_h["temp_c"].max()
        min_temp = df_h["temp_c"].min()
        avg_hum = df_h["humidity"].mean()
        avg_wind = df_h["wind_kmh"].mean()
        temp_var = round(df_h["temp_c"].var(), 2)
        avg_rain_prob = df_h["rain_prob_pct"].mean()

        a1, a2, a3, a4, a5 = st.columns(5)
        
        with a1:
            st.markdown(f"""
            <div class="weather-card" style="text-align:center;">
                <div class="metric-label">Highest Temp</div>
                <div class="metric-value" style="color:#EF4444;">🔥 {format_temp(max_temp, unit)}</div>
            </div>
            """, unsafe_allow_html=True)

        with a2:
            st.markdown(f"""
            <div class="weather-card" style="text-align:center;">
                <div class="metric-label">Lowest Temp</div>
                <div class="metric-value" style="color:#60A5FA;">❄️ {format_temp(min_temp, unit)}</div>
            </div>
            """, unsafe_allow_html=True)

        with a3:
            st.markdown(f"""
            <div class="weather-card" style="text-align:center;">
                <div class="metric-label">Average Humidity</div>
                <div class="metric-value">💧 {avg_hum:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with a4:
            st.markdown(f"""
            <div class="weather-card" style="text-align:center;">
                <div class="metric-label">Average Wind</div>
                <div class="metric-value" style="font-size:1.6rem; margin-top:5px;">🌬️ {format_speed(avg_wind, unit)}</div>
            </div>
            """, unsafe_allow_html=True)

        with a5:
            st.markdown(f"""
            <div class="weather-card" style="text-align:center;">
                <div class="metric-label">Temp Variance</div>
                <div class="metric-value" style="font-size:1.6rem; margin-top:5px;">📈 {temp_var} °C²</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        c_box, c_hist = st.columns([1, 1])

        with c_box:
            st.markdown("#### Temperature vs Humidity Distribution")
            fig_scatter = px.scatter(
                df_h,
                x="temp_c",
                y="humidity",
                size="wind_kmh",
                color="rain_prob_pct",
                labels={"temp_c": "Temperature (°C)", "humidity": "Humidity (%)", "rain_prob_pct": "Rain Prob %"},
                title="Thermal-Hydrological Correlation Chart"
            )
            fig_scatter.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                height=300
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with c_hist:
            st.markdown("#### Rain Probability Distribution")
            fig_rain = px.histogram(
                df_h,
                x="rain_prob_pct",
                nbins=10,
                color_discrete_sequence=["#3B82F6"],
                title="Rainfall Risk Frequency Histogram"
            )
            fig_rain.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                height=300
            )
            st.plotly_chart(fig_rain, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Dynamic Analytical Insights & Observations")

    insights = WeatherMLService.generate_smart_insights(data)
    for insight in insights:
        st.markdown(f'<div class="insight-badge" style="font-size:0.95rem; margin:6px 0; display:block;">{insight}</div>', unsafe_allow_html=True)
