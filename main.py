import threading
import paho.mqtt.client as mqtt
import json
from conf_db import *
import logging
from pymongo import MongoClient
from datetime import datetime

global_temperature = None
global_humidity = None
global_soil_moisture = None
global_light_intensity = None

# Abilita il logging per debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



# Funzione per gestire il messaggio in arrivo
def handle_message(payload):
    global global_temperature, global_humidity, global_soil_moisture, global_light_intensity

    data = json.loads(payload)
    global_temperature = data.get("temperature")
    global_humidity = data.get("humidity")
    global_soil_moisture = data.get("soilMoisture")
    global_light_intensity = data.get("lightIntensity")

    data_dict = create_dict()
    data_collection.insert_one(data_dict)
    print("Data uploaded on db")


# Callback che viene chiamata quando viene ricevuto un messaggio
def on_message(client, userdata, message):
    print(f"Received message '{message.payload}' on topic '{message.topic}'")
    payload = message.payload.decode('utf-8')

    # Creare un thread per gestire il messaggio
    threading.Thread(target=handle_message, args=(payload,)).start()


# Callback che viene chiamata quando il client si connette al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("IoT_measures/data")
    else:
        print("Connection failed. Return code =", rc)


def create_dict():

    # Crea un dizionario con le variabili
    data = {
        "temperature": global_temperature,
        "humidity": global_humidity,
        "soilMoisture": global_soil_moisture,
        "lightIntensity": global_light_intensity,
        "time": datetime.now()

    }
    return data

if __name__ == "__main__":
    # Configurazione del client MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Configurazione della connessione al broker MQTT
    mqtt_server = "broker.mqttdashboard.com"
    mqtt_port = 1883

    client.connect(mqtt_server, mqtt_port, 60)

    # Inizia il loop per gestire le connessioni e i messaggi
    client.loop_forever()
