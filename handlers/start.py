from aiogram import Router, types
from aiogram.filters import *
import texts

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(texts.cmd_start)


