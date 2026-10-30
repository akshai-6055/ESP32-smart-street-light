# ESP32 Smart Street Light — Node.js + PostgreSQL (Cloud & Docker)

A complete IoT Smart Street Light system featuring:
- **ESP32 Node**: Hardware control of LED from LDR sensor, sends telemetry over HTTPS/HTTP.
- **Node.js/Express Backend**: REST API with real-time health checks, metrics, and summary data.
- **PostgreSQL**: Native cloud database support (1-click on Render) and local Docker support.
- **Live Dashboard**: Interactive UI with Chart.js displaying sensor trends, state distribution, and telemetry records.

---

## 1. Quick Deploy to Render (Easiest Method)

Render provides a native free PostgreSQL database and free Node.js Web Service. Thanks to [`render.yaml`](./render.yaml), you can deploy both together automatically.

### Step 1: Push Code to GitHub
In PowerShell inside this project folder:
```powershell
git init
git add .
git commit -m "ESP32 Smart Street Light ready for Render"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

### Step 2: Deploy on Render via Blueprint
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Blueprint**.
3. Connect your GitHub repository.
4. Render will read [`render.yaml`](./render.yaml) and automatically configure:
   - **PostgreSQL Database**: `streetlight-postgres` (Free tier)
   - **Web Service**: `esp32-smart-street-light` (Free tier)
   - Automatic `DATABASE_URL` linking between the database and web service.
5. Click **Apply**.
6. The service will build and launch. Once finished, Render gives you an HTTPS URL:
   ```text
   https://esp32-smart-street-light.onrender.com
   ```
   *Note: The database table `sensor_readings` is created automatically on the first server boot!*

### Step 3: Flash ESP32
1. Open [`esp32/Smart_Street_Light_ESP32/Smart_Street_Light_ESP32.ino`](./esp32/Smart_Street_Light_ESP32/Smart_Street_Light_ESP32.ino) in Arduino IDE.
2. Put your Render URL in `serverUrl`:
   ```cpp
   const char* serverUrl = "https://esp32-smart-street-light.onrender.com/api/readings";
   ```
3. Upload sketch to ESP32 and open Serial Monitor at **115200 baud** to see live transmissions.

---

## 2. API Endpoints

- `GET  /api/health` — Checks database connectivity.
- `POST /api/readings` — Receives telemetry (`{"device_id":"...", "sensor":1, "ambient":"Dark", "led":"ON"}`).
- `GET  /api/readings/latest` — Retrieves latest sensor reading.
- `GET  /api/readings?limit=50` — Retrieves historical readings.
- `GET  /api/summary` — Aggregates total records and LED ON/OFF statistics.

---

## 3. Local Development (Optional)

If you wish to run locally:

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Start containers (if Docker is installed):
   ```powershell
   docker compose up --build -d
   ```
3. Or run Node directly (if PostgreSQL is installed locally):
   ```powershell
   npm install
   npm start
   ```
4. Dashboard is available at `http://localhost:3000`.
