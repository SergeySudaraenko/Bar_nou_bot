from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# Состояния для ConversationHandler
SELECT_DATE, SELECT_TIME, ENTER_NAME, ENTER_PHONE = range(4)

# Загружаем переменные из .env файла
load_dotenv()

# Telegram bot token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Ваш личный Chat ID для получения уведомлений

# Список месяцев на испанском
SPANISH_MONTHS = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
]

# Функция для отправки сообщения через Telegram
def send_to_telegram(message):
    """Отправка сообщения от имени Bar_Nou_Bot в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,  # ID чата, куда будут приходить сообщения
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Сообщение успешно отправлено в Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")


async def start_booking(update: Update, context: CallbackContext):
    """Начало бронирования. Показываем календарь на следующие 30 дней."""
    query = update.callback_query
    await query.answer()

    now = datetime.now()

    # Генерация календаря на 30 дней
    keyboard = []
    for i in range(0, 30, 5):  # Построчно по 5 дней (удобнее для мобильных)
        row = []
        for j in range(5):
            date = now + timedelta(days=i + j)
            if i + j < 30:
                day = date.day
                month = SPANISH_MONTHS[date.month - 1]  # Название месяца на испанском
                row.append(InlineKeyboardButton(
                    f"{day} {month}",  # Число и месяц
                    callback_data=f"day_{date.strftime('%Y-%m-%d')}"
                ))
        keyboard.append(row)

    # Кнопка "Cancelar"
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "Seleccione una fecha para la reserva:",
        reply_markup=reply_markup
    )
    return SELECT_DATE


async def handle_date(update: Update, context: CallbackContext):
    """Обработка выбора даты из календаря."""
    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice == "cancel":
        await query.edit_message_text("Reserva cancelada.")
        return ConversationHandler.END

    if choice.startswith("day_"):
        selected_date_str = choice.split("_")[1]
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")

        context.user_data["date"] = selected_date

        # Создаем кнопки для выбора времени
        keyboard = []
        for i in range(8, 24, 2):  # Интервалы времени с 8 до 24 часов, каждые 2 часа
            start_time = f"{i:02d}:00"
            end_time = f"{i+2:02d}:00"
            keyboard.append([
                InlineKeyboardButton(
                    f"{start_time} - {end_time}",
                    callback_data=f"time_{start_time}-{end_time}"
                )
            ])

        # Кнопка "Cancelar"
        keyboard.append([InlineKeyboardButton("Cancelar", callback_data="cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Seleccione un intervalo de tiempo:",
            reply_markup=reply_markup
        )
        return SELECT_TIME

    await query.edit_message_text("Selección incorrecta. Por favor, inténtalo nuevamente.")
    return SELECT_DATE


async def handle_time(update: Update, context: CallbackContext):
    """Обработка выбора времени."""
    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice == "cancel":
        await query.edit_message_text("Reserva cancelada.")
        return ConversationHandler.END

    if choice.startswith("time_"):
        selected_time_range = choice.split("_")[1]
        context.user_data["time"] = selected_time_range

        await query.edit_message_text(
            f"Seleccionaste el intervalo: {selected_time_range}. Por favor, ingresa tu nombre:"
        )
        return ENTER_NAME

    await query.edit_message_text("Selección incorrecta. Por favor, inténtalo nuevamente.")
    return SELECT_TIME


async def handle_name(update: Update, context: CallbackContext):
    """Обработка ввода имени."""
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("El nombre es demasiado corto. Por favor, ingresa un nombre válido:")
        return ENTER_NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        f"Ingresaste el nombre: {name}. Por favor, ingresa tu número de teléfono móvil (Solo números):"
    )
    return ENTER_PHONE


async def handle_phone(update: Update, context: CallbackContext):
    """Обработка ввода номера телефона."""
    phone = update.message.text.strip()

    if phone.isdigit() and len(phone) >= 8:
        context.user_data["phone"] = phone

        # Формируем сообщение для Telegram
        message = f"""
        🆕 *Nueva reserva de cliente:*

        📛 *Nombre:* {context.user_data['name']}
        📅 *Fecha:* {context.user_data['date'].strftime('%d %b %Y')}
        🕒 *Hora:* {context.user_data['time']}
        📞 *Teléfono:* {phone}
        """
        send_to_telegram(message)

        await update.message.reply_text(
            f"¡Reserva completada con éxito! Espere la llamada del administrador.\n"
            f"Nombre: {context.user_data['name']}\n"
            f"Fecha: {context.user_data['date'].strftime('%d %b %Y')}\n"
            f"Hora: {context.user_data['time']}\n"
            f"Teléfono: {context.user_data['phone']}"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Formato de teléfono incorrecto. Por favor, ingresa solo números (al menos 8 dígitos):"
    )
    return ENTER_PHONE


async def cancel_booking(update: Update, context: CallbackContext):
    """Обработка отмены бронирования."""
    await update.message.reply_text("Reserva cancelada.")
    return ConversationHandler.END
