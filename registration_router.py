import re
from datetime import datetime
from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards import *
from db_utils import *
import logging

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

# 1. ОПРЕДЕЛЯЕМ СОСТОЯНИЯ (States)
class UserInfo(StatesGroup):
    phone = State()    # Ожидание номера телефона
    email = State()    # Ожидание почты
    birthday = State() # Ожидание даты рождения

# 2. СОЗДАЕМ ОТДЕЛЬНЫЙ РОУТЕР ДЛЯ СЦЕНАРИЯ РЕГИСТРАЦИИ
registration_router = Router(name="registration_router")

# --- Все обработчики, относящиеся к регистрации, будут здесь ---
# Они не нуждаются в StateFilter, так как будут подключены к основному роутеру с этим условием.

@registration_router.message(F.content_types(types.ContentType.CONTACT))
async def process_phone_contact(message: types.Message, state: FSMContext):
    """Обработчик для случая, когда пользователь прислал КОНТАКТ."""
    phone_number = message.contact.phone_number
    logger.info(f"Пользователь {message.from_user.id} прислал контакт: {phone_number}")

    await state.update_data(phone=phone_number)
    await state.set_state(UserInfo.email)

    await message.answer(
        "✅ Номер принят из вашего профиля. Теперь, пожалуйста, укажите ваш email.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@registration_router.message(F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    """Обработчик для случая, когда пользователь ВВЁЛ ТЕКСТ вручную."""
    phone_number = message.text.strip()
    logger.info(f"Пользователь {message.from_user.id} ввел номер вручную: {phone_number}")

    # --- Валидация введенного текста ---
    if len(phone_number) != 12 or not phone_number.startswith('+7') or not phone_number[1:].isdigit():
        await message.answer("❌ Неверный формат номера. Пожалуйста, введите его заново или воспользуйтесь кнопкой.")
        return  # Пользователь остается в состоянии UserInfo.phone

    await state.update_data(phone=phone_number)
    await state.set_state(UserInfo.email)

    await message.answer(
        "✅ Номер принят. Теперь, пожалуйста, укажите ваш email.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@registration_router.message(F.text)
async def process_email(message: types.Message, state: FSMContext):
    """Обработчик ввода email."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    email = message.text.strip()

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not re.match(email_regex, email):
        await message.answer("❌ Неверный формат e-mail. Пожалуйста, введите корректный адрес.")
        return

    await state.update_data(email=email)
    await message.answer(
        "✅ E-mail принят. Укажите дату Вашего рождения в формате ДД.ММ.ГГГГ (например, 27.01.1984)"
    )
    await state.set_state(UserInfo.birthday)
    logger.info(f"У пользователя {user_id} запрошена дата рождения")

@registration_router.message(F.text)
async def process_birthday(message: types.Message, state: FSMContext):
    """Обработчик ввода даты рождения."""
    birthday = message.text.strip()

    # Проверка формата: dd.mm.yyyy
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthday):
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ (например, 27.01.1984).")
        return

    # Проверка существования даты
    try:
        datetime.strptime(birthday, '%d.%m.%Y')
    except ValueError:
        await message.answer("❌ Такой даты не существует. Пожалуйста, проверьте и введите заново.")
        return

    await state.update_data(birthday=birthday)
    
    # Переходим к финальной функции сохранения в БД
    await add_new_user_to_db(message, state)


async def add_new_user_to_db(message: types.Message, state: FSMContext):
    """Функция сохранения данных пользователя в базу."""
    data = await state.get_data()
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    phone = data.get('phone', '')
    email = data.get('email', '')
    birthday = data.get('birthday', '')
    
    try:
        error = add_user_to_database(user_id, user_name, phone, email, birthday)
        if error:
            raise ValueError(error)
            
        await message.answer(
            "🎉 Поздравляю! Вы успешно зарегистрированы!",
            reply_markup=create_replay_keyboard_for_user_after_registration()
        )
        logger.info(f"Пользователь {user_name} успешно зарегистрирован.")
        
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при регистрации: {e}")
        logger.error(f"Ошибка при регистрации {user_name}: {e}")
        
    finally:
        # Сбрасываем состояние FSM в любом случае (успех/ошибка)
        await state.clear()


# --- ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К ДИСПЕТЧЕРУ ---
async def include_create_new_user_func(dispatcher: Dispatcher, bot: Bot, logger: logging.Logger):
    """
    Эта функция подключает все обработчики регистрации к основному диспетчеру.
    """
        
    # --- ОБРАБОТЧИКИ НАЧАЛА И ОТМЕНЫ ---
    
    @dispatcher.callback_query(lambda call: call.data == 'type_new_user')    
    @dispatcher.include_router(registration_router, StateFilter(UserInfo.phone))
    async def process_callback_type_new_user(callback_query: types.CallbackQuery, state: FSMContext):
        """Обработчик кнопки 'Стать новым пользователем'."""
        await bot.answer_callback_query(callback_query.id)
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        
        await bot.send_message(
            user_id,
            "Пожалуйста, введите номер в формате +7******* или передайте его с помощью кнопки.",
            reply_markup=create_keyboard_for_ask_phone()
        )
        
        await state.set_state(UserInfo.phone)
        logger.info(f"Начало регистрации для пользователя {user_id} ({user_name})")
    
    @dispatcher.callback_query(lambda call: call.data == 'type_cancel')
    async def process_callback_type_cancel(callback_query: types.CallbackQuery, state: FSMContext):
        """Обработчик кнопки 'Отмена'."""
        await bot.answer_callback_query(callback_query.id)
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        
        await bot.send_message(
            user_id,
            "Процесс регистрации отменен.",
            reply_markup=create_keyboard_for_new_user()
        )
        
        await state.clear()
        logger.info(f"Регистрация отменена пользователем {user_id} ({user_name})")   

   