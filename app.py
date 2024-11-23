from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher, ConversationHandler
import logging
import json
import sys
import io
import os
from pymongo import MongoClient
from datetime import datetime
from conf_db import *
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


whitelist = []# <---- INSERT HERE THE USERNAMES

global_counter = 0

#------------THRESHOLDS-------------------
MAX_UMIDITY = 50 # 80%
MAX_TEMP = 40 # 40°C

# Recupera i nomi di tutte le collection nel database
#collections = db.list_collection_names()


# Recupera l'ultimo documento--------------------------------------------------------------------------------

def extract_last_doc():
    last_document_cursor = data_collection.find().sort([('timestamp', -1)]).limit(1)
    last_document = next(last_document_cursor, None)
    return dict(last_document)


app = Flask(__name__)  # Istanzio una classe
TOKEN = ""  # <----------------   Sostituisci con il token del tuo bot
bot = Bot(TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)
# Stati per il ConversationHandler
SELECTING_CLUSTER = range(1)
SELECTING_FIRST_CLUSTER, SELECTING_SECOND_CLUSTER, CALCULATING = range(3)
ASK_FIRST_CLUSTER, ASK_SECOND_CLUSTER = range(2)

# Abilita il logging per debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# Funzione per verificare la whitelist
def is_user_authorized(update, context):
    user_id = update.message.from_user.username
    if user_id not in whitelist:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Accesso negato.")
        return False
    return True

#INIZIO 3 FUNZIONI X COMPARAZIONE CLUSTER
# Function to start the conversation and ask for the first cluster


def start_compare_clusters(update, context):
    if is_user_authorized(update, context):
        update.message.reply_text("Please enter the name of the first cluster:")
        return ASK_FIRST_CLUSTER
    else:
        update.message.reply_text("You are not authorized to perform this action.")
        return ConversationHandler.END


# Function to handle the input of the first cluster
def ask_first_cluster(update, context):
    context.user_data['first_cluster'] = update.message.text.strip()
    update.message.reply_text("Please enter the name of the second cluster:")
    return ASK_SECOND_CLUSTER

# Function to handle the input of the second cluster and compare the clusters

def ask_second_cluster(update, context):
    context.user_data['second_cluster'] = update.message.text.strip()
    first_cluster = context.user_data['first_cluster']
    second_cluster = context.user_data['second_cluster']

    # Perform the comparison
    result_message = compare_clusters_by_humidity(first_cluster, second_cluster)
    update.message.reply_text(result_message)

    return ConversationHandler.END


