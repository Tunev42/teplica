#include <OneWire.h>
#include <DallasTemperature.h>

const int RELAY_PIN = 2;
const int SOIL_PIN = A0;
const int TEMP_PIN = 3;

const int SOIL_DRY = 350;
const int SOIL_WET = 600;
const float MAX_TEMP = 28.0;

OneWire oneWire(TEMP_PIN);
DallasTemperature sensors(&oneWire);

int soilMoisture = 0;
float temperature = 0.0;
bool pumpIsOn = false;

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  Serial.begin(9600);
  sensors.begin();
  delay(1000);

  Serial.println("=== Umnica Teplica v.1.2 ===");
  Serial.println("System started");
}

void loop() {
  soilMoisture = analogRead(SOIL_PIN);

  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);

  if (soilMoisture < SOIL_DRY && !pumpIsOn) {
    digitalWrite(RELAY_PIN, LOW);
    pumpIsOn = true;
  }

  if (soilMoisture > SOIL_WET && pumpIsOn) {
    digitalWrite(RELAY_PIN, HIGH);
    pumpIsOn = false;
  }

  Serial.print(soilMoisture);
  Serial.print(",");
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.println(pumpIsOn ? "ON" : "OFF");

  if (temperature > MAX_TEMP) {
    Serial.print("WARNING: High temperature! ");
    Serial.println(temperature);
  }

  if (temperature == -127.0) {
    Serial.println("WARNING: Temp sensor not found!");
  }

  delay(2000);
}
