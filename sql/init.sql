CREATE TABLE weather(
    measurement_id SERIAL PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    temperature REAL,
    pressure REAL,
    humidity REAL,
    pm10  REAL,
    pm2_5 REAL
);
