#Импорт библиотек
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
import os
import logging
import datetime as dt

#Импорт зависимостей
from db import init_db
from scheduler import start_scheduler, scheduled_job_first, evening_photo_job

#Импорт роутеров
from handlers.registration import router_registration
from handlers.recognise_emoji import router_emoji

#Получение токена из файла настроек
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Объявление бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

#Функция активации
async def main():
    # Настройка логирования
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Запуск базы данных
    init_db()

    start_scheduler()

    dp.include_routers(router_registration, router_emoji)
    await dp.start_polling(bot)

#Запуск
if __name__ == '__main__':
    asyncio.run(main())