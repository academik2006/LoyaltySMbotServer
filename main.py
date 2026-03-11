import logging
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from keyboards import *
from db_utils import *
from api_key import API_TOKEN
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StateFilter


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Определяем состояния
class UserInfo(StatesGroup):
    phone = State()  # ожидание номера телефона
    email = State()   # ожидание почты
    birthday = State()   # ожидание даты рождения   

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

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name   
    
    await message.answer(f"Привет, {user_name}! Добро пожаловать в программу лояльности Суши Мастер.",reply_markup=create_keyboard_for_new_user())   

    logger.info(f"Пользователь {user_id} ({user_name}) запустил /start")


@dp.callback_query(lambda call: call.data == 'type_new_user')
async def process_callback_type_new_user(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)  # Подтверждение приема события
    
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await bot.send_message(user_id, "Пожалуйста, добавьте свой номер телефона")
    await state.set_state(UserInfo.phone)
    logger.info(f"У пользователя {user_id} ({user_name}) запрошен номер телефона")

@dp.callback_query(lambda call: call.data == 'type_about_loyalty')
async def process_callback_type_new_user(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)  
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name
    await bot.send_message(user_id, "Куча каких-то условий и правил")    
    logger.info(f"Пользователю {user_id} ({user_name}) отправлены условия программы лояльности")

# Ввод имени
@dp.message(StateFilter(UserInfo.phone))
async def process_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    phone = message.text
    await state.update_data(phone=phone)
    await message.answer(f"Отлично. Укажите ваш email")
    await state.set_state(UserInfo.email)
    logger.info(f"У Пользователя {user_id} ({user_name}) запрошена почта")

@dp.message(StateFilter(UserInfo.email))
async def process_email(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    email = message.text
    await state.update_data(email=email)
    await message.answer(f"Принято. Укажите дату Вашего рождения в формате число.месяц.год (например, 27.01.1984)")
    await state.set_state(UserInfo.birthday)
    logger.info(f"У Пользователя {user_id} ({user_name}) запрошена дата рождения")    

@dp.message(StateFilter(UserInfo.birthday))
async def process_birthday(message: Message, state: FSMContext):
    birthday = message.text
    await state.update_data(birthday=birthday)
    
    # Получаем все необходимые данные
    data = await state.get_data()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    phone = data.get('phone', '')
    email = data.get('email', '')
    birthday = data['birthday']

    # Добавляем пользователя в базу данных
    try:
        add_user_to_database(user_id, user_name, phone, email, birthday)
        await message.answer("Поздравляю! Вы успешно зарегистрированы в нашей программе лояльности.")
        await state.clear()  # Очищаем состояние после завершения процесса
    except Exception as e:
        await message.answer("К сожалению, произошла ошибка при регистрации. Повторите попытку позже.")
        logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
  

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