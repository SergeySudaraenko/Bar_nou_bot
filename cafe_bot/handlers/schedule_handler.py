import json
import httpx  # Используем httpx для асинхронных запросов
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

async def schedule(update: Update, context: CallbackContext):
    try:
        # Загрузка данных из URL
        url = "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/schedule.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Проверяем, что запрос выполнен успешно
            schedule_data = response.json()  # Преобразуем JSON-ответ в словарь

        # Формирование текста с графиком
        schedule_text = "Horario de trabajo:\n"
        for day, hours_list in schedule_data.items():
            schedule_text += f"{day}:\n"
            for hours in hours_list:
                schedule_text += f"  {hours}\n"

        # Добавление кнопок
        keyboard = [
            [InlineKeyboardButton("Ver el menú", callback_data="menu")],
            [InlineKeyboardButton("Dirección y contactos", callback_data="contacts")],
            [InlineKeyboardButton("Reservar una mesa", callback_data="book")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Проверяем, если запрос пришел через callback_query или через сообщение
        if update.callback_query:
            # Если это callback запрос (например, на кнопке), редактируем сообщение
            await update.callback_query.edit_message_text(schedule_text, reply_markup=reply_markup)
        else:
            # Если это обычное сообщение (например, через команду /schedule), отправляем новое сообщение
            await update.message.reply_text(schedule_text, reply_markup=reply_markup)

    except Exception as e:
        # В случае ошибки, отправляем сообщение об ошибке
        error_text = "Error al cargar el horario de trabajo."
        keyboard = [
            [InlineKeyboardButton("Volver al menú principal", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(error_text, reply_markup=reply_markup)
        print(f"Error: {e}")
