"""
Machine Learning & Predictive Intelligence Component
Renders 24h Random Forest temperature forecasts, feature importances, anomaly scores, and an interactive AI Weather Chatbot.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.ml_service import WeatherMLService
from services.db_service import get_historical_logs

def render_ml_view(data: dict, city: str):
    st.markdown("### 🤖 Machine Learning Predictive Intelligence & AI Chatbot")

    hourly = data.get("hourly_forecast", [])
    if not hourly:
        st.warning("Insufficient hourly data for ML modeling.")
        return

    # Train Random Forest Regressor
    ml_results = WeatherMLService.forecast_temperature_24h(hourly)
    df_pred = ml_results["predictions_df"]

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Model Type</div>
            <div class="metric-value" style="font-size:1.5rem; color:#38BDF8;">Random Forest</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Mean Absolute Error (MAE)</div>
            <div class="metric-value" style="color:#00E676;">{ml_results['mae']} °C</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="weather-card" style="text-align:center;">
            <div class="metric-label">Root Mean Sq Error (RMSE)</div>
            <div class="metric-value" style="color:#F59E0B;">{ml_results['rmse']} °C</div>
        </div>
        """, unsafe_allow_html=True)

    col_chart, col_feat = st.columns([2, 1])

    with col_chart:
        st.markdown("#### Actual vs Scikit-Learn Predicted Temperature Trajectory")
        fig_ml = go.Figure()
        fig_ml.add_trace(go.Scatter(
            x=df_pred["time"],
            y=df_pred["temp_c"],
            mode="lines+markers",
            name="Actual / API Forecast (°C)",
            line=dict(color="#38BDF8", width=3)
        ))
        fig_ml.add_trace(go.Scatter(
            x=df_pred["time"],
            y=df_pred["predicted_temp_c"],
            mode="lines+markers",
            name="ML Random Forest Model (°C)",
            line=dict(color="#EC4899", width=3, dash="dash")
        ))
        fig_ml.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ml, use_container_width=True)

    with col_feat:
        st.markdown("#### Feature Importances")
        feat_df = pd.DataFrame(list(ml_results["feature_importance"].items()), columns=["Feature", "Importance"]).sort_values(by="Importance", ascending=True)
        fig_feat = px.bar(
            feat_df,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale="Blues"
        )
        fig_feat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            height=340
        )
        st.plotly_chart(fig_feat, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Isolation Forest Weather Anomaly Detection")

    df_hist = get_historical_logs(city=city, days=30)
    anomalies = WeatherMLService.detect_anomalies(df_hist)

    if anomalies.empty:
        st.info(f"No statistical weather anomalies detected in SQLite logs for {city}.")
    else:
        st.warning(f"Detected **{len(anomalies)}** atmospheric anomalies in historical logs:")
        st.dataframe(anomalies[["timestamp", "city", "temp_c", "humidity", "wind_kmh", "pressure_mb", "aqi", "condition"]], use_container_width=True)

    st.markdown("---")
    st.markdown("### 💬 Weather AI Assistant & Chatbot")
    
    user_query = st.text_input("Ask the AI Weather Assistant a question (e.g. 'Can I go cycling today?', 'What is the AQI health risk?', 'Will it rain tonight?'):")
    if user_query:
        query_lower = user_query.lower()
        if "cycle" in query_lower or "cycling" in query_lower or "run" in query_lower or "exercise" in query_lower:
            reply = f"🚴 **Cycling & Outdoor Fitness Status for {city}:** Current wind speed is {data['wind_kmh']} km/h and temperature is {data['temp_c']}°C. "
            if data["wind_kmh"] < 20 and "rain" not in data["condition"].lower():
                reply += "Conditions are **ideal** for cycling and outdoor workouts!"
            else:
                reply += "Conditions may be windy or wet. Exercise caution outdoors."
        elif "aqi" in query_lower or "air" in query_lower or "mask" in query_lower:
            reply = f"😷 **Air Quality Summary:** AQI is currently **{data['aqi']['aqi_value']}** (PM2.5: {data['aqi']['pm25']}). "
            if data["aqi"]["aqi_value"] > 150:
                reply += "Air quality is unhealthy. Wearing an N95 mask is strongly advised."
            else:
                reply += "Air quality is within moderate/healthy thresholds."
        elif "rain" in query_lower or "umbrella" in query_lower or "shower" in query_lower:
            hourly = data.get("hourly_forecast", [])
            max_prob = max([h["rain_prob_pct"] for h in hourly]) if hourly else 0
            reply = f"🌧️ **Precipitation Outlook:** Peak rain probability over the next 24 hours is **{max_prob}%**. "
            if max_prob > 50:
                reply += "Carrying an umbrella is recommended!"
            else:
                reply += "Low likelihood of rain today."
        else:
            reply = f"🤖 **Weather Assistant for {city}:** Currently {data['temp_c']}°C with {data['condition']} conditions. Humidity is {data['humidity']}% and wind speed is {data['wind_kmh']} km/h."

        st.markdown(f"""
        <div class="weather-card" style="border-left: 5px solid #38BDF8; margin-top:10px;">
            <p style="margin:0; font-size:1rem;">{reply}</p>
        </div>
        """, unsafe_allow_html=True)
