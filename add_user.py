from aiogram import types
from aiogram.types import Message
from aiogram.filters.command import *
from keyboards import *
from db_utils import *
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter


# Определяем состояния
class UserInfo(StatesGroup):
    phone = State()  # ожидание номера телефона
    email = State()   # ожидание почты
    birthday = State()   # ожидание даты рождения   


def include_create_new_user_func (dp, bot, logger):

    @dp.callback_query(lambda call: call.data == 'type_new_user')
    async def process_callback_type_new_user(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)  # Подтверждение приема события
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        await bot.send_message(user_id, "Пожалуйста, введите номер в формате +7*******, содержащий ровно 12 символов.", reply_markup=create_keyboard_for_cancel())
        await state.set_state(UserInfo.phone)
        logger.info(f"У пользователя {user_id} ({user_name}) запрошен номер телефона")
    
    
    @dp.message(StateFilter(UserInfo.phone))
    async def process_phone(message: Message, state: FSMContext):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        try:
            phone = message.text

            if len(phone) != 12 or not phone.startswith('+') or not phone[1:].isdigit():
                raise ValueError("Неверный формат номера! Пожалуйста, введите номер в формате +7*******, содержащий ровно 12 символов.")                               
            
            await state.update_data(phone=phone)
            await message.answer(f"Отлично. Укажите ваш email")
            await state.set_state(UserInfo.email)
            logger.info(f"У Пользователя {user_id} ({user_name}) запрошена почта")           

        except ValueError as e:
            await message.answer(str(e))
            await state.set_state(UserInfo.phone)  # Возвращаем пользователя на этап ввода телефона
            return        
        

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
        await add_new_user_to_db(message,state)
        

    async def add_new_user_to_db(message: Message, state: FSMContext):
        # Получаем все необходимые данные
        data = await state.get_data()
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        phone = data.get('phone', '')
        email = data.get('email', '')
        birthday = data['birthday']

        # Добавляем пользователя в базу данных
        try:
            error = add_user_to_database(user_id, user_name, phone, email, birthday)
            if error:
                raise ValueError(error)  # Поднимаем исключение с описанием ошибки
        except ValueError as e:
            # Сообщаем пользователю об ошибке
            await message.answer(f"К сожалению, произошла ошибка при добавлении пользователя: {e}")
            logger.error(f"Произошла ошибка при добавлении пользователя {user_name}: {e}")
        else:
            # Всё прошло успешно, сообщаем пользователю
            await message.answer("Поздравляю! Вы успешно зарегистрированы в нашей программе лояльности.", reply_markup=create_keyboard_for_user_after_registration())
            logger.info(f"Пользователь {user_name} успешно зарегистрирован в программе лояльности.")
        finally:
            # Всегда сбрасываем состояние после завершения операции
            await state.clear()

    @dp.callback_query(lambda call: call.data == 'type_cancel')
    async def process_callback_type_cancel(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)  # Подтверждение приема события
        
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.first_name
        await bot.send_message(user_id, "Процесс регистрации нового пользователя отменен", reply_markup=create_keyboard_for_new_user())
        await state.clear()
        logger.info(f"Пользователь {user_id} ({user_name}) отменил процесс регистрации")        
