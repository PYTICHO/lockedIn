import os, asyncio, logging
from aiogram import Bot, Dispatcher, html, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import start
from aiogram.types import *
from dotenv import load_dotenv
import texts
from os import getenv
from db import init_db, save_post, approvedPost, rejectedPost
load_dotenv()

# Enter data
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

ADMINS = [int(x.strip()) for x in os.getenv("ADMINS_IDS", "").split(",") if x.strip()]
CHANNEL_ID = os.getenv("CHANNEL_ID")


# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

# Подключаем обработчики
dp.include_router(start.router)


# Ловим обычный текст
@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.reply(texts.incorrectMessageFormat)


# Отправка на модеризацию к админам
@dp.message(F.photo)
async def sendProgress(message: types.Message):
    caption = message.caption
    if not caption:
        await message.reply(texts.incorrectMessageFormat)
        return
    photo_id = message.photo[-1].file_id
    user_id = message.from_user.id
    user_message_id = message.message_id 

    post_id = await save_post(user_id=user_id, photo_id=photo_id, caption=caption, user_message_id=user_message_id)

    # Кнопки для модерации
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{post_id}"),
         InlineKeyboardButton(text="⛔️ Отклонить", callback_data=f"reject_{post_id}")]
    ])

    # Отправляем всем админам
    for admin_id in ADMINS:
        await bot.send_photo(
            admin_id,
            photo=photo_id,
            caption=caption,
            reply_markup=markup
        )

    await message.reply("✅ Сообщение сохранено и отправлено на модерацию.")

# Обработка постов прошедших модерацию
@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: CallbackQuery):
    #Получаем id поста, сохраненный в БД(id)
    post_id = int(callback.data.split("_")[1])
    # Подключаемся к БД
    post = await approvedPost(post_id=post_id)

    user_id = post["user_id"]
    user_message_id = post["user_message_id"]
    photo_id = post["photo_id"]
    caption = post["caption"]
    # Отправляем в канал
    await bot.send_photo(
        CHANNEL_ID,
        photo=photo_id,
        caption=caption
    )
    
    await callback.message.edit_caption(
            f"✅ Пост одобрен админом",
            reply_markup=None
    )
    
    if post["user_id"] and post["user_message_id"]:
        await bot.send_message(
            user_id,
            "✅ Ваш пост был одобрен модератором",
            reply_to_message_id=user_message_id
        )


@dp.callback_query(F.data.startswith("reject_"))
async def reject_post(callback: CallbackQuery):
    post_id = int(callback.data.split("_")[1])
    post = await rejectedPost(post_id=post_id)

    user_id = post["user_id"]
    user_message_id = post["user_message_id"]
    
    await callback.message.edit_caption(
        reply_markup=None
    )
    await callback.message.reply(f"⛔️ Пост отклонён админом")

    if post["user_id"] and post["user_message_id"]:
        await bot.send_message(
            user_id,
            "❌ Ваш пост был отклонён модератором",
            reply_to_message_id=user_message_id
        )




# Инициализация и запуск
async def main() -> None:
    global pool
    await init_db()
    await dp.start_polling(bot)


if __name__=="__main__":
    logging.info("Бот запущен ✅")
    print("Бот запущен ✅")

    asyncio.run(main())

