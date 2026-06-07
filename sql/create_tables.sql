-- Raw BLS series metadata
CREATE TABLE IF NOT EXISTS bls_series (
    series_id VARCHAR(20) PRIMARY KEY,
    series_name VARCHAR(100),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Raw CPI data points
CREATE TABLE IF NOT EXISTS bls_cpi_raw (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR(20) REFERENCES bls_series(series_id),
    year INTEGER,
    period VARCHAR(10),
    value DECIMAL(10,3),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);