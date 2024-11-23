from pymongo import MongoClient
# Connessione al server MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Modifica l'URI con le informazioni del tuo server MongoDB

# Seleziona il database e la collezione per i dati e la whitelist
db = client['IoT_test']
data_collection = db['dati_vigna_test']