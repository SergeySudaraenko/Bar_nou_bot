import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import os

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к папке с изображениями
IMAGE_PATH = "data/images/"  # Путь к папке с изображениями, возможно нужно изменить путь, если изображения в другой папке

# Загружаем товары для категории
def load_category_items(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла {file_path}: {e}")
        return []

async def show_menu(update: Update, context: CallbackContext):
    """Показывает кнопки с категориями."""
    query = update.callback_query
    await query.answer()
    
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
    
    # Связываем callback_data с файлами
    category_files = {
        "category_cafe": "data/category_1.json",
        "category_cerveza": "data/category_2.json",
        "category_bocadillos": "data/category_3.json",
        "category_comida": "data/category_4.json",
    }

    # Проверяем, существует ли файл для выбранной категории
    file_path = category_files.get(query.data)
    if not file_path:
        await query.edit_message_text("Categoría no encontrada. Inténtalo de nuevo.")
        return

    # Загружаем данные из файла
    items = load_category_items(file_path)
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
    all_categories = [
        "data/category_1.json",
        "data/category_2.json",
        "data/category_3.json",
        "data/category_4.json",
    ]

    product = None
    for category_file in all_categories:
        items = load_category_items(category_file)
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
    image_path = os.path.join(IMAGE_PATH, product['image'])
    logger.info(f"Пытаемся загрузить изображение: {image_path}")  # Логируем путь к изображению

    try:
        if os.path.exists(image_path):  # Проверка существования файла
            with open(image_path, "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=f"⭐ {product['name']} - {product['price']}€\n\n{product['description']}"
                )
        else:
            logger.error(f"Изображение не найдено: {image_path}")
            await query.message.reply_text(
                f"⭐ {product['name']} - {product['price']}€\n\n{product['description']}\n\n(Imagen no disponible)"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await query.message.reply_text(
            f"⭐ {product['name']} - {product['price']}€\n\n{product['description']}\n\n(Imagen no disponible)"
        )
