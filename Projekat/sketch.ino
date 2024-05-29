#define BLYNK_TEMPLATE_ID "TMPL4fkA2Wv_9"
#define BLYNK_TEMPLATE_NAME "Temperature Monitoring"
#define BLYNK_AUTH_TOKEN "EDXOD9lwdmJVdZdnXmGcgtEUWKxwvi7H"

#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <Wire.h>
#include <DHT.h>

#define DHTPIN 15
#define POTENTIOMETER_PIN 34
#define DHTTYPE DHT22
#define READ_PERIOD 1000L

char auth[] = BLYNK_AUTH_TOKEN;

char ssid[] = "Wokwi-GUEST";
char pass[] = "";

BlynkTimer timer;

DHT dht(DHTPIN, DHTTYPE);

void sendSensor()
{
  
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  int potentiometerData = analogRead(POTENTIOMETER_PIN);
  float pressure = map(potentiometerData, 0, 4095, 300, 1100);

  if (isnan(humidity) || isnan(temperature)) {

    Serial.println("Failed to read from DHT sensor!");
    return;
  }

    Blynk.virtualWrite(V0, temperature);
    Blynk.virtualWrite(V1, humidity);
    Blynk.virtualWrite(V2, pressure);

    Serial.print("Temperature : ");
    Serial.print(temperature);
    Serial.println("°C");
    Serial.print("Humidity : ");
    Serial.print(humidity);
    Serial.println("%");
    Serial.print("Atmospheric Pressure : ");
    Serial.print(pressure);
    Serial.println("mb");
}

void setup()
{   
  
  Serial.begin(115200);

  Blynk.begin(auth, ssid, pass);
  dht.begin();
  timer.setInterval(1000L, sendSensor);
}

void loop()
{

  Blynk.run();
  timer.run();
}