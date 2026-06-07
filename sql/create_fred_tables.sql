CREATE TABLE IF NOT EXISTS fred_series (
    series_id VARCHAR(20) PRIMARY KEY,
    series_name VARCHAR(100),
    category VARCHAR(50),
    frequency VARCHAR(20),
    units VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fred_data_raw (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR(20) REFERENCES fred_series(series_id),
    date DATE,
    value DECIMAL(10,3),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);