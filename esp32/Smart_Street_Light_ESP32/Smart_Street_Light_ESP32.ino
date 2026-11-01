#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// ========== WI-FI SETTINGS ==========
const char* ssid = "REDMI 15C";
const char* password = "qfvq1983";

// ========== CLOUD BACKEND SETTINGS ==========
// When hosted on Render, use your Render service URL:
// Example: "https://your-service-name.onrender.com/api/readings"
// If testing locally on your PC, use your local IP with HTTP:
// Example: "http://192.168.40.165:3000/api/readings"
const char* serverUrl = "https://esp32-smart-street-light.onrender.com/api/readings";
const char* deviceId = "esp32_street_01";

// Telemetry interval (milliseconds)
const unsigned long SEND_INTERVAL_MS = 5000;

// ========== PIN CONFIGURATION ==========
// P2  = GPIO2 (Built-in or external LED)
// P27 = GPIO27 (LDR Digital Output DO pin)
const int LED_PIN = 2;
const int LDR_DO_PIN = 27;

// Set HIGH if DO is HIGH in darkness.
// Change to LOW if DO is LOW in darkness.
const int DARK_LEVEL = HIGH;

// ========== LOCAL WEB SERVER (DIAGNOSTICS) ==========
WebServer server(80);

// ========== SYSTEM VARIABLES ==========
bool isDark = false;
bool ledState = false;
int sensorValue = HIGH;
bool lastDarkState = false;
unsigned long lastSendTime = 0;

// ========== READ SENSOR AND CONTROL LED ==========
void updateStreetLight() {
  sensorValue = digitalRead(LDR_DO_PIN);
  isDark = (sensorValue == DARK_LEVEL);
  ledState = isDark;
  digitalWrite(LED_PIN, ledState ? HIGH : LOW);
}

// ========== SEND TELEMETRY TO CLOUD (RENDER / LOCAL) ==========
void sendTelemetry() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[Cloud] Wi-Fi not connected. Skipping send.");
    return;
  }

  // Construct JSON payload matching the backend schema
  String payload = "{";
  payload += "\"device_id\":\"" + String(deviceId) + "\",";
  payload += "\"sensor\":" + String(sensorValue) + ",";
  payload += "\"ambient\":\"" + String(isDark ? "Dark" : "Bright") + "\",";
  payload += "\"led\":\"" + String(ledState ? "ON" : "OFF") + "\"";
  payload += "}";

  // Ensure target URL points to /api/readings endpoint
  String endpointUrl = String(serverUrl);
  endpointUrl.trim();
  if (!endpointUrl.endsWith("/api/readings")) {
    if (endpointUrl.endsWith("/")) {
      endpointUrl += "api/readings";
    } else {
      endpointUrl += "/api/readings";
    }
  }

  Serial.println("[Cloud] Sending payload: " + payload);

  HTTPClient http;
  bool isHttps = endpointUrl.startsWith("https://");

  if (isHttps) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure(); // Skip certificate verification for cloud endpoints
    http.begin(secureClient, endpointUrl);
  } else {
    WiFiClient plainClient;
    http.begin(plainClient, endpointUrl);
  }

  http.addHeader("Content-Type", "application/json");
  http.setTimeout(15000); // 15s timeout to handle Render cold-starts gracefully

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    Serial.printf("[Cloud] POST %s -> HTTP %d\n", endpointUrl.c_str(), httpCode);
    if (httpCode == 201) {
      Serial.println("[Cloud] Success! Reading recorded in database.");
    }
  } else {
    Serial.printf("[Cloud] POST failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// ========== LOCAL WEBPAGE (DIAGNOSTICS) ==========
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Street Light - Local Diagnostic</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; background: #101827; color: white; margin: 0; padding: 15px; }
    .card { background: #1f2a40; max-width: 420px; margin: 20px auto; padding: 25px; border-radius: 18px; box-shadow: 0 5px 20px #0005; }
    h1 { color: #facc15; }
    .light { font-size: 75px; margin: 20px; }
    .info { background: #303e56; padding: 15px; margin: 12px 0; border-radius: 12px; }
    .status { font-size: 26px; font-weight: bold; margin-top: 12px; }
    .on { color: #facc15; }
    .off { color: #cbd5e1; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Smart Street Light</h1>
    <p>ESP32 Node Status</p>
    <div class="light" id="bulb">💡</div>
    <div class="info">Ambient Condition: <div class="status" id="ambient">Loading...</div></div>
    <div class="info">Street Light LED: <div class="status" id="led">Loading...</div></div>
    <div class="info">LDR DO Pin: <div class="status" id="sensor">--</div></div>
  </div>
  <script>
    async function update() {
      try {
        const res = await fetch('/status');
        const d = await res.json();
        document.getElementById('ambient').textContent = d.ambient;
        const led = document.getElementById('led');
        led.textContent = d.led;
        led.className = 'status ' + (d.led === 'ON' ? 'on' : 'off');
        document.getElementById('sensor').textContent = d.sensor;
        document.getElementById('bulb').textContent = d.led === 'ON' ? '💡' : '🌑';
      } catch(e) {}
    }
    update(); setInterval(update, 1000);
  </script>
</body>
</html>
)rawliteral";
  server.send(200, "text/html", html);
}

void handleStatus() {
  updateStreetLight();
  String json = "{";
  json += "\"ambient\":\"" + String(isDark ? "Dark" : "Bright") + "\",";
  json += "\"led\":\"" + String(ledState ? "ON" : "OFF") + "\",";
  json += "\"sensor\":" + String(sensorValue);
  json += "}";
  server.send(200, "application/json", json);
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);
  pinMode(LDR_DO_PIN, INPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.println();
  Serial.println("==========================================");
  Serial.println(" ESP32 Smart Street Light (Cloud Ready) ");
  Serial.println("==========================================");

  // Initial read
  updateStreetLight();
  lastDarkState = isDark;

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected!");
    Serial.print("ESP32 Local IP: ");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.on("/status", handleStatus);
    server.begin();
    Serial.println("Local diagnostic server started at port 80.");

    // Send first reading immediately on boot
    sendTelemetry();
    lastSendTime = millis();
  } else {
    Serial.println("Wi-Fi connection failed. Street light will operate offline.");
  }
}

// ========== MAIN LOOP ==========
void loop() {
  // Update sensor and LED actuator in real-time
  updateStreetLight();

  // If connected, serve local diagnostic webpage
  if (WiFi.status() == WL_CONNECTED) {
    server.handleClient();
  }

  // Detect state change or timer expiration for cloud telemetry
  unsigned long now = millis();
  bool stateChanged = (isDark != lastDarkState);
  bool timerExpired = (now - lastSendTime >= SEND_INTERVAL_MS);

  if (stateChanged || timerExpired) {
    if (stateChanged) {
      Serial.println("[Event] Light level changed! Triggering instant cloud update.");
      lastDarkState = isDark;
    }
    sendTelemetry();
    lastSendTime = now;
  }

  delay(50);
}
