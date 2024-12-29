import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Получение токена из переменной окружения
TOKEN = os.getenv("TOKEN")

# Проверка на наличие токена
if not TOKEN:
    raise ValueError("Переменная окружения TOKEN не найдена. Проверьте файл .env.")

