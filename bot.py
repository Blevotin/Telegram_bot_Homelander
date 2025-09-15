from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from telegram.ext import MessageHandler, filters
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен!")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.args:
        city = context.args[0]
        url = f"https://api.weatherapi.com/v1/current.json?key=6465d9942ba74529b9a135645250509&q={city}&lang=ru"
        response = requests.get(url)
        data = response.json()
        temperature = data['current']['temp_c']
        description = data['current']['condition']['text']
        await update.message.reply_text(f"В {city} {temperature}°C, {description}")
    else:
        await update.message.reply_text(f"Напиши /weather и город")


from datetime import datetime


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_date = datetime(2025, 11, 6)  # Целевая дата
    current_date = datetime.now()  # Текущая дата
    time_left = target_date - current_date  # Разница

    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    seconds = time_left.seconds % 60

    await update.message.reply_text(f"До дембеля: {days} дней, {hours} часов, {minutes} минут, {seconds} секунд")


async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        a = f"https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_TXj6w119qbwxQiTKMU67WSAWvbjJnvsjqvmuD8Oj&currencies=RUB%2CEUR%2CUSD"
        b = requests.get(a)
        data = b.json()
        ru = data['data']['RUB']
        await update.message.reply_text(f"Курс Рубля = {ru}")



async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()  # Приводим к нижнему регистру

    if "привет" in user_text:
        await update.message.reply_text("И тебе привет! 😊")
    elif "как дела" in user_text:
        await update.message.reply_text("Отлично! А у тебя?")
    elif "дима" in user_text or "диме" in user_text or "димасик" in user_text:
        await update.message.reply_text("Оооо, Димасик, слышал о нем, классный парень @gygygy44")
    elif "давай краба" in user_text:
        await update.message.reply_text("На🦀")
    elif "ты пидор?" in user_text:
        await update.message.reply_text("да!")
    elif "хуйня на голове" in user_text or "херня на головн" in user_text:
        await update.message.reply_text("мой парень любит когда есть за что держаться!")
    elif "а че так гордо?" in user_text:
        await update.message.reply_text("Я гордый пидорасик!")
    else:
        return



TOKEN = "8226370714:AAHyhzM0QuoYOPihLn_npm4KUc8BRSc7ItY"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("kurs", kurs))
app.add_handler(CommandHandler("data", timer))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("Бот запущен!")
app.run_polling()