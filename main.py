import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from api_key import API_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    await message.answer(f"Привет, {user_name}! Я твой первый асинхронный бот.")
    logger.info(f"Пользователь {user_id} ({user_name}) запустил /start")


# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id

    await message.answer("Я умею:\n/start — поздороваться\n/help — показать это сообщение")
    logger.info(f"Пользователь {user_id} запросил /help")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())