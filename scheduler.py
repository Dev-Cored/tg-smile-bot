#Импорт библиотек
from aiogram.types import InputMediaPhoto
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import random
import json

#Импорт зависимостей
from db import get_session, get_acync_session, Group, User, Photo, SentMathce
import generators.generators as gen
from handlers.registration import get_chat_name

#Новая случайная эмоция и сброс счетчика отправленных селфи
async def update_today_emoji_and_sent_counter(session: AsyncSession):
    groups_result = await session.execute(select(Group))
    groups = groups_result.scalars().all()

    users_result = await session.execute(select(User))
    users = users_result.scalars().all()

    for group in groups:
        group.today_emoji = gen.random_emotion()

    for user in users:
        user.daily_photo_sent = 0

    await session.commit()

async def scheduled_job_first():
    session = await get_acync_session()
    async with session as session:
        await update_today_emoji_and_sent_counter(session)


#Отправка альбома из накопленных селфи за день в 7 вечера
async def evening_photo_job():
    session = await get_acync_session()
    async with session as session:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        groups = (await session.execute(select(Group))).scalars().all()

        for group in groups:
            emotion = group.today_emoji
            user_ids_result = await session.execute(
                select(User.user_id).where(User.group_id == group.group_id)
            )
            user_ids = [row[0] for row in user_ids_result.all()]
            if not user_ids:
                continue
            photos_result = await session.execute(
                select(Photo).where(
                    Photo.sender_id.in_(user_ids),
                    Photo.emotion == emotion,
                    Photo.date >= today_start
                )
            )
            photos = photos_result.scalars().all()
            selected_photos = random.sample(photos, min(len(photos), 10))

            print(f"Group {await get_chat_name(group.group_id)}, emotion: {emotion}, found photos: {[p.file_id for p in photos]}")

            if len(selected_photos) < 2:
                print(f"Недостаточно фото для группы {await get_chat_name(group.group_id)} — найдено: {len(selected_photos)}")
                for user_id in user_ids:
                    try:
                        from bot import bot
                        await bot.send_message(chat_id=user_id, text="К сожалению, сегодня не было получено достаточно фотографий для альбома.")
                    except Exception as e:
                        print(f"Ошибка при отправке пользователю {user_id}: {e}")
                continue
            media = [InputMediaPhoto(media=photo.file_id) for photo in selected_photos]
            photo_ids = [photo.id for photo in selected_photos]

            recipients_success = []

            for user_id in user_ids:
                try:
                    from bot import bot
                    await bot.send_message(chat_id=user_id, text=f"📸 Случайные фото с эмоцией {emotion} из вашей группы за сегодня:")
                    await bot.send_media_group(chat_id=user_id, media=media)
                    recipients_success.append(user_id)
                except Exception as e:
                    print(f"Ошибка при отправке пользователю {user_id}: {e}")

            if recipients_success:
                album_log = SentMathce(
                    group_id=group.id,
                    photos_ids=json.dumps(photo_ids),
                    recipients_ids=json.dumps(recipients_success),
                    date=datetime.now()
                )
                session.add(album_log)

        await session.commit()



#Функция запуска
def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_job_first, "cron", hour=8, minute=0)  # каждый день в 08:00
    scheduler.add_job(evening_photo_job, "cron", hour=19, minute=0) # каждый день в 19:00
    scheduler.start()