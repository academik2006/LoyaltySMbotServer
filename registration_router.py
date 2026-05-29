import re
from datetime import datetime
from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNotFound
from db_utils import *
import logging
from keyboards import *
from messages import LAVA_PRIZE, POLICY_TEXT, WELCOME_PRIZE_TEXT
from network import *

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

# 1. ОПРЕДЕЛЯЕМ СОСТОЯНИЯ (States)
class UserInfo(StatesGroup):    
    phone = State()    # Ожидание номера телефона   
    sms = State() #Валидация номера телефона
    idloyaty = State() #Валидация номера телефона
    email = State()    # Ожидание почты
    birthday = State() # Ожидание даты рождения

registration_router = Router(name="registration_router")

#CHANNEL_USERNAME = "-1001265323457"

@registration_router.message(F.content_type == types.ContentType.CONTACT)
async def process_phone_contact(message: types.Message, state: FSMContext):
    """Обработчик для случая, когда пользователь прислал КОНТАКТ."""
    
    # Получаем номер из объекта Contact
    raw_phone = message.contact.phone_number

    # Логика нормализации:
    # 1. Если номер начинается с '8', заменяем на '+7'.
    # 2. Если номер начинается с '7' (без плюса), добавляем '+'.
    # 3. В остальных случаях (например, уже +7 или +1) оставляем как есть.
    
    if raw_phone.startswith('8'):
        # Случай: 8983...
        phone_number = '+7' + raw_phone[1:]
    elif raw_phone.startswith('7'):
        # Ваш случай: 7983... (добавляем плюс)
        phone_number = '+' + raw_phone
    else:
        # Для международных номеров или других форматов
        phone_number = raw_phone 

    logger.info(f"Пользователь {message.from_user.id} прислал контакт. Нормализованный номер: {phone_number}")

    await state.update_data(phone=phone_number)
    #await state.set_state(UserInfo.email)

    await message.answer(
        f"✅ Номер {phone_number} успешно загружен из вашего профиля. Необходимо пройти процедуру подтверждения номера номера",
        reply_markup=create_keyboard_for_ask_sms()
    )

