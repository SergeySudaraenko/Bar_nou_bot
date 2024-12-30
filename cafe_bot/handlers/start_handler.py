from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import os

async def start(update: Update, context: CallbackContext):
    # Клавиатура с кнопками
    keyboard = [
        [InlineKeyboardButton("Ver el menú", callback_data="menu")],
        [InlineKeyboardButton("Reservar una mesa", callback_data="book")],
        [InlineKeyboardButton("Ver horario de trabajo", callback_data="schedule")],
        [InlineKeyboardButton("Dirección y contactos", callback_data="contacts")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка логотипа
    
    file_path = os.path.join("data", "images", "Logo2.png")
    await update.message.reply_photo(photo=open(file_path, "rb"))

    # Отправка приветственного сообщения с клавиатурой
    await update.message.reply_text(
        "¡Bienvenido a Bar Nou! Elija una acción:\n",
        reply_markup=reply_markup
    )