# Funzione di gestione del comando '/start'
def start(update, context):
    if is_user_authorized(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")


# Funzione per stampare i dati dell'ultimo documento in caso di errore del sensore
def dati(update, context):
    if is_user_authorized(update, context):
        sample_dict = extract_last_doc()
        dict_str = "\n".join([f"{key}: {value}" for key, value in sample_dict.items()])
        humidity = sample_dict['humidity']
        temperature = sample_dict['temperature']
        if humidity > MAX_UMIDITY:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Humidity is higher than threshold")
        if temperature > MAX_TEMP:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Temperature is higher than threshold")
        context.bot.send_message(chat_id=update.effective_chat.id, text=dict_str)


# Funzione per listare i cluster disponibili
def list_clusters(update, context):
    if is_user_authorized(update, context):
        # Recupera i nomi di tutte le collection nel database
        collections = db.list_collection_names()

        # Filtra le collection di sistema
        filtered_collections = [
            coll for coll in collections
            if not coll.startswith("system.") and not coll.startswith("system.buckets.")
        ]

        if filtered_collections:
            collections_str = "\n".join(filtered_collections)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Clusters:\n{collections_str}\n\nPlease type the name of the cluster you want to view:")
            return SELECTING_CLUSTER
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No clusters found in the database.")
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You are not authorized to perform this action.")
        return ConversationHandler.END


# Funzione per stampare tutti i documenti presenti in una collection
def all_data(update, context, collection_name: str):
    if is_user_authorized(update, context):
        # Seleziona la collection
        if collection_name not in db.list_collection_names():
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Cluster {collection_name} not found in the database.")
            return ConversationHandler.END

        data_collection = db[collection_name]

        # Recupera tutti i documenti nella collection
        all_documents_cursor = data_collection.find()
        all_documents = list(all_documents_cursor)

        if all_documents:
            for document in all_documents:
                dict_str = "\n".join([f"{key}: {value}" for key, value in document.items()])
                context.bot.send_message(chat_id=update.effective_chat.id, text=dict_str)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No documents found in the collection.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You are not authorized to perform this action.")

    return ConversationHandler.END


# Supporta la selezione da tastiera
def handle_cluster_selection(update, context):
    collection_name = update.message.text.strip()
    return all_data(update, context, collection_name)


# Funzione per avviare il processo di selezione della collezione
def start_calculation(update, context):
    if is_user_authorized(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Per favore, inserisci il nome della collezione che vuoi analizzare.")
        return SELECTING_CLUSTER
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Non sei autorizzato ad eseguire questa azione.")
        return ConversationHandler.END


# Funzione per gestire l'input del nome della collezione
def select_collection(update, context):
    collection_name = update.message.text.strip()
    context.user_data['selected_collection'] = collection_name
    return calculate_average_values(update, context, collection_name)


# Calcolo statistiche di un cluster
def calculate_average_values(update, context, collection_name):
    # Seleziona la collection
    data_collection = db[collection_name]

    # Recupera tutti i documenti nella collection
    all_documents_cursor = data_collection.find()
    all_documents = list(all_documents_cursor)

    if all_documents:
        # Inizializza i totali per il calcolo della media
        total_humidity = 0
        total_temp = 0
        total_soil_moist = 0
        total_luminosity = 0
        count = 0

        # Itera attraverso ogni documento
        for document in all_documents:
            if "humidity" in document and "temperature" in document and "soilMoisture" in document and "lightIntensity" in document:
                total_humidity += document["humidity"]
                total_temp += document["temperature"]
                total_soil_moist += document["soilMoisture"]
                total_luminosity += document["lightIntensity"]
                count += 1

        if count > 0:
            # Calcola la media
            avg_humidity = total_humidity / count
            avg_temp = total_temp / count
            avg_soil_moist = total_soil_moist / count
            avg_luminosity = total_luminosity / count

            # Costruisci il messaggio da inviare
            message = (
                f"Average Humidity: {avg_humidity}\n"
                f"Average Temperature: {avg_temp}\n"
                f"Average Soil Moisture: {avg_soil_moist}\n"
                f"Average Luminosity: {avg_luminosity}"
            )

            # Invia il messaggio all'utente
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Nessun documento trovato nella collezione.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Nessun documento trovato nella collezione.")

    return ConversationHandler.END


#Funzione per etichettare la temperatura in base al valore.PER ORA FUNZIONERA' DALL'UNICO ELEMENTO INSERITO NEL CLUSER2
def lobesia_risk(update, context):
    sample_dict = extract_last_doc()  # Estrazione delle ultime misurazioni per quel cluster
    temperature = sample_dict["temperature"]

    # Tentativo di convertire il valore di "temp" in float
    try:
        temp = float(temperature)
    except (ValueError, TypeError):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid temperature value.")
        return

    # Determinazione del rischio di lobesia in base alla temperatura
    if temp > 35 or temp < 10:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Rischio lobesia BASSO")
    elif 25 <= temp <= 30:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Rischio lobesia ALTO")
    elif 30 < temp <= 35 or 10 < temp < 25:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Rischio lobesia MEDIO")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Valore di temperatura non valido.")

# Per la funzione benessere tra cluster richiamo la funzione media tra due cluster "VICINI"
# mi salvo i risultati in un dizionario e in base al valore di umidità stampo quale è quello più sano


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Operation cancelled.")
    return ConversationHandler.END



# Aggiungi gli handler per i comandi e i messaggi
start_handler = CommandHandler('start', start)
# echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dati_handler = CommandHandler('dati', dati)
# list_collection_handler = CommandHandler('list_clusters', list_clusters)
avarage_values_handler = CommandHandler('avarage_values', calculate_average_values)
lobesia_risk_handler = CommandHandler('lobesia_risk',
                                      lobesia_risk)  # Definizione dell'handler per il comando /lobesia_risk

# nei miei test non funziona lobesia_risk e /avarage_values
# per listare i cluster listclusters e per la media usa calculate_average

# Aggiungi il gestore di comando per /listclustersci
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('listclusters', list_clusters)],
    states={
        # quiiiiiiiiiiiiiiiiiii-------------------------
        SELECTING_CLUSTER: [MessageHandler(Filters.text & ~Filters.command, handle_cluster_selection)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Configura il ConversationHandler per gestire l'input del nome della collezione
conv_handler_2 = ConversationHandler(
    entry_points=[CommandHandler('calculate_average', start_calculation)],
    states={
        SELECTING_CLUSTER: [MessageHandler(Filters.text & ~Filters.command, select_collection)],
    },
    fallbacks=[],
)

# Add the conversation handler to the dispatcher
compare_clusters_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('compare_clusters', start_compare_clusters)],
    states={
        ASK_FIRST_CLUSTER: [MessageHandler(Filters.text & ~Filters.command, ask_first_cluster)],
        ASK_SECOND_CLUSTER: [MessageHandler(Filters.text & ~Filters.command, ask_second_cluster)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


dispatcher.add_handler(compare_clusters_conv_handler)


# Function to compare the average humidity of two clusters
def compare_clusters_by_humidity(cluster1, cluster2):
    def calculate_average_humidity(collection_name):
        # Seleziona la collection
        data_collection = db[collection_name]

        # Recupera tutti i documenti nella collection
        all_documents_cursor = data_collection.find()
        all_documents = list(all_documents_cursor)

        if all_documents:
            total_humidity = 0
            count = 0

            # Itera attraverso ogni documento
            for document in all_documents:
                if "humidity" in document:
                    total_humidity += document["humidity"]
                    count += 1

            if count > 0:
                avg_humidity = total_humidity / count
                return avg_humidity
            else:
                return None
        else:
            return None

    avg_humidity_cluster1 = calculate_average_humidity(cluster1)
    avg_humidity_cluster2 = calculate_average_humidity(cluster2)

    if avg_humidity_cluster1 is None and avg_humidity_cluster2 is None:
        return "No documents found in both collections."
    elif avg_humidity_cluster1 is None:
        return f"The cluster {cluster2} has an average humidity of {avg_humidity_cluster2}. The cluster {cluster1} does not contain documents with humidity data."
    elif avg_humidity_cluster2 is None:
        return f"The cluster {cluster1} has an average humidity of {avg_humidity_cluster1}. The cluster {cluster2} does not contain documents with humidity data."
    else:
        if avg_humidity_cluster1 < avg_humidity_cluster2:
            return f"The cluster {cluster1} has a lower average humidity ({avg_humidity_cluster1}) compared to the cluster {cluster2} ({avg_humidity_cluster2})."
        else:
            return f"The cluster {cluster2} has a lower average humidity ({avg_humidity_cluster2}) compared to the cluster {cluster1} ({avg_humidity_cluster1})."


#Seconda versione confronto tra clusters
def compare_clusters_handler(update, context):
    if is_user_authorized(update, context):
        try:
            cluster1, cluster2 = context.args
            result_message = compare_clusters_by_humidity(cluster1, cluster2)
            context.bot.send_message(chat_id=update.effective_chat.id, text=result_message)
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Per favore, specifica due nomi di cluster separati da uno spazio.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Non sei autorizzato ad eseguire questa azione.")


compare_clusters_command_handler = CommandHandler('compare_clusters', compare_clusters_handler)
dispatcher.add_handler(compare_clusters_command_handler)
# Aggiunta degli handler al dispatcher

dispatcher.add_handler(conv_handler_2)

# Aggiunta dell'handler al dispatcher del bot
dispatcher.add_handler(lobesia_risk_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(dati_handler)
dispatcher.add_handler(conv_handler)
dispatcher.add_handler(avarage_values_handler)


# Endpoint per il webhook
@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return 'OK'


@app.route('/echoBot', methods=['POST'])
def webhook():
    print(request.get_json())
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"


if __name__ == '__main__':
    app.run()  # Avvia l'app Flask su una porta specifica