@registration_router.message(StateFilter(UserInfo.phone),F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    """Обработчик для случая, когда пользователь ВВЁЛ ТЕКСТ вручную."""
    phone_number = message.text.strip()
    logger.info(f"Пользователь {message.from_user.id} ввел номер вручную: {phone_number}")

    if len(phone_number) != 12 or not phone_number.startswith('+7') or not phone_number[1:].isdigit():
        await message.answer("❌ Неверный формат номера. Пожалуйста, введите номер заново.", reply_markup=create_keyboard_for_cancel())
        return  # Пользователь остается в состоянии UserInfo.phone

    await state.update_data(phone=phone_number)
    
    await message.answer(
        f"✅ Номер {phone_number}  принят. Необходимо пройти процедуру подтверждения номера телефона",
        reply_markup=create_keyboard_for_ask_sms()
    )

@registration_router.message(StateFilter(UserInfo.sms),F.text)
async def process_send_validate_sms_text(message: types.Message, state: FSMContext):
    """Обработчик для случая, когда пользователь отправил SMS боту"""
    
    try:
        code = message.text.strip()
        code_int = int(code)
    except ValueError:
        print("Строка не может быть преобразована в целое число.")

    
    logger.info(f"Пользователь {message.from_user.id} ввел sms: {code}")

    data = await state.get_data()
    phone = data.get('phone', '')
    
    if len(code) != 4 or not code.isdigit():
        await message.answer("❌ Неверный формат SMS. Пожалуйста, введите код из 4 цифр из SMS-сообщения", reply_markup=create_keyboard_for_cancel())
        return 

    await state.update_data(sms=code_int)
    api_result = await validate_sms_code (phone,code_int)         

    if api_result.get("success"):        
        # Если код 200, идем дальше (запрашиваем полученный код)
        idloyaty=api_result["data"]["id"]
        logger.info(f"Отправили SMS для потверждения номера для {phone}, результат успешно, сохранен idloyaty {idloyaty}") 
        await state.update_data(idloyaty=idloyaty)        
        await message.answer(            
            "✅ Код подтверждения принят. Напишите ваш e-mail",
            reply_markup=create_keyboard_for_cancel()
        )
        await state.set_state(UserInfo.email)        
    else:
        # Если код НЕ 200, показываем ошибку и предлагаем повторить или отменить
        error_code = api_result.get("status", "неизвестный")
        error_text = api_result.get("error", "Произошла ошибка на сервере.")        
        logger.info(f"Отправили SMS для потверждения номера для {phone}, результат ошибка код {error_code}, причина {error_text}") 
        await message.answer(            
            f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз или отмените действие.",
            reply_markup=create_keyboard_for_cancel()
        )    
        return   


@registration_router.message(StateFilter(UserInfo.email), F.text)
async def process_email(message: types.Message, state: FSMContext):
    """Обработчик ввода email."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    email = message.text.strip()

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not re.match(email_regex, email):
        await message.answer("❌ Неверный формат e-mail. Пожалуйста, введите корректный адрес.", reply_markup=create_keyboard_for_cancel())
        return

    await state.update_data(email=email)
    await message.answer(
        "✅ E-mail принят. Укажите дату Вашего рождения в формате ДД.ММ.ГГГГ (например, 27.01.1984)"
    )
    await state.set_state(UserInfo.birthday)
    logger.info(f"У пользователя {user_id} запрошена дата рождения")

@registration_router.message(StateFilter(UserInfo.birthday),F.text)
async def process_birthday(message: types.Message, state: FSMContext):
    """Обработчик ввода даты рождения."""
    birthday = message.text.strip()

    # Проверка формата: dd.mm.yyyy
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthday):
        await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ (например, 27.01.1984).", reply_markup=create_keyboard_for_cancel())
        return

    # Проверка существования даты
    try:
        datetime.strptime(birthday, '%d.%m.%Y')
    except ValueError:
        await message.answer("❌ Такой даты не существует. Пожалуйста, проверьте и введите заново.", reply_markup=create_keyboard_for_cancel())
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
    idloyaty = data.get('idloyaty', '')
    email = data.get('email', '')
    birthday = data.get('birthday', '')
    
    try:
        error = add_user_to_database(user_id, user_name, phone, idloyaty, email, birthday)
        if error:
            raise ValueError(error)
        
        await message.answer(
            WELCOME_PRIZE_TEXT,
            #reply_markup=create_keyboard_start_welcome_prize()
        )
            
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


async def include_create_new_user_func(dispatcher: Dispatcher, bot: Bot, logger: logging.Logger): 
    
    
    @dispatcher.callback_query(lambda call: call.data == 'type_new_user')        
    async def process_callback_type_new_user(callback_query: types.CallbackQuery, state: FSMContext):
    
        await bot.answer_callback_query(callback_query.id)
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name        
        
        await bot.send_message(
           user_id,
           POLICY_TEXT,
           parse_mode="HTML", 
           reply_markup=create_keyboard_for_new_user_ask_suggestion() 
        )
        logger.info(f"Запросили согласие на участие в программе {user_id} ({user_name})")

    @dispatcher.callback_query(lambda call: call.data == 'type_new_user_send_suggestion')        
    async def process_callback_type_new_user(callback_query: types.CallbackQuery, state: FSMContext):
    
        await bot.answer_callback_query(callback_query.id)
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        
        await bot.send_message(
            user_id,
            "Для регистрации в программе лояльности необходимо передать и потвердить номер телефона. Выберите удобный способ",
            reply_markup=create_keyboard_for_ask_phone()
        )                
        logger.info(f"Начало регистрации для пользователя {user_id} ({user_name})")    

    @dispatcher.callback_query(lambda call: call.data == 'type_start_welcome_prize')        
    async def process_callback_type_new_user(callback_query: types.CallbackQuery):
    
        await bot.answer_callback_query(callback_query.id)
               
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        
        try:        
            chat_member = await bot.get_chat_member(chat_id="-100555", user_id=user_id)        
        
            if chat_member.status in ["member", "administrator", "creator"]:
                logger.info(f"Пользователь {user_id} ({user_name}) уже подписан на канал.")                                       
                photo_path = 'lava_prize.jpg'
                await bot.answer_photo(
                photo=types.FSInputFile(path=photo_path), 
                parse_mode="HTML"
                )

        except TelegramNotFound:    
        
            logger.info(f"Пользователь {user_id} ({user_name}) не подписан на канал. Запускаем процесс подписки.")      

            await bot.send_message(
                user_id,                
                "Подпишись на наш Telegram-канал, чтобы получить доступ к подарку.",
                reply_markup=create_keyboard_go_sushi_master_chanel()
            )
        logger.info(f"Пользователь зашел в процедуру получения стартового подарка {user_id} ({user_name})")            
        

    @dispatcher.callback_query(lambda call: call.data == 'type_send_phone_manual')
    async def process_callback_type_cancel(callback_query: types.CallbackQuery, state: FSMContext):        
        await bot.answer_callback_query(callback_query.id)        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        
        await bot.send_message(
            user_id,
            "Пришлите номер телефона в формате +7...., не более 12 цифр ",            
        )
        await state.set_state(UserInfo.phone)
        logger.info(f"Пользователь выбрать передать телефон в ручном формате {user_id} ({user_name})")      

    @dispatcher.callback_query(lambda call: call.data == 'type_send_contact_from_telegram')
    async def process_callback_type_cancel(callback_query: types.CallbackQuery):        
        await bot.answer_callback_query(callback_query.id)        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        await bot.send_message(
            user_id,
            "Пожалуйста, нажмите кнопку \"Отправить мой номер\", чтобы передать ваш номер автоматически",
            reply_markup=create_contact_keyboard()
        )   

        await bot.send_message(
            user_id,
            "Если передать номер не удалось (не задан в профиле Telegram), нажмите кнопку \"Отмена\"",
            reply_markup=create_keyboard_for_cancel()
        )   
                
        logger.info(f"Пользователь выбрать передать контакт из Телеграма {user_id} ({user_name})")          


    @dispatcher.callback_query(lambda call: call.data == 'type_send_sms')
    async def process_callback_type_send_sms(callback_query: types.CallbackQuery, state: FSMContext):        
        await bot.answer_callback_query(callback_query.id)        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        data = await state.get_data()
        phone_number = data.get('phone', '')
        api_result = await send_verification_code(phone_number)    

        logger.info(f"Пользователь {user_id} ({user_name} запросил SMS для потверждения номера для {phone_number}") 

        if api_result.get("success"):
        # Если код 200, идем дальше (запрашиваем полученный код)
            await state.set_state(UserInfo.sms)        
            await bot.send_message(
            user_id,
            "✅ Код подтверждения отправлен на ваш телефон. Напишите его в чат после получения",
            reply_markup=types.ReplyKeyboardRemove() # Убираем предыдущую клавиатуру
        )
        else:
            # Если код НЕ 200, показываем ошибку и предлагаем повторить или отменить
            error_code = api_result.get("status", "неизвестный")
            error_text = api_result.get("error", "Произошла ошибка на сервере.")                            
            await bot.send_message(
                user_id,
                f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз или отмените действие.",
                reply_markup=create_keyboard_for_ask_sms()
            )             
    
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

    
   