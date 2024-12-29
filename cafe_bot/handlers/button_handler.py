from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        # Отображаем категории меню
        keyboard = [
            [InlineKeyboardButton("Cafe", callback_data="category_cafe")],
            [InlineKeyboardButton("Cerveza", callback_data="category_cerveza")],
            [InlineKeyboardButton("Bocadillos", callback_data="category_bocadillos")],
            [InlineKeyboardButton("Comida", callback_data="category_comida")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Seleccione una categoría:", reply_markup=reply_markup)

    elif query.data.startswith("category_"):
        category = query.data.split("_")[1]
        await query.edit_message_text(f"Has seleccionado la categoría: {category}. Aquí están los productos...")

    elif query.data == "schedule":
        from handlers.schedule_handler import schedule
        await schedule(update, context)

    elif query.data == "book":
        from handlers.book_handler import start_booking
        await start_booking(update, context)

    elif query.data == "contacts":
        from handlers.contacts_handler import contacts
        await contacts(update, context)

    else:
        # Если callback_data не совпадает с ожидаемым
        await query.edit_message_text("Selección desconocida. Inténtalo de nuevo.")
