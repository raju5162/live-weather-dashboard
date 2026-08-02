"""
Live Weather Dashboard - Data Analytics & ML Web Application
Built with Python, Streamlit, Plotly, Pandas, SQLite, and Scikit-Learn.
"""

import streamlit as st
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Live Weather & Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import DEFAULT_CITIES, apply_custom_css
from services.weather_api import WeatherAPIService
from services.db_service import (
    init_db, log_weather_data, log_search, get_search_history,
    get_favorites, add_favorite, remove_favorite
)
from services.export_service import WeatherExportService

from components.current_overview import render_current_overview
from components.forecast_view import render_forecast_view
from components.map_view import render_map_view
from components.alerts_view import render_alerts_view
from components.analytics_view import render_analytics_view
from components.historical_view import render_historical_view
from components.comparison_view import render_comparison_view
from components.ml_view import render_ml_view

# Initialize Database
init_db()

# Initialize Session State
if "search_city" not in st.session_state:
    st.session_state["search_city"] = "Delhi"
if "temp_unit" not in st.session_state:
    st.session_state["temp_unit"] = "°C"
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "api_provider" not in st.session_state:
    st.session_state["api_provider"] = "openweather"

# Apply CSS Design System
apply_custom_css(st.session_state["theme_mode"])

# Sidebar Layout
with st.sidebar:
    st.markdown("## 🌤️ Weather Dashboard")
    st.markdown("---")

    # City Search Input
    city_input = st.text_input("📍 Search City Name:", value=st.session_state["search_city"])
    if city_input and city_input != st.session_state["search_city"]:
        st.session_state["search_city"] = city_input.strip()
        log_search(st.session_state["search_city"])
        st.rerun()

    # Quick Select Popular Cities
    st.markdown("**Quick Locations:**")
    quick_cols = st.columns(3)
    for idx, q_city in enumerate(["Delhi", "Mumbai", "London", "New York", "Tokyo", "Paris"]):
        with quick_cols[idx % 3]:
            if st.button(q_city, key=f"btn_{q_city}"):
                st.session_state["search_city"] = q_city
                log_search(q_city)
                st.rerun()

    st.markdown("---")
    # Unit & Theme Toggles
    col_u, col_t = st.columns(2)
    with col_u:
        unit = st.radio("Temperature Unit:", ["°C", "°F"], index=0 if st.session_state["temp_unit"] == "°C" else 1)
        st.session_state["temp_unit"] = unit
    with col_t:
        theme = st.radio("UI Theme Mode:", ["Dark", "Light"], index=0 if st.session_state["theme_mode"] == "Dark" else 1)
        if theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = theme
            st.rerun()

    st.markdown("---")
    # Favorites Manager
    fav_cities = get_favorites()
    is_fav = st.session_state["search_city"] in fav_cities
    if is_fav:
        if st.button(f"⭐ Favorite: {st.session_state['search_city']} (Remove)"):
            remove_favorite(st.session_state["search_city"])
            st.rerun()
    else:
        if st.button(f"☆ Add {st.session_state['search_city']} to Favorites"):
            add_favorite(st.session_state["search_city"])
            st.rerun()

    if fav_cities:
        st.markdown("**Your Favorite Cities:**")
        fav_choice = st.selectbox("Select Favorite:", ["-- Choose --"] + fav_cities)
        if fav_choice != "-- Choose --" and fav_choice != st.session_state["search_city"]:
            st.session_state["search_city"] = fav_choice
            st.rerun()

    st.markdown("---")
    # API Settings Accordion
    with st.expander("🔑 API Key & Engine Config"):
        st.session_state["api_provider"] = st.selectbox("Provider:", ["openweather", "weatherapi"])
        st.session_state["api_key"] = st.text_input("API Key (Optional):", value=st.session_state["api_key"], type="password")
        st.caption("Leave blank to use built-in Live Weather Simulation Engine.")

    # Auto Refresh
    auto_refresh_rate = st.selectbox("Auto Refresh Interval:", ["Off", "5 minutes", "10 minutes", "30 minutes"])

    st.markdown("---")
    st.markdown("### 📥 Download Data")

# Instantiate Weather API Service
api_service = WeatherAPIService(
    api_key=st.session_state["api_key"],
    provider=st.session_state["api_provider"]
)

# Fetch Weather Data for Current City
weather_data = api_service.fetch_weather(st.session_state["search_city"])

# Log live readout to SQLite database
log_weather_data(weather_data)

# Export Buttons in Sidebar
with st.sidebar:
    csv_data = WeatherExportService.export_to_csv(weather_data)
    st.download_button(
        label="📄 Download CSV",
        data=str(csv_data),
        file_name=f"weather_{weather_data['city']}.csv",
        mime="text/csv",
        use_container_width=True
    )

    excel_bytes = bytes(WeatherExportService.export_to_excel(weather_data))
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_bytes,
        file_name=f"weather_analytics_{weather_data['city']}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    pdf_bytes = bytes(WeatherExportService.generate_pdf_report(weather_data))
    st.download_button(
        label="📜 Download PDF Summary",
        data=pdf_bytes,
        file_name=f"weather_report_{weather_data['city']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.markdown("---")
    # API Usage Stats Box
    stats = weather_data.get("api_stats", {})
    st.markdown(
        f"""
        <div style="font-size:0.8rem; color:#94A3B8;">
            <b>API Stats & Health:</b><br>
            • Status: <span style="color:#00E676;">{stats.get('status', 'OK')}</span><br>
            • Response Time: <b>{stats.get('response_time_ms', 0)} ms</b><br>
            • Total API Calls: <b>{stats.get('calls', 1)}</b><br>
            • Provider: <b>{stats.get('provider', 'Mock Engine')}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

# Main Dashboard Title & Tabs
st.markdown("<h1 style='margin-bottom:0;'>🌦️ Live Weather & Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94A3B8; font-size:1.05rem;'>Real-time Atmospheric Intelligence, Air Quality Diagnostics, ML Forecasting & Time-Series Analytics</p>", unsafe_allow_html=True)

tabs = st.tabs([
    "🌡️ Current Overview",
    "📅 7-Day & 24h Forecast",
    "🗺️ Weather Map",
    "⚠️ Severe Alerts",
    "📊 Data Analytics",
    "📜 Historical Trends",
    "🌆 City Comparison",
    "🤖 ML Forecasting & AI"
])

with tabs[0]:
    render_current_overview(weather_data, st.session_state["temp_unit"])

with tabs[1]:
    render_forecast_view(weather_data, st.session_state["temp_unit"])

with tabs[2]:
    render_map_view(weather_data, st.session_state["temp_unit"])

with tabs[3]:
    render_alerts_view(weather_data)

with tabs[4]:
    render_analytics_view(weather_data, st.session_state["temp_unit"])

with tabs[5]:
    render_historical_view(weather_data["city"], st.session_state["temp_unit"])

with tabs[6]:
    render_comparison_view(api_service, weather_data["city"], st.session_state["temp_unit"])

with tabs[7]:
    render_ml_view(weather_data, weather_data["city"])
