import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from keyboards import *
from db_utils import *
from main_keyboard_click import *
from messages import WELCOME_TEXT
from registration_router import *
from api_keys import API_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from registration_router import registration_router
from aiohttp import web

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

ADMIN_ID = 123456789

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
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
                    await message.answer("Список адресов доставки...")
                case "Заказать доставку 🚗":
                    await message.answer("Оформление заказа...")
                case "Задать вопрос 💬":
                    await message.answer("Задавайте ваш вопрос...")
                case "Условия программы лояльности ✅":                    
                    user_name = message.from_user.first_name 
                    await send_loyalty_text(user_id,user_name)                    
                case "Персональные предложения 👑":
                    await message.answer("Специальные предложения для вас...")

async def get_db_size (message:Message):
    try:
        size,error = get_total_users_count()         
        if error:
            raise ValueError(error)
        await message.answer(f"В базе данных {size} пользователей")                       
        
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе статистики: {e}")         


@dispatcher.message(Command("stats"))
async def show_stats(message: Message):
    """
    Показывает общую статистику заказов (только для админа)
    """
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.reply("Ты не админ!")
        await get_db_size(message)    
        return    
    await get_db_size(message)    


@dispatcher.callback_query(lambda call: call.data == 'type_about_loyalty')
async def process_callback_type_new_user(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)  
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await send_loyalty_text(user_id,user_name)    

async def send_loyalty_text (user_id, user_name):
    loyality_text = "Куча каких-то условий и правил"
    await bot.send_message(user_id, loyality_text)    
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
        welcome_text = WELCOME_TEXT.format(username=user_name)
        await message.answer(welcome_text, reply_markup=create_keyboard_for_new_user())                                                                 
    else:
        logger.info(f"Пользователь уже зарегистрирован: {user_id} ({user_name})")
        await message.answer(
            f"Привет, {user_name}! Рады видеть Вас снова.",
            reply_markup=create_replay_keyboard_for_user_after_registration()
        )

async def main():      
    await create_db()        
    await include_create_new_user_func (dispatcher, bot, logger)    
    await dispatcher.start_polling(bot) 
    logger.info("Бот запущен!")       


if __name__ == "__main__":
    asyncio.run(main())        
        

# async def handle_webhook(request):
#     update = types.Update(**await request.json())
#     await dispatcher.process_update(update)
#     return web.Response()        

# async def on_startup(_):
#     await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
#     logger.info(f"Вебхук установлен: {WEBHOOK_URL + WEBHOOK_PATH}")

# async def on_shutdown(_):
#     await bot.delete_webhook()
#     logger.info("Вебхук удален")        

# async def main():
#     await create_db()
#     await include_create_new_user_func(dispatcher, bot, logger)

#     app = web.Application()
#     app.router.add_post(WEBHOOK_PATH, handle_webhook)
#     app.on_startup.append(on_startup)
#     app.on_shutdown.append(on_shutdown)

#     # Запуск через AppRunner (рекомендуется для async main)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
#     await site.start()

#     logger.info(f"Бот запущен с вебхуками на {WEBAPP_HOST}:{WEBAPP_PORT}")
    
#     # Чтобы приложение не завершилось
#     await asyncio.Event().wait() 

# if __name__ == "__main__":
#     asyncio.run(main())