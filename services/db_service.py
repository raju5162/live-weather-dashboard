"""
SQLite Database Manager for Live Weather Dashboard
Handles persistence of hourly weather snapshots, search history, and favorite cities.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_PATH = "weather_history.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Create necessary database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        city TEXT NOT NULL,
        temp_c REAL,
        feels_like_c REAL,
        humidity INTEGER,
        wind_kmh REAL,
        pressure_mb INTEGER,
        aqi INTEGER,
        condition TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        city TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorite_cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT UNIQUE NOT NULL,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def log_weather_data(data: dict):
    """Log a single live weather snapshot to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO weather_logs (timestamp, city, temp_c, feels_like_c, humidity, wind_kmh, pressure_mb, aqi, condition)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data["city"],
        data["temp_c"],
        data.get("feels_like_c", data["temp_c"]),
        data["humidity"],
        data["wind_kmh"],
        data["pressure_mb"],
        data["aqi"]["aqi_value"],
        data["condition"]
    ))
    
    conn.commit()
    conn.close()

def log_search(city: str):
    """Record a city search event."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO search_history (city) VALUES (?)", (city.strip().title(),))
    conn.commit()
    conn.close()

def get_search_history(limit: int = 10) -> list:
    """Retrieve recent search queries."""
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT DISTINCT city FROM search_history ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df["city"].tolist() if not df.empty else []

def get_favorites() -> list:
    """Get favorited cities."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT city FROM favorite_cities ORDER BY added_at DESC", conn)
    conn.close()
    return df["city"].tolist() if not df.empty else []

def add_favorite(city: str) -> bool:
    """Add a city to favorites."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO favorite_cities (city) VALUES (?)", (city.strip().title(),))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_favorite(city: str):
    """Remove a city from favorites."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorite_cities WHERE city = ?", (city.strip().title(),))
    conn.commit()
    conn.close()

def get_historical_logs(city: str = None, days: int = 30) -> pd.DataFrame:
    """Fetch historical logs as a Pandas DataFrame."""
    conn = get_connection()
    query = "SELECT * FROM weather_logs WHERE timestamp >= datetime('now', ?)"
    params = [f"-{days} days"]
    
    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city.strip())
        
    query += " ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def seed_sample_history_if_empty(city: str = "Delhi"):
    """Populates historical sample records if table is empty for rich initial charts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM weather_logs WHERE LOWER(city) = LOWER(?)", (city.strip(),))
    count = cursor.fetchone()[0]
    
    if count == 0:
        now = datetime.now()
        base_temp = 28.0
        records = []
        for i in range(168): # 7 days * 24 hours
            ts = now - timedelta(hours=168 - i)
            h = ts.hour
            temp = round(base_temp + 5 * pd.np.sin(h * 3.14 / 12) + random.uniform(-1.5, 1.5), 1)
            humidity = int(max(30, min(95, 60 - 15 * pd.np.sin(h * 3.14 / 12) + random.randint(-5, 5))))
            wind = round(max(5.0, 12 + 4 * pd.np.cos(h * 3.14 / 12) + random.uniform(-2, 2)), 1)
            press = 1010 + random.randint(-4, 4)
            aqi = int(max(40, min(350, 110 + random.randint(-30, 40))))
            cond = "Sunny" if h in range(7, 18) else "Clear"
            
            records.append((ts.strftime("%Y-%m-%d %H:%M:%S"), city, temp, temp+1, humidity, wind, press, aqi, cond))
            
        cursor.executemany("""
        INSERT INTO weather_logs (timestamp, city, temp_c, feels_like_c, humidity, wind_kmh, pressure_mb, aqi, condition)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()
    conn.close()
