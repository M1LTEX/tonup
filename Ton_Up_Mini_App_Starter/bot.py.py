import os, asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

load_dotenv()
TOKEN=os.getenv("BOT_TOKEN","").strip()
URL=os.getenv("WEBAPP_URL","").strip()

async def main():
    if not TOKEN: raise RuntimeError("Заповни BOT_TOKEN у .env")
    if not URL.startswith("https://"): raise RuntimeError("WEBAPP_URL має бути HTTPS")
    bot=Bot(TOKEN); dp=Dispatcher()
    @dp.message(CommandStart())
    async def start(m: Message):
        kb=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Відкрити Ton Up 🎁",web_app=WebAppInfo(url=URL))]],resize_keyboard=True)
        await m.answer("Ласкаво просимо до Ton Up! Це демо з віртуальними монетами.",reply_markup=kb)
    @dp.message(lambda m: m.text == "/id")
    async def uid(m: Message): await m.answer(f"Твій Telegram ID: {m.from_user.id}")
    await dp.start_polling(bot)
if __name__=="__main__": asyncio.run(main())
