import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import docker
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Docker клиента
docker_client = docker.from_env()

# Список разрешенных пользователей (можно добавить через переменные окружения)
ALLOWED_USERS = [int(user_id) for user_id in os.getenv('ALLOWED_USERS', '').split(',') if user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return
    
    await update.message.reply_text(
        "Привет! Я бот для управления Docker контейнерами.\n"
        "Доступные команды:\n"
        "/list - Показать список контейнеров\n"
        "/start_container <container_id> - Запустить контейнер\n"
        "/stop_container <container_id> - Остановить контейнер\n"
        "/restart_container <container_id> - Перезапустить контейнер"
    )

async def list_containers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список всех контейнеров"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    try:
        containers = docker_client.containers.list(all=True)
        if not containers:
            await update.message.reply_text("Нет запущенных контейнеров.")
            return

        message = "Список контейнеров:\n\n"
        for container in containers:
            status = "🟢" if container.status == "running" else "🔴"
            message += f"{status} ID: {container.short_id}\n"
            message += f"Имя: {container.name}\n"
            message += f"Статус: {container.status}\n"
            message += "-------------------\n"

        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка при получении списка контейнеров: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка контейнеров.")

async def start_container(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запустить контейнер"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите ID контейнера.")
        return

    container_id = context.args[0]
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        await update.message.reply_text(f"Контейнер {container_id} успешно запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске контейнера: {e}")
        await update.message.reply_text("Произошла ошибка при запуске контейнера.")

async def stop_container(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановить контейнер"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите ID контейнера.")
        return

    container_id = context.args[0]
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        await update.message.reply_text(f"Контейнер {container_id} успешно остановлен.")
    except Exception as e:
        logger.error(f"Ошибка при остановке контейнера: {e}")
        await update.message.reply_text("Произошла ошибка при остановке контейнера.")

async def restart_container(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезапустить контейнер"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите ID контейнера.")
        return

    container_id = context.args[0]
    try:
        container = docker_client.containers.get(container_id)
        container.restart()
        await update.message.reply_text(f"Контейнер {container_id} успешно перезапущен.")
    except Exception as e:
        logger.error(f"Ошибка при перезапуске контейнера: {e}")
        await update.message.reply_text("Произошла ошибка при перезапуске контейнера.")

def main():
    """Основная функция запуска бота"""
    # Получение токена из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("Не указан токен бота в переменных окружения!")
        return

    # Создание приложения
    application = Application.builder().token(token).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_containers))
    application.add_handler(CommandHandler("start_container", start_container))
    application.add_handler(CommandHandler("stop_container", stop_container))
    application.add_handler(CommandHandler("restart_container", restart_container))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main() 