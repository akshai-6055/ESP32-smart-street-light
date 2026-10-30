-- PostgreSQL / PL/pgSQL Schema for Smart Street Light

CREATE TABLE IF NOT EXISTS sensor_readings (
  id BIGSERIAL PRIMARY KEY,
  device_id VARCHAR(64) NOT NULL,
  ldr_digital SMALLINT NOT NULL,
  ambient VARCHAR(16) NOT NULL,
  led_status VARCHAR(8) NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_device_received ON sensor_readings (device_id, received_at);
