import asyncio
import logging
import sys
from io import BytesIO
import schedule
from datetime import datetime
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import CommandStart
from aiogram.types import ContentType

import openai
from PIL import Image

from config import token, key, user_id_to_send_report

# Telegram Bot Token и OpenAI API Key из файла конфигурации
TOKEN = token
OPENAI_API_KEY = key
USER_ID_TO_SEND_REPORT = user_id_to_send_report

# Инициализация бота
bot = Bot(token=TOKEN)
router = Router()
dp = Dispatcher()

# Установка API-ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Словарь для хранения текущих запросов пользователя
user_requests = {}
daily_logs = []

async def ask_gpt4(text):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        answer = response['choices'][0]['message']['content']
        print("GPT-4 Response:", answer)
        return answer
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I'm having trouble connecting to OpenAI right now."

@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Welcome! Send me any text and I will respond using GPT-4.")
    print("Start command received")

@router.message(F.content_type == ContentType.TEXT)
async def text_handler(message: types.Message):
    user_request = message.text
    user_requests[message.from_user.id] = user_request

    # Логирование запроса
    daily_logs.append(f"{datetime.now()} - User {message.from_user.id}: {user_request}")
    print("User request logged:", user_request)

    # Запрашиваем у GPT-4, что сделать с запросом пользователя
    answer = await ask_gpt4(user_request)
    try:
        await message.answer(answer)
        print("Text response sent to user")
    except TypeError:
        await message.answer("Nice try!")
        print("Failed to send text response")

@router.message(F.content_type == ContentType.PHOTO)
async def photo_handler(message: types.Message):
    photo = message.photo[-1]  # Получаем фото с наивысшим разрешением
    photo_bytes = await photo.download(destination=BytesIO())
    image = Image.open(photo_bytes)

    # Здесь можно добавить любую обработку изображения (например, отправить его в API для распознавания)
    # Пример: отправка изображения в OpenAI DALL-E или другой сервис

    # Пример логирования
    daily_logs.append(f"{datetime.now()} - User {message.from_user.id} sent a photo")

    await message.answer("Photo received and processed.")
    print("Photo received and processed")

async def send_daily_report():
    log_file = "daily_log.txt"
    with open(log_file, "w") as file:
        file.write("\n".join(daily_logs))
    print("Daily log written to file")

    with open(log_file, "rb") as file:
        await bot.send_document(USER_ID_TO_SEND_REPORT, file, caption="Daily log report")
    print("Daily report sent to user")

    daily_logs.clear()

def schedule_daily_report():
    schedule.every().day.at("23:59").do(lambda: asyncio.run(send_daily_report()))
    print("Scheduled daily report")

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main() -> None:
    dp.include_router(router)
    # Стартуем polling с указанием бота
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    schedule_daily_report()
    asyncio.run(main())
