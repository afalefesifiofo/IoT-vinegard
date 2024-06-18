from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher
import logging
from pymongo import MongoClient

app = Flask(__name__)
TOKEN = "my_token"  # Sostituisci con il token del tuo bot
bot = Bot(TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Abilita il logging per debug
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Sostituisci con il tuo URI MongoDB
db = client["nome_del_tuo_database"]
collection = db["nome_della_tua_collezione"]

# Funzione per recuperare i dati del sensore
def get_sensor_data():
    data = collection.find_one(sort=[('_id', -1)])  # Trova l'ultimo documento inserito
    if data:
        temperatura = data.get("temperatura", "N/A")
        umidita_aria = data.get("umidita_aria", "N/A")
        umidita_terreno = data.get("umidita_terreno", "N/A")
        return f"Temperatura: {temperatura}°C\nUmidità Aria: {umidita_aria}%\nUmidità Terreno: {umidita_terreno}%"
    else:
        return "Nessun dato disponibile."

# Funzione di gestione del comando '/start'
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ciao! Usa /dati per ottenere i dati del sensore.")

# Funzione di gestione del comando '/dati'
def dati(update, context):
    sensor_data = get_sensor_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text=sensor_data)

# Aggiungi gli handler per i comandi e i messaggi
start_handler = CommandHandler('start', start)
dati_handler = CommandHandler('dati', dati)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(dati_handler)

# Endpoint per il webhook
@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return 'OK'

if __name__ == '__main__':
    app.run()
