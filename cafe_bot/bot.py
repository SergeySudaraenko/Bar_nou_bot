from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, filters, MessageHandler
from constants import ENTER_NAME, ENTER_PHONE, SELECT_DATE, SELECT_TIME
from handlers.start_handler import start
from handlers.schedule_handler import schedule
from handlers.menu_handler import show_menu, handle_category, handle_product
from handlers.book_handler import handle_date, handle_time, handle_name, handle_phone, start_booking
from handlers.button_handler import button_handler
from handlers.contacts_handler import contacts  
from config import TOKEN

# Настройка логирования
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Запуск бота...")

    # Создание приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("contacts", contacts))  # Обработчик для команды /contacts

    # Обработчики меню и категорий
    app.add_handler(CallbackQueryHandler(show_menu, pattern="^show_menu$"))
    app.add_handler(CallbackQueryHandler(handle_category, pattern="^category_.*$"))

    # Обработчик продуктов (показ фотографий)
    app.add_handler(CallbackQueryHandler(handle_product, pattern="^item_\\d+$"))

    # Обработчик бронирования
    booking_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_booking, pattern="^book$")],
        states={
            SELECT_DATE: [CallbackQueryHandler(handle_date, pattern="^day_\\d{4}-\\d{2}-\\d{2}$")],
            SELECT_TIME: [CallbackQueryHandler(handle_time, pattern="^time_\\d{2}:\\d{2}-\\d{2}:\\d{2}$")],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
        },
        fallbacks=[CommandHandler("cancel", start), CommandHandler("menu", show_menu)],
    )
    app.add_handler(booking_handler)

    # Глобальный обработчик кнопок
    app.add_handler(CallbackQueryHandler(button_handler))

    # Запуск бота
    app.run_polling()
