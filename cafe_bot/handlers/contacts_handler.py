import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

async def contacts(update: Update, context: CallbackContext):
    try:
        # Чтение данных из файла contactos.json
        with open("data/contactos.json", "r", encoding="utf-8") as file:
            contactos_data = json.load(file)

        # Формирование текста с контактами
        contacts_text = "Dirección y contactos:\n"
        for key, value in contactos_data.items():
            contacts_text += f"{key}: {value}\n"

        # Добавление кнопок
        keyboard = [
            [InlineKeyboardButton("Ver el menú", callback_data="menu")],
            [InlineKeyboardButton("Horario de trabajo", callback_data="schedule")],
            [InlineKeyboardButton("Reservar una mesa", callback_data="book")]
        ]
    
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Проверяем, если запрос пришел через callback_query или через сообщение
        if update.callback_query:
            # Если это callback запрос (например, на кнопке), редактируем сообщение
            await update.callback_query.edit_message_text(contacts_text, reply_markup=reply_markup)
        else:
            # Если это обычное сообщение (например, через команду /contacts), отправляем новое сообщение
            await update.message.reply_text(contacts_text, reply_markup=reply_markup)

    except Exception as e:
        # В случае ошибки, отправляем сообщение об ошибке
        error_text = "Error al cargar la información de contacto."
        keyboard = [
            [InlineKeyboardButton("Volver al menú principal", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(error_text, reply_markup=reply_markup)
        print(f"Error: {e}")
