import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from add_user import *
from keyboards import *
from db_utils import *
from api_key import API_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

include_create_new_user_func (dp, bot, logger)

# Обработчик команды /help
@dp.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id

    await message.answer("Я умею:\n/start — поздороваться\n/help — показать это сообщение")
    logger.info(f"Пользователь {user_id} запросил /help")

@dp.message(Command("about"))
async def about_command(message: Message):
    user_id = message.from_user.id

    await message.answer("Я бот, созданный на aiogram в марте 2026!")
    logger.info(f"Пользователь {user_id} запросил /about")

@dp.callback_query(lambda call: call.data == 'type_about_loyalty')
async def process_callback_type_new_user(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)  
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await bot.send_message(user_id, "Куча каких-то условий и правил")    
    logger.info(f"Пользователю {user_id} ({user_name}) отправлены условия программы лояльности")

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name   
    
    await message.answer(f"Привет, {user_name}! Добро пожаловать в программу лояльности Суши Мастер.",reply_markup=create_keyboard_for_new_user())   

    logger.info(f"Пользователь {user_id} ({user_name}) запустил /start")




# Обработчик любого присланного текста
@dp.message(F.text)
async def echo_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    await message.answer(f"Ты сказал: {text}")
    logger.info(f"Пользователь {user_id} отправил сообщение: {text}")        


async def main():
    logger.info("Создание базы данных")
    await create_db()
    logger.info("База данных создана")    
    logger.info("Бот запущен!")    
    await dp.start_polling(bot)   
    

if __name__ == "__main__":
    asyncio.run(main())