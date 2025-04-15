#Импорт библиотек
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

#Импорт зависимостей
import db


router_registration = Router()

@router_registration.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id


