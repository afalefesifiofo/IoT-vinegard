#include <DHT.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// Definizione dei pin dei sensori
#define SOIL_MOISTURE_PIN A0
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define PHOTORESISTOR_PIN A1

// Definizione dei pin per la SoftwareSerial
#define RX_PIN 2
#define TX_PIN 3

// Inizializzazione del sensore DHT
DHT dht(DHT_PIN, DHT_TYPE);

// Inizializzazione della SoftwareSerial
SoftwareSerial mySerial(TX_PIN, RX_PIN); 

void setup() {
  Serial.begin(9600);// Comunicazione seriale con il computer
  //mySerial.begin(9600);    // Comunicazione seriale con il NodeMCU
  dht.begin();
}

void loop() {
  // Lettura dei dati dal sensore di umidità del terreno
  int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  String soilLevel = ""; 
  
if (soilMoistureValue < 400) {
    soilLevel = "WET";  // Umidità alta
} else if (soilMoistureValue >= 400 && soilMoistureValue <= 500) {
    soilLevel = "MEDIUM WET";  // Umidità media
} else if(soilMoistureValue > 500){
    soilLevel = "DRY";  // Terreno secco
}


  // Lettura dei dati dal sensore DHT11
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Lettura dei dati dal fotoresistore
  int lightIntensity = analogRead(PHOTORESISTOR_PIN);

    String lightLevel =""; 
  
if (lightIntensity < 30) {
    lightLevel = "HIGH";  // LUMINOSITA alta
} else if (lightIntensity >= 30 && lightIntensity <= 130 ) {
    lightLevel = "MEDIUM";  // LUMINOSITA media
} else if (lightIntensity > 130){
    lightLevel = "LOW";  // LUMINOSITA BASSA
}

  // Creazione di un oggetto JSON
  StaticJsonDocument<200> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soilMoisture"] = soilLevel;
  doc["lightIntensity"] = lightLevel;

  // Serializzazione del documento JSON in una stringa
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);

  // Invio dei dati via seriale al NodeMCU
  Serial.println(jsonBuffer);
    // Invio alla porta seriale software

  delay(10000); // Attendi 10 secondi prima di eseguire una nuova lettura
}
