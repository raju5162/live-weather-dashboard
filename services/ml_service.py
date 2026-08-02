"""
Machine Learning & Analytical Insights Service
Utilizes Scikit-Learn (RandomForestRegressor, IsolationForest) for temperature forecasting,
anomaly detection, and smart automated weather insights.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

class WeatherMLService:
    @staticmethod
    def forecast_temperature_24h(hourly_forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train a Random Forest model on hourly atmospheric features
        and predict the temperature curve for the next 24 hours.
        """
        df = pd.DataFrame(hourly_forecast)
        df["hour"] = df["time"].apply(lambda x: int(x.split(":")[0]))
        df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24.0)
        df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24.0)

        # Feature matrix
        X = df[["hour", "sin_hour", "cos_hour", "humidity", "wind_kmh", "pressure_mb", "rain_prob_pct"]]
        y = df["temp_c"]

        # Train Random Forest Regressor
        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(X, y)

        # In-sample & future trajectory predictions
        predictions = rf.predict(X)
        mae = round(float(mean_absolute_error(y, predictions)), 2)
        rmse = round(float(root_mean_squared_error(y, predictions)), 2)

        # Feature importance calculation
        feature_importance = dict(zip(X.columns, [round(float(val), 3) for val in rf.feature_importances_]))

        df["predicted_temp_c"] = [round(float(p), 1) for p in predictions]

        return {
            "predictions_df": df[["time", "hour", "temp_c", "predicted_temp_c", "humidity", "wind_kmh"]],
            "mae": mae,
            "rmse": rmse,
            "feature_importance": feature_importance
        }

    @staticmethod
    def detect_anomalies(df_history: pd.DataFrame) -> pd.DataFrame:
        """
        Detect unusual weather observations using Isolation Forest.
        """
        if df_history.empty or len(df_history) < 10:
            return pd.DataFrame()

        features = ["temp_c", "humidity", "wind_kmh", "pressure_mb", "aqi"]
        clean_df = df_history.dropna(subset=features).copy()

        iso = IsolationForest(contamination=0.08, random_state=42)
        clean_df["anomaly_score"] = iso.fit_predict(clean_df[features])
        clean_df["is_anomaly"] = clean_df["anomaly_score"] == -1

        return clean_df[clean_df["is_anomaly"]]

    @staticmethod
    def generate_smart_insights(weather_data: Dict[str, Any]) -> List[str]:
        """
        Generate automated rule-based analytical observations and smart health/activity recommendations.
        """
        insights = []
        temp = weather_data["temp_c"]
        humidity = weather_data["humidity"]
        wind = weather_data["wind_kmh"]
        aqi = weather_data["aqi"]["aqi_value"]
        uv = weather_data["uv_index"]
        cond = weather_data["condition"].lower()

        # Temperature evaluation
        if temp > 35:
            insights.append("🔥 High Temperature Notice: Heat index is elevated. Stay in air-conditioned environments.")
        elif temp < 10:
            insights.append("❄️ Low Temperature Notice: Cold morning conditions. Layer warm clothing.")
        else:
            insights.append("🌡️ Mild Thermal Comfort: Temperature is in a pleasant seasonal range.")

        # Humidity evaluation
        if humidity > 80:
            insights.append("💧 High Atmospheric Humidity: Muggy conditions; increased chance of dew or sudden rain.")
        elif humidity < 30:
            insights.append("🌵 Dry Air Conditions: Low humidity detected. Consider using a room humidifier.")

        # Wind & Cycling evaluation
        if wind < 15 and "rain" not in cond and "storm" not in cond:
            insights.append("🚴 Cycling & Outdoor Sports: Wind speed is mild (<15 km/h) and suitable for outdoor workouts.")
        elif wind > 30:
            insights.append("🌬️ Strong Wind Gusts: High wind speeds detected (>30 km/h). Exercise caution while driving.")

        # AQI evaluation
        if aqi > 150:
            insights.append("😷 Severe Air Quality Advisory: High PM2.5 concentrations. Wear an N95 mask outdoors.")
        elif aqi <= 50:
            insights.append("🌱 Fresh Air Quality: AQI is under 50. Excellent day for outdoor parks and recreation.")

        # UV evaluation
        if uv >= 8:
            insights.append("☀️ Dangerous UV Index: UV Index is high (≥8). Apply SPF 50+ sunscreen and wear sunglasses.")

        # Rain expectation
        hourly = weather_data.get("hourly_forecast", [])
        rain_soon = any(h["rain_prob_pct"] > 60 for h in hourly[:4])
        if rain_soon:
            insights.append("🌧️ Rain Expected Soon: Precipitation probability exceeds 60% within the next 4 hours.")

        return insights
