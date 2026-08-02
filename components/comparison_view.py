"""
City Comparison Component
Compares weather metrics across multiple selected global cities simultaneously using side-by-side tables and charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DEFAULT_CITIES, format_temp
from services.weather_api import WeatherAPIService

def render_comparison_view(api_service: WeatherAPIService, current_city: str, unit: str):
    st.markdown("### 🌆 Multi-City Side-by-Side Comparison")

    selected_cities = st.multiselect(
        "Select Cities to Compare:",
        options=DEFAULT_CITIES + ["Tokyo", "Paris", "Sydney", "Dubai", "Singapore"],
        default=[current_city, "Mumbai", "Bangalore", "London"] if current_city not in ["Mumbai", "Bangalore", "London"] else ["Delhi", "Mumbai", "Bangalore", "London"]
    )

    if not selected_cities:
        st.warning("Please select at least one city to perform comparison.")
        return

    comparison_data = []
    for c in selected_cities:
        w = api_service.fetch_weather(c)
        comparison_data.append({
            "City": w["city"],
            "Temp_C": w["temp_c"],
            "FeelsLike_C": w["feels_like_c"],
            "Humidity (%)": w["humidity"],
            "Wind Speed (km/h)": w["wind_kmh"],
            "AQI Index": w["aqi"]["aqi_value"],
            "Condition": w["condition"]
        })

    df_comp = pd.DataFrame(comparison_data)

    if unit == "°F":
        df_comp["Temp"] = df_comp["Temp_C"].apply(lambda t: format_temp(t, "°F"))
        df_comp["Feels Like"] = df_comp["FeelsLike_C"].apply(lambda t: format_temp(t, "°F"))
    else:
        df_comp["Temp"] = df_comp["Temp_C"].apply(lambda t: format_temp(t, "°C"))
        df_comp["Feels Like"] = df_comp["FeelsLike_C"].apply(lambda t: format_temp(t, "°C"))

    # Display comparison table
    st.markdown("#### Comparative Summary Table")
    st.dataframe(
        df_comp[["City", "Temp", "Feels Like", "Humidity (%)", "Wind Speed (km/h)", "AQI Index", "Condition"]],
        use_container_width=True
    )

    st.markdown("---")
    col_bar, col_radar = st.columns([1, 1])

    with col_bar:
        st.markdown("#### Temperature & AQI Comparison")
        fig_bar = px.bar(
            df_comp,
            x="City",
            y=["Temp_C", "AQI Index"],
            barmode="group",
            title="Multi-City Temperature vs AQI Index",
            labels={"value": "Magnitude", "variable": "Metric"}
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            height=340
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_radar:
        st.markdown("#### Multidimensional Weather Profile (Radar Chart)")
        fig_radar = go.Figure()
        for idx, row in df_comp.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row["Temp_C"], row["Humidity (%)"], row["Wind Speed (km/h)"], min(row["AQI Index"], 200)/2],
                theta=['Temp (°C)', 'Humidity (%)', 'Wind (km/h)', 'Normalized AQI'],
                fill='toself',
                name=row["City"]
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            height=340
        )
        st.plotly_chart(fig_radar, use_container_width=True)
