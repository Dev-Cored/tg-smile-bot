from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def decline():
    kb = [
        [
            types.KeyboardButton(text="🚫Отмена❌", )
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def inline_bot_link():
    btn = [
        [
            types.InlineKeyboardButton(text='Перейти к боту', url='https://t.me/dev_core_officlal_smile_bot')
        ]
    ]
    button = types.InlineKeyboardMarkup(
        inline_keyboard=btn
    )
    return button