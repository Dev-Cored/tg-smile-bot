#Импорт библиотек
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
import os
import logging

#Импорт зависимостей
import db

#Получение токена из файла настроек
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#Запуск базы данных


#Объявление бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

#Функция активации
async def main():
    dp.include_routers()

    await dp.start_polling(bot)

#Запуск
if __name__ == '__main__':
    asyncio.run(main())