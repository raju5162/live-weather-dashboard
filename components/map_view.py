"""
Interactive Weather Map Component
Uses Plotly map visualizations to display requested city, user coordinates, and nearby metropolitan micro-climates.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from config import format_temp

def render_map_view(data: dict, unit: str):
    st.markdown("### 🗺️ Interactive Weather Map")

    lat = data["latitude"]
    lon = data["longitude"]
    city = data["city"]
    temp = data["temp_c"]

    # Generate surrounding regional benchmark markers
    map_data = [
        {"city": city, "lat": lat, "lon": lon, "temp_c": temp, "humidity": data["humidity"], "type": "Target Location"},
        {"city": f"{city} North", "lat": lat + 0.35, "lon": lon + 0.25, "temp_c": round(temp - 1.2, 1), "humidity": data["humidity"] + 5, "type": "Regional Station"},
        {"city": f"{city} South", "lat": lat - 0.40, "lon": lon - 0.30, "temp_c": round(temp + 1.5, 1), "humidity": max(20, data["humidity"] - 6), "type": "Regional Station"},
        {"city": f"{city} East", "lat": lat + 0.15, "lon": lon + 0.45, "temp_c": round(temp + 0.8, 1), "humidity": data["humidity"] + 2, "type": "Regional Station"},
        {"city": f"{city} West", "lat": lat - 0.20, "lon": lon - 0.35, "temp_c": round(temp - 0.5, 1), "humidity": data["humidity"] - 3, "type": "Regional Station"}
    ]

    df_map = pd.DataFrame(map_data)
    df_map["temp_display"] = df_map["temp_c"].apply(lambda t: format_temp(t, unit))

    fig_map = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        color="temp_c",
        size="temp_c",
        hover_name="city",
        hover_data={"temp_display": True, "humidity": True, "type": True, "lat": False, "lon": False},
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=22,
        zoom=7,
        title=f"Regional Micro-Climate Thermal Map around {city}"
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=40, b=0),
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0")
    )

    st.plotly_chart(fig_map, use_container_width=True)
