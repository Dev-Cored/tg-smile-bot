#Импорт библиотек
import aiohttp
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.types import ChatMemberUpdated, Chat
from deepface import DeepFace
import datetime

#Импорт зависимостей
from db import get_session, User, Photo, SentMathce, Group
from generators import generators as gen
from .registration import check_chat_type_is_private, get_chat_name
import generators.kbs as kb
import face_analize as fa

#Объявление роутера
router_emoji = Router()

#Статусы
class Emoji(StatesGroup):
    waiting_for_selfie = State()
#Команда для отправки эмодзи
@router_emoji.message(Command("emoji"))
async def emoji(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    chat_type = message.chat.type
    session = get_session()

    is_private = await check_chat_type_is_private(chat_type)
    if is_private:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is not None:
            user_group = session.query(Group).filter(Group.group_id == user.group_id).first()
            if user_group is not None:
                await message.answer(f"Сегодня для группы {await get_chat_name(user_group.group_id)} установлена эмоция {user_group.today_emoji}")
                await message.answer(f"Отправь свое селфи для зачета!")
                await state.set_state(Emoji.waiting_for_selfie)
            else:
                await message.answer("Вы не еще не присоединились ни к одной группе! Воспользуйтесь командой /join в групповом чате, чтобы присоединиться к программе в рамках этого чата.")
        else:
            await message.answer("Вы не еще не присоединились ни к одной группе! Воспользуйтесь командой /join в групповом чате, чтобы присоединиться к программе в рамках этого чата.")
    else:
        group = session.query(Group).filter(Group.group_id == chat_id).first()
        await message.reply(f"Установленная эмоция в этом чате: {group.today_emoji}. Отправьте свою эмоцию в личные сообщения бота!", reply_markup=kb.inline_bot_link())

@router_emoji.message(Emoji.waiting_for_selfie, F.photo)
async def selfie(message: types.Message, state: FSMContext):
    selfie_id = message.photo[-1].file_id
    user_id = message.from_user.id
    session = get_session()

    photo = session.query(Photo).filter(Photo.file_id == selfie_id).first()
    if photo is None:

        analyse, file_bytes = await fa.get_emoji(selfie_id)
        await message.answer(f"Эмоция на фото: {gen.emote_to_text(analyse)}")
        user = session.query(User).filter(User.user_id == user_id).first()
        user_group_id = user.group_id
        group = session.query(Group).filter(Group.group_id == user_group_id).first()
        group_emotion = group.today_emoji
        if analyse != group_emotion:
            await message.answer(f"Эмоция на вашем селфи не соответствует заданной на сегодня! Заданная на сегодня эмоция: {gen.emote_to_text(group_emotion)}\nОтправьте селфи еще раз!")
        else:
            if user.daily_photo_sent <= 4:
                user.daily_photo_sent += 1
                await message.answer(f"Зачет! Сегодня вы выполнили задание на эмоцию! Ожидайте новое задание завтра. Вы можете отправить еще {5 - user.daily_photo_sent}")
                session.add(Photo(sender_id=user_id, file_id=selfie_id, file=file_bytes, emotion=analyse, date=datetime.datetime.now()))
                session.commit()
                await state.clear()
            elif user.daily_photo_sent > 4:
                await message.answer(f"Вы уже отправили максимально допустимое кол-во эмоций! Дождитесь завтра, чтобы получить новое задание на эмоцию.")
    else:
        await message.answer("Нельзя отправлять одно и то же фото несколько раз. Отправьте селфи повторно:")
## Тута дописать распознавание лиц и скачку байтов
## Сделать добавление в базу данных
