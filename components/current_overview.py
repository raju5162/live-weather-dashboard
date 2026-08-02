"""
Current Weather Overview & AQI Component
Renders key metrics, glassmorphic overview cards, AQI gauge chart, and pollutant metrics.
"""

import streamlit as st
import plotly.graph_objects as go
from config import format_temp, format_speed, WEATHER_ICONS, get_aqi_details

def render_current_overview(data: dict, unit: str):
    st.markdown("### 🌡️ Current Weather Overview")

    temp_display = format_temp(data["temp_c"], unit)
    feels_display = format_temp(data["feels_like_c"], unit)
    wind_display = format_speed(data["wind_kmh"], unit)
    icon = WEATHER_ICONS.get(data["condition"], "🌤️")

    # Header Card
    col_city, col_time = st.columns([2, 1])
    with col_city:
        st.markdown(
            f"""
            <div class="weather-card">
                <h1 style="margin:0; font-size: 2.8rem; font-weight:800;">{icon} {data['city']}, <span style="font-weight:400; opacity:0.8;">{data['country']}</span></h1>
                <p style="margin-top:4px; font-size:1.1rem; color:#94A3B8;">Condition: <b>{data['condition']}</b> | Coords: {data['latitude']}°, {data['longitude']}°</p>
                <div style="font-size:3.5rem; font-weight:800; color:#38BDF8; margin-top:10px;">{temp_display} <span style="font-size:1.3rem; color:#94A3B8; font-weight:400;">(Feels like {feels_display})</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_time:
        st.markdown(
            f"""
            <div class="weather-card" style="text-align:right;">
                <div class="metric-label">Last Updated</div>
                <div style="font-size:1.2rem; font-weight:700; margin-top:4px;">🕒 {data['last_updated']}</div>
                <hr style="margin: 12px 0; border-color: rgba(255,255,255,0.1);">
                <div class="metric-label">Solar Schedule</div>
                <div style="margin-top:6px; font-size:0.95rem;">🌅 Sunrise: <b>{data['sunrise']}</b></div>
                <div style="margin-top:4px; font-size:0.95rem;">🌇 Sunset: <b>{data['sunset']}</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 6 Core Metric Tiles
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Humidity</div>
            <div class="metric-value">💧 {data['humidity']}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Wind Speed</div>
            <div class="metric-value" style="font-size:1.6rem; margin-top:5px;">🌬️ {wind_display}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Cloudiness</div>
            <div class="metric-value">☁️ {data['cloud_pct']}%</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Visibility</div>
            <div class="metric-value" style="font-size:1.6rem; margin-top:5px;">👀 {data['visibility_km']} km</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Pressure</div>
            <div class="metric-value" style="font-size:1.6rem; margin-top:5px;">🧭 {data['pressure_mb']} mb</div>
        </div>
        """, unsafe_allow_html=True)

    with m6:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">UV Index</div>
            <div class="metric-value">☀️ {data['uv_index']} / 11</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🍃 Air Quality Index (AQI) & Pollution Analysis")

    aqi_info = get_aqi_details(data["aqi"]["aqi_value"])

    col_gauge, col_recom = st.columns([1, 1])

    with col_gauge:
        # Plotly AQI Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=data["aqi"]["aqi_value"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>AQI Index ({aqi_info['level']})</b>", 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, 500], 'tickwidth': 1},
                'bar': {'color': aqi_info['color']},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#00E676'},
                    {'range': [51, 100], 'color': '#FFEB3B'},
                    {'range': [101, 150], 'color': '#FF9800'},
                    {'range': [151, 200], 'color': '#F44336'},
                    {'range': [201, 300], 'color': '#9C27B0'},
                    {'range': [301, 500], 'color': '#880E4F'}
                ],
            }
        ))
        fig_gauge.update_layout(
            height=260, 
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#E2E8F0"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_recom:
        st.markdown(
            f"""
            <div class="weather-card" style="border-left: 6px solid {aqi_info['color']}; min-height: 220px;">
                <h4 style="margin:0; color:{aqi_info['color']};">Status: {aqi_info['level']} (AQI {data['aqi']['aqi_value']})</h4>
                <p style="margin-top:10px; font-size:1rem;"><b>Health Recommendation:</b></p>
                <p style="font-size:0.95rem; color:#CBD5E1;">{aqi_info['recommendation']}</p>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
                    <span><b>PM2.5:</b> {data['aqi']['pm25']} µg/m³</span>
                    <span><b>PM10:</b> {data['aqi']['pm10']} µg/m³</span>
                    <span><b>CO:</b> {data['aqi']['co']}</span>
                    <span><b>NO₂:</b> {data['aqi']['no2']}</span>
                    <span><b>O₃:</b> {data['aqi']['o3']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
