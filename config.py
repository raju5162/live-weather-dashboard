"""
Config & Design System for Live Weather Dashboard
"""
import streamlit as st

DEFAULT_CITIES = [
    "Delhi", "Mumbai", "Bangalore", "London", "New York", 
    "Tokyo", "Paris", "Sydney", "Dubai", "Singapore"
]

WEATHER_ICONS = {
    "Sunny": "☀️",
    "Clear": "☀️",
    "Partly Cloudy": "⛅",
    "Cloudy": "☁️",
    "Overcast": "☁️",
    "Rain": "🌧️",
    "Heavy Rain": "🌧️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Windy": "🌬️",
}

def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32

def format_temp(val_celsius: float, unit: str = "°C") -> str:
    if unit == "°F":
        val = celsius_to_fahrenheit(val_celsius)
        return f"{val:.1f}°F"
    return f"{val_celsius:.1f}°C"

def format_speed(speed_kmh: float, unit: str = "°C") -> str:
    if unit == "°F":
        speed_mph = speed_kmh * 0.621371
        return f"{speed_mph:.1f} mph"
    return f"{speed_kmh:.1f} km/h"

def get_aqi_details(aqi_val: float):
    if aqi_val <= 50:
        return {"level": "Good", "color": "#00E676", "recommendation": "Air quality is ideal for outdoor activities."}
    elif aqi_val <= 100:
        return {"level": "Moderate", "color": "#FFEB3B", "recommendation": "Sensitive individuals should limit prolonged outdoor exertion."}
    elif aqi_val <= 150:
        return {"level": "Unhealthy for Sensitive Groups", "color": "#FF9800", "recommendation": "Wear a mask outdoors if sensitive. Reduce prolonged outdoor exercise."}
    elif aqi_val <= 200:
        return {"level": "Unhealthy", "color": "#F44336", "recommendation": "Everyone should wear N95 masks and avoid heavy outdoor physical activities."}
    elif aqi_val <= 300:
        return {"level": "Very Unhealthy", "color": "#9C27B0", "recommendation": "Health alert! Avoid outdoor activities and keep windows closed."}
    else:
        return {"level": "Hazardous", "color": "#880E4F", "recommendation": "Emergency condition! Stay indoors and run air purifiers."}

def apply_custom_css(theme_mode: str = "Dark"):
    is_dark = theme_mode == "Dark"
    bg_color = "#0B0F19" if is_dark else "#F4F6F9"
    card_bg = "rgba(22, 28, 45, 0.75)" if is_dark else "rgba(255, 255, 255, 0.9)"
    text_color = "#E2E8F0" if is_dark else "#1E293B"
    border_color = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.08)"
    subtext_color = "#94A3B8" if is_dark else "#64748B"
    accent_glow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)" if is_dark else "0 8px 30px rgba(0, 0, 0, 0.05)"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    .weather-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: {accent_glow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .weather-card:hover {{
        transform: translateY(-2px);
    }}
    
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: {text_color};
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: {subtext_color};
    }}
    
    .insight-badge {{
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }}
    
    .alert-card-warning {{
        background: rgba(245, 158, 11, 0.15);
        border-left: 5px solid #F59E0B;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: {text_color};
    }}
    
    .alert-card-danger {{
        background: rgba(239, 68, 68, 0.15);
        border-left: 5px solid #EF4444;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: {text_color};
    }}

    .forecast-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 15px;
        text-align: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
