from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton

conn = sqlite3.connect('notes.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS notes (user_id INTEGER, text TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER, fio TEXT, age INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS product (id_product INTEGER, text TEXT, price REAL)')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        id_product INTEGER,
        quantity INTEGER DEFAULT 1,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (id_product) REFERENCES product(id_product)
    )
''')
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (11, 'Филадельфия', 500))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (1, 'Пицца Маргарита', 450 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (2, 'Бургер Классический', 350 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (3, 'Паста Карбонара', 380 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (4, 'Салат Цезарь', 350 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (5, 'Куриные крылышки', 400 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (6, 'Картофель фри', 200 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (7, 'Ролл Калифорния', 550 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (8, 'Чизкейк', 250 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (9, 'Кола', 120 ))
# cursor.execute('INSERT INTO product (id_product, text, price) VALUES (?, ?, ?)', (10, 'Кофе', 150 ))

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
cursor.execute("SELECT * FROM users")
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print("USERS TABLE:")
print("id | fio | age")
print("---------------")
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]}")

# Выводим таблицу product
cursor.execute("SELECT * FROM product")
rows = cursor.fetchall()

print("\nPRODUCT TABLE:")
print("order_id | text | price")
print("-------------------------")
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]}")

# Выводим таблицу product
cursor.execute("SELECT * FROM orders")
rows = cursor.fetchall()

print("\nORDERS TABLE:")
print("id_product | user_id | id_product | quantity | order_date")
print("----------------------------------------------------------")
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[4]}")

conn.commit()
GET_USER_DATA = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем кнопки
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", callback_data='button1')],
        [InlineKeyboardButton("Кнопка 2", callback_data='button2')],
        [InlineKeyboardButton("Меню", callback_data='menu')]
    ]

    # Создаем разметку клавиатуры
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    if query.data.startswith('item_'):
        # Достаем ID продукта из callback_data
        product_id = int(query.data.split('_')[1])

        # Проверяем регистрацию
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            await query.edit_message_text("❌ Сначала зарегистрируйтесь!")
            return

        # Получаем данные продукта из базы
        cursor.execute('SELECT text, price FROM product WHERE id_product = ?', (product_id,))
        product = cursor.fetchone()

        if product:
            name, price = product
            # Добавляем в заказ
            cursor.execute(
                'INSERT INTO orders (user_id, id_product, quantity) VALUES (?, ?, 1)',
                (user_id, product_id)
            )
            conn.commit()

            await query.edit_message_text(f"✅ {name} добавлен в заказ!\nЦена: {price}₽")

async def cbr_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://cbr.ru/currency_base/daily/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем таблицу по классу
        table = soup.find('table', class_='data')

        usd_rate = "не найдено"
        eur_rate = "не найдено"

        if table:
            # Ищем все строки таблицы (пропускаем заголовок)
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    currency_code = cols[1].text.strip()  # Буквенный код

                    if currency_code == 'USD':
                        usd_rate = cols[4].text.strip()  # Курс
                    elif currency_code == 'EUR':
                        eur_rate = cols[4].text.strip()
        symbol = "BTCUSDT"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

        response = requests.get(url)
        data = response.json()
        price = float(data['price'])  # ← КОНВЕРТИРУЕМ В ЧИСЛО
        rounded_price = round(price, 2)  # ← ОКРУГЛЯЕМ

        await update.message.reply_text(
            f"🏦 Курс ЦБ РФ:\n"
            f"🇺🇸 USD: {usd_rate} руб.\n"
            f"🇪🇺 EUR: {eur_rate} руб.\n"
            f"💵 BTC: {rounded_price} дол.\n"
        )

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

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

async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_date = datetime(2025, 11, 6)  # Целевая дата
    current_date = datetime.now()  # Текущая дата
    time_left = target_date - current_date  # Разница

    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    seconds = time_left.seconds % 60

    await update.message.reply_text(f"До дембеля: {days} дней, {hours} часов, {minutes} минут, {seconds} секунд")

async def binance_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = "BTCUSDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    response = requests.get(url)
    data = response.json()
    price = float(data['price'])  # ← КОНВЕРТИРУЕМ В ЧИСЛО
    rounded_price = round(price, 2)  # ← ОКРУГЛЯЕМ

    await update.message.reply_text(f"BTC: {rounded_price}$")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()  # Приводим к нижнему регистру
    user_id = update.effective_user.id

    if "привет" in user_text:
        await update.message.reply_text("И тебе привет! 😊")
    elif "как дела" in user_text:
        await update.message.reply_text("Отлично! А у тебя?")
    elif "дима" in user_text or "диме" in user_text or "димасик" in user_text:
        await update.message.reply_text("Оооо, Димасик, слышал о нем, классный парень")
    elif "давай краба" in user_text:
        await update.message.reply_text("На🦀")
    elif "ты пидор?" in user_text:
        await update.message.reply_text("да!")
    elif "хуйня на голове" in user_text or "херня на головн" in user_text:
        await update.message.reply_text("мой парень любит когда есть за что держаться!")
    elif "а че так гордо?" in user_text:
        await update.message.reply_text("Я гордый пидорасик!")
    elif "русик запиши" in user_text:
        if 'русик запиши, что' in user_text:
            note_text = user_text.split("русик запиши, что", 1)[1].strip()
        elif 'русик запиши что' in user_text:
            note_text = user_text.split("русик запиши что", 1)[1].strip()
        else:
            note_text = user_text.split("русик запиши", 1)[1].strip()

        cursor.execute('INSERT INTO notes VALUES (?, ?)', (user_id, note_text))
        conn.commit()
        await update.message.reply_text("✅ Записал!")

    elif "покажи ка ему" in user_text:
        await update.message.reply_text("вдох - выдох")

    elif "русик удали" in user_text:
        if "русик удали все" in user_text:
            # Удаляем все записи пользователя
            cursor.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
            conn.commit()
            await update.message.reply_text("🗑️ Все записи удалены!")
        else:
            # Удаляем конкретную запись
            note_to_delete = user_text.split("русик удали", 1)[1].strip()
            cursor.execute('DELETE FROM notes WHERE user_id = ? AND text = ?', (user_id, note_to_delete))
            conn.commit()

            if cursor.rowcount > 0:
                await update.message.reply_text(f"✅ Запись '{note_to_delete}' удалена!")
            else:
                await update.message.reply_text("❌ Запись не найдена!")

    elif "русик покажи" in user_text:
        # Достаем все записи пользователя
        cursor.execute('SELECT text FROM notes WHERE user_id = ?', (user_id,))
        notes = cursor.fetchall()

        if notes:
            # Формируем список записей
            notes_list = "\n".join([f"• {note[0]}" for note in notes])
            await update.message.reply_text(f"📝 Ваши записи:\n{notes_list}")
        else:
            await update.message.reply_text("📝 Записей пока нет!")
    else:
        return

async def wb_parser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    print(query)

    params = {
        'query': query,
        'appType': '1',
        'curr': 'rub',
        'dest': '-1123297',
        'resultset': 'catalog',
        'spp': '30',
        'lang': 'ru',
        'page': '1',
    }

    try:
        response = requests.get('https://recom.wb.ru/personal/ru/common/v8/search', params=params)

        # ПЕРВОЕ: проверяем статус ответа
        if response.status_code != 200:
            await update.message.reply_text(f"Ошибка API: {response.status_code}")
            return

        data = response.json()
        products = data.get('products', [])

        # ВТОРОЕ: проверяем специальные команды
        if query.lower() == 'количество':
            await update.message.reply_text(f'Количество товаров: {len(products)}')
            return

        # ТРЕТЬЕ: выводим товары
        if products:
              # Берем 1 товар
                product = products[1]
                name = product.get('name', 'Название не указано')
                brand = product.get('brand', 'Бренд не указан')
                price = product.get('sizes', [{}])[0].get('price', {}).get('product', 0) / 100
                rating = product.get('reviewRating', 0)
                feedbacks = product.get('feedbacks', 0)

                await update.message.reply_text(
                    f"🛍️ {brand} - {name}\n"
                    f"💰 Цена: {price} руб.\n"
                    f"⭐ Рейтинг: {rating}\n"
                    f"📊 Отзывы: {feedbacks}\n"
                    f"🔗 https://www.wildberries.ru/catalog/{product['id']}/detail.aspx"
                )
        else:
            await update.message.reply_text("Товары не найдены")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def get_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Настраиваем Selenium
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Фоновый режим
        driver = webdriver.Chrome(options=options)

        driver.get("https://gumrf.ru/?ysclid=mff5t7hfbq177393887")

        # Ждем пока JavaScript выполнится и элемент появится
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "GetWeek"))
        )

        week_text = element.text.lower()  # "Числитель (нечётная неделя)" или "Знаменатель (чётная неделя)"

        driver.quit()

        await update.message.reply_text(f"📅 {week_text}")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def place_an_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['in_conversation'] = True
    try:
        await update.message.reply_text("Пожалуйста, введите ваши данные в формате: Фамилия Имя Отчество Возраст")
        return GET_USER_DATA
    except Exception as e:
        await update.message.reply_text(f"Ошибка:")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("пизда")

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        a = update.message.text
        data = a.split()
        user_id = update.effective_user.id

        # Проверяем, зарегистрирован ли уже пользователь
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        user_exists = cursor.fetchone() is not None

        if user_exists:
            await update.message.reply_text("Вы уже зарегистрированы!")
            return ConversationHandler.END  # ← ВАЖНО: завершаем диалог

        if len(data) >= 4:
            fio = data[0] + ' ' + data[1] + ' ' + data[2]
            age = data[3]

            cursor.execute('INSERT INTO users (user_id, fio, age) VALUES (?, ?, ?)',
                           (user_id, fio, age))
            conn.commit()
            await update.message.reply_text(f"Данные сохранены {fio} {age} лет!")

            # Показываем меню после регистрации
            await next_function(update, context)
            return ConversationHandler.END  # ← ВАЖНО: завершаем диалог
        else:
            await update.message.reply_text("Недостаточно данных. Введите: Фамилия Имя Отчество Возраст")
            return GET_USER_DATA  # ← Остаемся в том же состоянии для повторного ввода

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")
        return ConversationHandler.END  # ← Завершаем при ошибке

async def next_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Берем ВСЕ продукты из базы
    cursor.execute('SELECT id_product, text, price FROM product')
    products = cursor.fetchall()

    # Создаем кнопки из базы
    keyboard = []
    for product in products:
        product_id, name, price = product
        # callback_data содержит ID продукта
        keyboard.append([InlineKeyboardButton(f"{name} - {price}₽", callback_data=f'item_{product_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🍽️ Меню:", reply_markup=reply_markup)

TOKEN = "8226370714:AAHyhzM0QuoYOPihLn_npm4KUc8BRSc7ItY"

app = ApplicationBuilder().token(TOKEN).build()
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("place_an_order", place_an_order)],
    states={
        GET_USER_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(CommandHandler("data", timer))
app.add_handler(CommandHandler("wb", wb_parser))
app.add_handler(CommandHandler("bin", binance_price))
app.add_handler(CommandHandler("cource", cbr_currency))
app.add_handler(CommandHandler("get_week", get_week))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(conv_handler)  # ПОСЛЕДНИЙ

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

app.run_polling()
