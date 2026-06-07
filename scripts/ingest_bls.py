import requests
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv()

BLS_API_KEY = os.getenv("BLS_API_KEY")
DB_URL = os.getenv("DB_URL")

# Series we care about — id maps to human readable name and category
SERIES = {
    "CUUR0000SA0":  ("All Items",      "overall"),
    "CUUR0000SAF":  ("Food",           "food"),
    "CUUR0000SAH":  ("Housing",        "housing"),
    "CUUR0000SAE":  ("Energy",         "energy"),
    "CUUR0000SAM":  ("Medical Care",   "medical"),
    "CUUR0000SAT":  ("Transportation", "transportation"),
}

def fetch_bls_data(series_ids, start_year="2015", end_year="2024"):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": BLS_API_KEY
    }
    response = requests.post(url, json=payload)
    return response.json()

def get_db_connection():
    return psycopg2.connect(DB_URL)

def insert_series_metadata(cursor):
    for series_id, (name, category) in SERIES.items():
        cursor.execute("""
            INSERT INTO bls_series (series_id, series_name, category)
            VALUES (%s, %s, %s)
            ON CONFLICT (series_id) DO NOTHING;
        """, (series_id, name, category))
    print("Series metadata inserted")

def insert_cpi_data(cursor, data):
    count = 0
    for series in data["Results"]["series"]:
        series_id = series["seriesID"]
        for item in series["data"]:
            cursor.execute("""
                INSERT INTO bls_cpi_raw (series_id, year, period, value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (series_id, int(item["year"]), item["period"], float(item["value"])))
            count += 1
    print(f"{count} data points inserted")

def main():
    series_ids = list(SERIES.keys())
    
    print("Fetching data from BLS...")
    data = fetch_bls_data(series_ids)
    
    if data["status"] != "REQUEST_SUCCEEDED":
        print("API call failed:", data)
        return
    
    print("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    insert_series_metadata(cursor)
    insert_cpi_data(cursor, data)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Done.")

main()