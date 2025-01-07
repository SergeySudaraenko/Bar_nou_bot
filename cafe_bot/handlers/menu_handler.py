import json
import logging
import httpx  # Для асинхронных запросов
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL для JSON файлов
URLS = {
    "menu": "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/menu.json",
    "category_1": "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/category_1.json",
    "category_2": "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/category_2.json",
    "category_3": "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/category_3.json",
    "category_4": "https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/category_4.json"
}

# Функция для асинхронной загрузки данных из URL
async def load_json_from_url(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Проверка на успешный ответ
            return response.json()  # Возвращаем данные в формате JSON
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных с {url}: {e}")
        return {}

async def show_menu(update: Update, context: CallbackContext):
    """Показывает кнопки с категориями."""
    query = update.callback_query
    await query.answer()

    # Загружаем меню
    menu_data = await load_json_from_url(URLS["menu"])

    if not menu_data:
        await query.edit_message_text("Ошибка загрузки меню.")
        return

    keyboard = [
        [InlineKeyboardButton("Café", callback_data="category_cafe")],
        [InlineKeyboardButton("Cerveza", callback_data="category_cerveza")],
        [InlineKeyboardButton("Bocadillos", callback_data="category_bocadillos")],
        [InlineKeyboardButton("Comida", callback_data="category_comida")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Selecciona una categoría:", reply_markup=reply_markup)

async def handle_category(update: Update, context: CallbackContext):
    """Показывает товары для выбранной категории с кнопками."""
    query = update.callback_query
    await query.answer()

    # Связываем callback_data с URL
    category_urls = {
        "category_cafe": URLS["category_1"],
        "category_cerveza": URLS["category_2"],
        "category_bocadillos": URLS["category_3"],
        "category_comida": URLS["category_4"],
    }

    # Получаем URL для выбранной категории
    url = category_urls.get(query.data)
    if not url:
        await query.edit_message_text("Categoría no encontrada. Inténtalo de nuevo.")
        return

    # Загружаем товары для категории
    items = await load_json_from_url(url)
    if not items:
        await query.edit_message_text("No hay productos disponibles en esta categoría.")
        return

    # Формируем кнопки для продуктов
    keyboard = [
        [InlineKeyboardButton(f"⭐ {item['name']}", callback_data=f"item_{item['id']}")]
        for item in items
    ]
    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("Volver a categorías", callback_data="show_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Selecciona un producto:", reply_markup=reply_markup)

async def handle_product(update: Update, context: CallbackContext):
    """Отправляет фотографию и описание выбранного продукта."""
    query = update.callback_query
    await query.answer()

    # Получаем ID товара из callback_data
    product_id = query.data.split("_")[1]

    # Загружаем все категории, чтобы найти товар по ID
    all_categories_urls = [
        URLS["category_1"],
        URLS["category_2"],
        URLS["category_3"],
        URLS["category_4"],
    ]

    product = None
    for url in all_categories_urls:
        items = await load_json_from_url(url)
        for item in items:
            if item["id"] == int(product_id):
                product = item
                break
        if product:
            break

    if not product:
        await query.edit_message_text("Producto no encontrado. Inténtalo de nuevo.")
        return

    # Отправляем фотографию и описание
    image_url = f"https://raw.githubusercontent.com/SergeySudaraenko/Bar_nou_bot/main/cafe_bot/data/images/{product['image']}"
    try:
        await query.message.reply_photo(
            photo=image_url,
            caption=f"⭐ {product['name']} - {product['price']}€\n\n{product['description']}"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await query.message.reply_text(
            f"⭐ {product['name']} - {product['price']}€\n\n{product['description']}\n\n(Imagen no disponible)"
        )
