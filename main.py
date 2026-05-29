import asyncio
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram import types
from aiogram.types import InputFile, Message
from aiogram.filters.command import *
from dotenv import load_dotenv
from keyboards import *
from db_utils import *
from main_keyboard_click import *
from messages import ADRESS_TEXT, LOYATLY_TEXT, WELCOME_TEXT, WELCOME_TEXT_FOR_PROMO
from registration_router import *
from aiogram.fsm.storage.memory import MemoryStorage
from registration_router import registration_router
from aiohttp import web
from backup import *

load_dotenv()  # Загружаем переменные из .env  
# Создаем папку для бэкапов, если её нет

logging.basicConfig(
    level=logging.INFO,
    #format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
     encoding='utf-8',  
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

#TOKEN = API_TOKEN
#WEBHOOK_URL = "https://dc33d5df-e9e9-4153-9505-b4ace0946590.tunnel4.com"
#WEBHOOK_PATH = "/webhook"
#WEBAPP_HOST = "0.0.0.0"
#WEBAPP_PORT = 8080

storage = MemoryStorage()
bot = Bot(token=os.getenv("API_TOKEN"))
dispatcher = Dispatcher(storage=storage)
main_router = Router()
dispatcher.include_router(main_router)
dispatcher.include_router(registration_router)


@main_router.message(F.text.in_(["Бонусный баланс 🎁", "История бонусов 📌", "Адреса 🏠",
                             "Заказать доставку 🚗", "Задать вопрос 💬",
                             "Условия программы лояльности ✅", "Персональные предложения 👑"]))

async def handle_main_keyboard_button_click(message: Message):    
        user_id = message.from_user.id    
        match message.text:
                case "Бонусный баланс 🎁":
                    await get_bonus_balance_for_user(message, user_id)                                                 
                case "История бонусов 📌":
                    await get_bonus_balance_history_for_user(message, user_id)                             
                case "Адреса 🏠":
                    await message.answer(ADRESS_TEXT)
                case "Заказать доставку 🚗":
                    await message.answer("Для оформления заказа перейдите на наш сайт:", reply_markup=create_keyboard_make_order())                    
                case "Задать вопрос 💬":
                    await message.answer("Нажмите на кнопку ниже, чтобы перейти к боту поддержки и задать вопрос", reply_markup=create_keyboard_give_question())
                case "Условия программы лояльности ✅":                    
                    user_name = message.from_user.first_name 
                    await send_loyalty_text(user_id,user_name)                    
                case "Персональные предложения 👑":
                    await message.answer("Специальные предложения для вас...")

@main_router.message(F.text.in_(["Рассылки 📢", "Статистика базы данных 📊", "Запрос данных пользователя 🔎",
                             "Скрыть панель администрирования ❌"]))
async def handle_admin_keyboard_button_click(message: Message):    
        user_id = message.from_user.id    
        match message.text:
                case "Рассылки 📢":
                    await message.answer("Нажатка кнопка меню рассылок")                    
                case "Статистика базы данных 📊":
                    await get_db_size(message)
                case "Запрос данных пользователя 🔎":
                    await message.answer("Запрос данных пользователя...")
                case "Скрыть панель администрирования ❌":
                    await add_user_on_start(message)                  
                

@dispatcher.message(Command("yaposhka"))
async def show_stats(message: Message):
    """
    Показывает общую статистику заказов (только для админа)
    """
    admin_ids_str = os.getenv("ADMIN_IDS")

    if admin_ids_str:
        ADMIN_IDS = [int(id_str) for id_str in admin_ids_str.split(',')]
    else:
        ADMIN_IDS = [] 

    user_id = message.from_user.id
    user_name = message.from_user.first_name 
    if user_id not in ADMIN_IDS:
        await message.reply("Ваш аккаунт не обладает правами админа")        
        logger.error(f"Запрос на администрирование от пользователя без прав администратора: {user_id}")         
        return
    await message.answer(
            f"Привет, {user_name}! Ниже представлено меню администрирования",
            reply_markup=create_replay_keyboard_for_admins()
        )    

async def get_db_size (message:Message):
    try:
        size,error = get_total_users_count()         
        if error:
            raise ValueError(error)
        await message.answer(f"В базе данных {size} пользователей")                       
        
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе статистики: {e}")         


@dispatcher.callback_query(lambda call: call.data == 'type_about_loyalty')
async def process_callback_type_new_user(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)  
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await send_loyalty_text(user_id,user_name)    

async def send_loyalty_text (user_id, user_name):    
    await bot.send_message(user_id, LOYATLY_TEXT)    
    logger.info(f"Пользователю {user_id} ({user_name}) отправлены условия программы лояльности")

# Обработчик команды /start
@dispatcher.message(Command("start"))
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name 
    user_id = message.from_user.id
    await add_user_on_start(message)
    logger.info(f"Пользователь {user_id} ({user_name}) запустил /start")


async def add_user_on_start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    query_result = execute_query("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    data, error = query_result

    if error:
        logger.error(f"Ошибка при проверке пользователя в БД: {error}")
        await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")
        return

    if not data:
        logger.info(f"Новый пользователь: {user_id} ({user_name})")        
        #welcome_text = WELCOME_TEXT.format(username=user_name)        
        welcome_text = WELCOME_TEXT_FOR_PROMO.format(username=user_name)        
        photo_path = 'welcome_pic.jpg'
        await message.answer_photo(
            photo=types.FSInputFile(path=photo_path), 
            caption=welcome_text,
            parse_mode="HTML",
            reply_markup=create_keyboard_for_new_user())
        
    else:
        logger.info(f"Пользователь уже зарегистрирован: {user_id} ({user_name})")
        await message.answer(
            f"Привет, {user_name}! Рады видеть Вас снова.",
            reply_markup=create_replay_keyboard_for_user_after_registration()
        )

async def main():          
    await create_db()        
    await include_create_new_user_func (dispatcher, bot, logger)    
    await create_backup_dir()
    await start_scheduler_backup(bot)
    await dispatcher.start_polling(bot) 
    logger.info("Бот запущен!")       


if __name__ == "__main__":
    asyncio.run(main())        
        

