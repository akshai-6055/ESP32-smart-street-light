const express = require('express');
const { Pool } = require('pg');

const app = express();
const PORT = Number(process.env.PORT || 3000);
app.use(express.json({ limit: '20kb' }));
app.use(express.static('public'));

// Database configuration: supports Render PostgreSQL via DATABASE_URL
// or standard PostgreSQL host/port/user credentials
const connectionString = process.env.DATABASE_URL;

const poolConfig = connectionString
  ? {
      connectionString,
      ssl: connectionString.includes('localhost') || connectionString.includes('127.0.0.1')
        ? false
        : { rejectUnauthorized: false }
    }
  : {
      host: process.env.DB_HOST || '127.0.0.1',
      port: Number(process.env.DB_PORT || 5432),
      user: process.env.DB_USER || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
      database: process.env.DB_NAME || 'streetlight_db',
      ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
    };

const pool = new Pool(poolConfig);

// Auto-initialize PostgreSQL schema on startup
async function initDatabase() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS sensor_readings (
        id BIGSERIAL PRIMARY KEY,
        device_id VARCHAR(64) NOT NULL,
        ldr_digital SMALLINT NOT NULL,
        ambient VARCHAR(16) NOT NULL,
        led_status VARCHAR(8) NOT NULL,
        received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_device_received ON sensor_readings (device_id, received_at);
    `);
    console.log('Database initialized: PostgreSQL sensor_readings table ready');
  } catch (err) {
    console.warn('Database initialization warning (will retry on query):', err.message);
  }
}
initDatabase();

// Health Check
app.get('/api/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ok', database: 'connected' });
  } catch (e) {
    res.status(503).json({ status: 'error', database: 'unavailable' });
  }
});

// Ingest Telemetry from ESP32
app.post('/api/readings', async (req, res) => {
  const b = req.body || {};
  const deviceId = String(b.device_id || 'streetlight_01').slice(0, 64);
  const sensor = Number(b.sensor);
  const ambient = String(b.ambient || '');
  const led = String(b.led || '');

  if (![0, 1].includes(sensor) || !['Dark', 'Bright'].includes(ambient) || !['ON', 'OFF'].includes(led)) {
    return res.status(400).json({ error: 'Expected sensor 0/1, ambient Dark/Bright, led ON/OFF' });
  }

  try {
    const result = await pool.query(
      'INSERT INTO sensor_readings (device_id, ldr_digital, ambient, led_status) VALUES ($1, $2, $3, $4) RETURNING id',
      [deviceId, sensor, ambient, led]
    );
    res.status(201).json({ saved: true, id: result.rows[0].id });
  } catch (e) {
    console.error('Database INSERT error:', e.message);
    res.status(500).json({ error: 'Could not save reading' });
  }
});

// Latest Reading
app.get('/api/readings/latest', async (_req, res) => {
  try {
    const result = await pool.query(
      'SELECT id, device_id, ldr_digital, ambient, led_status, received_at FROM sensor_readings ORDER BY id DESC LIMIT 1'
    );
    res.json(result.rows[0] || null);
  } catch (e) {
    res.status(500).json({ error: 'Could not fetch latest reading' });
  }
});

// Historical Readings
app.get('/api/readings', async (req, res) => {
  const limit = Math.min(Math.max(parseInt(req.query.limit || '50', 10) || 50, 1), 500);
  try {
    const result = await pool.query(
      'SELECT id, device_id, ldr_digital, ambient, led_status, received_at FROM sensor_readings ORDER BY id DESC LIMIT $1',
      [limit]
    );
    res.json(result.rows.reverse());
  } catch (e) {
    res.status(500).json({ error: 'Could not fetch history' });
  }
});

// Analytics & Energy Summary
app.get('/api/summary', async (_req, res) => {
  try {
    const result = await pool.query(`
      SELECT
        COUNT(*)::int AS total_records,
        COUNT(*) FILTER (WHERE led_status = 'ON')::int AS led_on_records,
        COUNT(*) FILTER (WHERE led_status = 'OFF')::int AS led_off_records
      FROM sensor_readings
    `);
    const row = result.rows[0] || {};
    const total = Number(row.total_records || 0);
    const onCount = Number(row.led_on_records || 0);
    const offCount = Number(row.led_off_records || 0);

    // Energy Calculations (Based on standard municipal street lighting metrics)
    // Each telemetry reading cycle represents a 0.05 kWh energy monitoring block (50 Wh per cycle)
    const KWH_PER_CYCLE = 0.05;  // 50 Wh per cycle
    const TARIFF_PER_KWH = 7.50; // ₹ 7.50 per kWh municipal tariff
    const CO2_FACTOR = 0.82;     // 0.82 kg CO2 per kWh avoided

    const energyConsumedKwh = onCount * KWH_PER_CYCLE;
    const energySavedKwh = offCount * KWH_PER_CYCLE;
    const energySavedPct = total > 0 ? (offCount / total) * 100 : 0;
    const costSavedInr = energySavedKwh * TARIFF_PER_KWH;
    const co2AvoidedKg = energySavedKwh * CO2_FACTOR;

    res.json({
      total_records: total,
      led_on_records: onCount,
      led_off_records: offCount,
      energy_consumed_kwh: Number(energyConsumedKwh.toFixed(2)),
      energy_saved_kwh: Number(energySavedKwh.toFixed(2)),
      energy_saved_pct: Number(energySavedPct.toFixed(1)),
      cost_saved_inr: Number(costSavedInr.toFixed(2)),
      co2_avoided_kg: Number(co2AvoidedKg.toFixed(2))
    });
  } catch (e) {
    res.status(500).json({ error: 'Could not fetch summary' });
  }
});

app.listen(PORT, '0.0.0.0', () => console.log(`Backend listening on ${PORT}`));
