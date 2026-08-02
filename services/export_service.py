"""
Export Service for Live Weather Dashboard
Provides multi-format data exports: CSV, Excel, JSON, and PDF reports.
"""

import json
import io
import pandas as pd
from fpdf import FPDF
from typing import Dict, Any

class WeatherExportService:
    @staticmethod
    def export_to_csv(data: Dict[str, Any]) -> str:
        """Export current weather & hourly forecast to CSV string."""
        hourly = data.get("hourly_forecast", [])
        df = pd.DataFrame(hourly)
        df.insert(0, "City", data["city"])
        df.insert(1, "Date", data["last_updated"])
        return df.to_csv(index=False)

    @staticmethod
    def export_to_excel(data: Dict[str, Any]) -> bytes:
        """Export current weather, hourly, and 7-day forecast to Excel workbook bytes."""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Overview
            overview_df = pd.DataFrame([{
                "City": data["city"],
                "Country": data["country"],
                "Temperature (°C)": data["temp_c"],
                "Feels Like (°C)": data["feels_like_c"],
                "Humidity (%)": data["humidity"],
                "Wind Speed (km/h)": data["wind_kmh"],
                "Pressure (mb)": data["pressure_mb"],
                "AQI": data["aqi"]["aqi_value"],
                "Condition": data["condition"],
                "Last Updated": data["last_updated"]
            }])
            overview_df.to_excel(writer, sheet_name="Overview", index=False)

            # Sheet 2: Hourly Forecast
            hourly_df = pd.DataFrame(data.get("hourly_forecast", []))
            hourly_df.to_excel(writer, sheet_name="Hourly Forecast", index=False)

            # Sheet 3: Daily Forecast
            daily_df = pd.DataFrame(data.get("daily_forecast", []))
            daily_df.to_excel(writer, sheet_name="7-Day Forecast", index=False)

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_to_json(data: Dict[str, Any]) -> str:
        """Export raw weather dictionary to formatted JSON."""
        return json.dumps(data, indent=4)

    @staticmethod
    def generate_pdf_report(data: Dict[str, Any]) -> bytes:
        """Generate a clean PDF analytical weather report."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        
        # Title
        pdf.cell(0, 10, f"Weather Analytics Report - {data['city']}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Generated: {data['last_updated']} | Data Source: {data.get('api_stats', {}).get('provider', 'API')}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(8)

        # Overview Table
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "1. Current Weather Overview", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        
        metrics = [
            ("City & Country", f"{data['city']}, {data['country']}"),
            ("Temperature", f"{data['temp_c']} °C (Feels like {data['feels_like_c']} °C)"),
            ("Condition", f"{data['condition']}"),
            ("Humidity", f"{data['humidity']}%"),
            ("Wind Speed", f"{data['wind_kmh']} km/h"),
            ("Atmospheric Pressure", f"{data['pressure_mb']} mb"),
            ("Air Quality Index (AQI)", f"{data['aqi']['aqi_value']} (PM2.5: {data['aqi']['pm25']})"),
            ("Sunrise / Sunset", f"{data['sunrise']} / {data['sunset']}")
        ]
        
        for label, val in metrics:
            pdf.cell(60, 7, label, border=1)
            pdf.cell(120, 7, str(val), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(8)
        # 7-Day Forecast Summary
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "2. 7-Day Weather Forecast", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 10)
        
        pdf.cell(30, 7, "Day", border=1)
        pdf.cell(30, 7, "Max Temp", border=1)
        pdf.cell(30, 7, "Min Temp", border=1)
        pdf.cell(40, 7, "Rain Chance", border=1)
        pdf.cell(50, 7, "Condition", border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 10)
        for day in data.get("daily_forecast", []):
            pdf.cell(30, 6, day["day_name"], border=1)
            pdf.cell(30, 6, f"{day['max_temp_c']} °C", border=1)
            pdf.cell(30, 6, f"{day['min_temp_c']} °C", border=1)
            pdf.cell(40, 6, f"{day['rain_chance_pct']}%", border=1)
            pdf.cell(50, 6, day["condition"], border=1, new_x="LMARGIN", new_y="NEXT")

        return bytes(pdf.output())
