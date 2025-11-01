import os, asyncio, logging
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import start
from dotenv import load_dotenv
import texts
from os import getenv
load_dotenv()

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

# Enter data
BOT_TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()

# Подключаем обработчики
dp.include_router(start.router)



# Код







# Инициализация и запуск
async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__=="__main__":
    logging.info("Бот запущен ✅")
    print("Бот запущен ✅")

    asyncio.run(main())

