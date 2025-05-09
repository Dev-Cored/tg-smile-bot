#Импорт библиотек
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.types import ChatMemberUpdated, Chat

#Импорт зависимостей
from db import get_session, User, Photo, SentMathce, Group
from generators import generators as gen

#Объявление роутера
router_registration = Router()

#Функции
async def check_chat_type_is_private(chat_type):
    if chat_type == "private":
        return True
    elif chat_type in ("group", "supergroup"):
        return False
    else:
        print(f"Тип чата: {chat_type}")

async def get_chat_name(chat_id):
    from bot import bot
    chat = await bot.get_chat(chat_id)
    chat_title = chat.title
    return chat_title


#Обработка добавления бота в группу
@router_registration.my_chat_member(F.new_chat_member.status.in_({"member", "administrator"}))
async def on_bot_added(event: ChatMemberUpdated):
    if event.old_chat_member.status in {"kicked", "left"}:
        group_id = event.chat.id
        from bot import bot
        await bot.send_message(
            chat_id=group_id,
            text="👋 Привет! Я Smile Bot! Помогу вашему коллективу контролировать эмоции! Чтобы присоединиться к программе в рамках этого чата, необходимо выполнить команду /join в этом чате."
        )
        session = get_session()
        session.add(Group(group_id=group_id, today_emoji=gen.random_emotion()))
        session.commit()

#Обработка выхода участника из чата и программы
@router_registration.chat_member()
async def on_user_leave(message: ChatMemberUpdated):
    if message.new_chat_member.status == "left":
        user_id = message.new_chat_member.user.id
        user_name = message.new_chat_member.user.name
        chat_id = message.chat.id
        session = get_session()

        user = session.query(User).filter(User.user_id == user_id).first()
        if user is not None:
            if user.group_id is not None:
                user.group_id = None
                from bot import bot
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"‼️ Пользователь {user_name} покинул чат и программу."
                )
        session.commit()

#Обработка команды старт
@router_registration.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    chat_type = message.chat.type
    chat_id = message.chat.id
    session = get_session()

    is_private = await check_chat_type_is_private(chat_type)
    if is_private:

        user = session.query(User).filter(User.user_id == user_id).first()

        if user is None:
            await message.answer("Воспользуйтесь командой /join в групповом чате, чтобы присоединиться к программе в рамках этого чата.")
        else:
            user = session.query(User).filter(User.group_id == user.group_id).first()
            user_group = user.group_id
            if user_group is None:
                await message.answer("Вы не еще не присоединились ни к одной группе! Воспользуйтесь командой /join в групповом чате, чтобы присоединиться к программе в рамках этого чата.")
            else:
                group = session.query(Group).filter(Group.group_id == user_group).first()
                await message.answer(f"Эмоция вашей группы: {gen.emote_to_text(group.today_emoji)}")
    else:
        group = session.query(Group).filter(Group.group_id == chat_id).first()
        if group is not None:
            await message.reply("Чтобы присоединиться к программе в рамках этого чата, необходимо выполнить команду /join в этом чате.")

@router_registration.message(Command('join'))
async def join(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user_fullname = message.from_user.full_name
    chat_type = message.chat.type
    chat_id = message.chat.id
    session = get_session()

    is_private = await check_chat_type_is_private(chat_type)
    if is_private:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            await message.answer("Вы еще не присоединились ни к одной группе! Воспользуйтесь командой /join в чате, чтобы участвовать в программе в рамках этого чата.")
        else:
            group = user.group_id
            if group is None:
                await message.answer("Вы еще не присоединились ни к одной группе! Воспользуйтесь командой /join в чате, чтобы участвовать в программе в рамках этого чата.")
            else:
                chat_title = await get_chat_name(chat_id)
                chat_emote = session.query(Group).filter(Group.group_id == group).first()
                user.group_id = chat_id
                await message.answer(f"""
Вы уже присоединились к программе в рамках группы <b>{chat_title}</b>!
Сегодняшняя эмоция <b>{chat_emote}</b>.
""", parse_mode=ParseMode.HTML)

    else:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            session.add(User(user_id=user_id, username=username, user_fullname=user_fullname, group_id=chat_id))
            await message.reply(f"Вы присоединяетесь к программе в рамках чата {await get_chat_name(chat_id)}.")
        else:
            if user.group_id is None:
                user.group_id = chat_id
                await message.reply(f"Вы присоединяетесь к программе в рамках чата {await get_chat_name(chat_id)}.")
            else:
                if user.group_id != chat_id:
                    await message.reply(f"Вы уже присоединились к программе в рамках {await get_chat_name(chat_id)}. Чтобы покинуть программу, покиньте тот чат.")
                elif user.group_id == chat_id:
                    group = session.query(Group).filter(Group.group_id == user.group_id).first()
                    await message.reply(f"Вы уже присоединились к программе в рамках этой группы. Текущая эмоция: {group.today_emoji}")
    session.commit()



