import logging
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from add_user import *
from keyboards import *
from db_utils import *
from api_key import API_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(storage=storage)
router = Router()
dispatcher.include_router(router)

# Основной роутер обработчиков

#@router.message(F.text.in_(["Бонусный баланс", "История бонусов", "Адреса",
#                             "Заказать доставку", "Задать вопрос",
#                             "Условия программы лояльности", "Персональные предложения"]))
@router.message(F.text)
async def handle_main_keyboard_button_click(message: Message):
        logger.info(f"Сработал обработчик кнопок с текстом {message.text}")
        match message.text:
                case "Бонусный баланс":
                    await message.answer("Ваш бонусный баланс...")
                case "История бонусов":
                    await message.answer("История начислений бонусов...")
                case "Адреса":
                    await message.answer("Список адресов доставки...")
                case "Заказать доставку":
                    await message.answer("Оформление заказа...")
                case "Задать вопрос":
                    await message.answer("Задавайте ваш вопрос...")
                case "Условия программы лояльности":
                    await message.answer("Условия программы лояльности...")
                case "Персональные предложения":
                    await message.answer("Специальные предложения для вас...")




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
    await bot.send_message(user_id, "Куча каких-то условий и правил")    
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
    result = execute_query("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not result:        
        image_path = 'welcome_pic.jpg'          
        with open(image_path, 'rb') as photo_file:            
            await message.answer(f"Привет, {user_name}! Добро пожаловать в программу лояльности Суши Мастер.",photo=photo_file, reply_markup=create_keyboard_for_new_user())                               
    else:        
        await message.answer(f"Привет, {user_name}! Рады видеть Вас снова", reply_markup=create_replay_keyboard_for_user_after_registration())                       

async def main():  
    logger.info("Создание базы данных")
    await create_db()
    logger.info("База данных создана")    
    logger.info("Бот запущен!")       
    await dispatcher.start_polling(bot) 

    #await create_db()
    
    #await include_create_new_user_func (dispatcher, bot, logger)
    #await dispatcher.start_polling(bot)
    #logger.info("Бот запущен!")
       

if __name__ == "__main__":
    asyncio.run(main())