import logging
import requests
import schedule
import time
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GROUP_ID = "-1002192776630"

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Função para obter dados do clima
def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?q=Salvador,BR&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        main = data['main']
        weather_desc = data['weather'][0]['description']
        temp = main['temp']
        feels_like = main['feels_like']
        humidity = main['humidity']
        wind_speed = data['wind']['speed']

        weather_report = (
            f"Clima em Salvador, BA:\n"
            f"Descrição: {weather_desc}\n"
            f"Temperatura: {temp}°C\n"
            f"Sensação Térmica: {feels_like}°C\n"
            f"Humidade: {humidity}%\n"
            f"Velocidade do Vento: {wind_speed} m/s\n"
        )
        return weather_report
    else:
        return "Não foi possível obter os dados do clima no momento."

# Função para enviar a mensagem do clima
def send_weather(context: CallbackContext):
    weather_report = get_weather()
    context.bot.send_message(chat_id=GROUP_ID, text=weather_report)

# Função para configurar o agendamento
def schedule_daily_weather(updater):
    job_queue = updater.job_queue
    job_queue.run_daily(send_weather, time=datetime.strptime('01:00', '%H:%M').time())

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Olá! Eu vou te enviar a previsão do tempo diariamente às 1:00 AM.')

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Agendar o envio diário da previsão do tempo
    schedule_daily_weather(updater)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
