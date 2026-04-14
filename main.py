import logging
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from keyboards import *
from db_utils import *
from messages import WELCOME_TEXT
from registration_router import *
from api_key import API_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from registration_router import registration_router

logging.basicConfig(
    level=logging.INFO,
    #format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
     encoding='utf-8',  
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


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
                    await message.answer("История начислений бонусов...")
                case "Адреса 🏠":
                    await message.answer("Список адресов доставки...")
                case "Заказать доставку 🚗":
                    await message.answer("Оформление заказа...")
                case "Задать вопрос 💬":
                    await message.answer("Задавайте ваш вопрос...")
                case "Условия программы лояльности ✅":
                    user_id = message.from_user.id
                    user_name = message.from_user.first_name 
                    await send_loyalty_text(user_id,user_name)                    
                case "Персональные предложения 👑":
                    await message.answer("Специальные предложения для вас...")

async def get_bonus_balance_for_user(message, user_id):
    try:
        idloyaty, error = get_idloyaty_by_user_id(user_id)
        if error:
            raise ValueError(error)       
        api_result = await get_user_info(idloyaty)         
        logger.info(f"Результат запроса бонусного баланса {api_result}") 

        if api_result.get("success"):        
            bonus=api_result['data']['bonusCount']
            if bonus is None:
                bonus=0                                   
            await message.answer(f"Баланс бонусных баллов {bonus} бонусов")
                        
        else:
            error_code = api_result.get("status", "неизвестный")
            error_text = api_result.get("error", "Произошла ошибка на сервере.")        
            logger.info(f"При запросе баланса бонусных балов произошла ошибка код {error_code}, причина {error_text}") 
            await message.answer(f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз позже")                            
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе к базе данных {user_id}: {e}")


# Обработчик команды /help
@dispatcher.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id

    await message.answer("Я умею:\n/start — поздороваться\n/help — показать это сообщение")
    logger.info(f"Пользователь {user_id} запросил /help")

@dispatcher.message(Command("about"))
async def about_command(message: Message):
    user_id = message.from_user.id

    await message.answer("Я бот, созданный на aiogram в марте 2026!")
    logger.info(f"Пользователь {user_id} запросил /about")

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