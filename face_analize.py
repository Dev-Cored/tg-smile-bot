from deepface import DeepFace
import numpy as np
import cv2
import aiohttp
import asyncio

async def get_emoji(selfie_id):
    from bot import TOKEN
    async with aiohttp.ClientSession() as session:
        # Получаем file_path по file_id
        async with session.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={selfie_id}") as resp:
            if resp.status != 200:
                print("Не удалось получить путь файла")
                return None
            data = await resp.json()
            file_path = data['result']['file_path']

        # Качаем файл
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        async with session.get(file_url) as resp:
            selfie_bytes = await resp.read()
            if len(selfie_bytes) < 1000:
                print(f"⚠️ Короткий файл: {len(selfie_bytes)} байт.")
                return None


        np_arr = np.frombuffer(selfie_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        print(f"Длина байтов изображения: {len(selfie_bytes)}")
        if img is None:
            print("⚠️ Не удалось декодировать изображение из байтов.")
            return None
        analyse = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        emotion = analyse[0]['dominant_emotion']
        print(analyse)
        print(emotion)
        return emotion, selfie_bytes

async def get_imoji_from_bites(selfie_bytes):
    np_arr = np.frombuffer(selfie_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    print(f"Длина байтов изображения: {len(selfie_bytes)}")
    if img is None:
        print("⚠️ Не удалось декодировать изображение из байтов.")
        return None
    analyse = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
    emotion = analyse[0]['dominant_emotion']
    print(analyse)
    print(emotion)
    return emotion

