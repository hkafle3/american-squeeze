import requests
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
DB_URL = os.getenv("DB_URL")

SERIES = {
    "LES1252881600Q": ("Median Usual Weekly Earnings",  "wages",     "quarterly", "dollars"),
    "ECIWAG":         ("Employment Cost Index Wages",   "wages",     "quarterly", "index"),
    "FEDFUNDS":       ("Federal Funds Rate",            "rates",     "monthly",   "percent"),
    "UNRATE":         ("Unemployment Rate",             "labor",     "monthly",   "percent"),
    "MSPUS":          ("Median Sales Price of Houses",  "housing",   "quarterly", "dollars"),
}

def fetch_fred_series(series_id, start_date="2015-01-01", end_date="2024-12-31"):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
    }
    response = requests.get(url, params=params)
    return response.json()

def get_db_connection():
    return psycopg2.connect(DB_URL)

def insert_series_metadata(cursor):
    for series_id, (name, category, frequency, units) in SERIES.items():
        cursor.execute("""
            INSERT INTO fred_series (series_id, series_name, category, frequency, units)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (series_id) DO NOTHING;
        """, (series_id, name, category, frequency, units))
    print("FRED series metadata inserted")

def insert_fred_data(cursor, series_id, observations):
    count = 0
    for obs in observations:
        if obs["value"] == ".":
            continue
        cursor.execute("""
            INSERT INTO fred_data_raw (series_id, date, value)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (series_id, obs["date"], float(obs["value"])))
        count += 1
    return count

def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_series_metadata(cursor)

    total = 0
    for series_id in SERIES:
        print(f"Fetching {series_id}...")
        data = fetch_fred_series(series_id)
        count = insert_fred_data(cursor, series_id, data["observations"])
        total += count
        print(f"  {count} observations inserted")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Done. {total} total data points inserted.")

main()