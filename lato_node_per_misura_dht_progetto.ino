#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>
#define RX_PIN D2 
#define TX_PIN D3 
SoftwareSerial mySerial(TX_PIN, RX_PIN);
// Configurazione del WiFi
const char* ssid = ""; //<-------
const char* password = "";//<-----

// Configurazione del broker MQTT
const char* mqtt_server = "broker.mqttdashboard.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "IoT_measures/data";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(9600);
  //mySerial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  // Lettura dei dati inviati dall'Arduino
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    // Invio dei dati al broker MQTT
    Serial.print("Publishing data: ");
    Serial.println(data);
    client.publish(mqtt_topic, data.c_str());
  }
  

}

void setup_wifi() {
  delay(10);
  // Connessione al WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop fino a quando non viene stabilita la connessione
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Tentativo di connessione
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Attendi 5 secondi prima di riprovare
      delay(5000);
    }
  }
}