from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

#from registration_router import CHANNEL_USERNAME


def create_keyboard_for_new_user():

    button1 = InlineKeyboardButton(text="Условия программы лояльности", callback_data="type_about_loyalty")
    button2 = InlineKeyboardButton(text="Зарегистрироваться", callback_data="type_new_user")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2]
        ]
    )    
    return keyboard

def create_replay_keyboard_for_user_after_registration():
    buttons = [
        [KeyboardButton(text="Бонусный баланс 🎁"), KeyboardButton(text="История бонусов 📌")],
        [KeyboardButton(text="Адреса 🏠"), KeyboardButton(text="Заказать доставку 🚗")],        
        [KeyboardButton(text="Условия программы лояльности ✅")],
        #[KeyboardButton(text="Персональные предложения 👑")],
        [KeyboardButton(text="Задать вопрос 💬")], 
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return reply_markup

def create_replay_keyboard_for_admins():
    buttons = [
        [KeyboardButton(text="Рассылки 📢")],
        [KeyboardButton(text="Статистика базы данных 📊")],
        [KeyboardButton(text="Запрос данных пользователя 🔎")],
        [KeyboardButton(text="Скрыть панель администрирования ❌")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return reply_markup

def create_keyboard_for_ask_phone():
    button1 = InlineKeyboardButton(text="Написать в чат боту", callback_data="type_send_phone_manual")
    button2 = InlineKeyboardButton(text="Передать контакт из профиля Telegram", callback_data="type_send_contact_from_telegram")
    button3 = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2],
            [button3]
        ]
    )    
    return keyboard

def create_keyboard_for_ask_sms():
    button1 = InlineKeyboardButton(text="Запросить код авторизации", callback_data="type_send_sms")
    button2 = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2],            
        ]
    )    
    return keyboard

def create_keyboard_make_order():
    button = InlineKeyboardButton(text="Перейти на сайт sushi-master.ru", url="https://sushi-master.ru")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button],            
        ]
    )    
    return keyboard

def create_keyboard_give_question():
    button = InlineKeyboardButton(text="Задать вопрос 💬", url="https://t.me/SushiMasterRU_bot")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button],            
        ]
    )    
    return keyboard

def create_contact_keyboard():
    """
    Создает клавиатуру с кнопкой для запроса контакта.
    """
    contact_button = KeyboardButton(text="Отправить мой номер", request_contact=True)
    
    # Передаем список со списком кнопок в параметр keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[contact_button]], # Кнопка обернута в список, чтобы создать один ряд
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    return keyboard

def create_keyboard(buttons, one_time):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=one_time)    
    for text in buttons:
        btn = KeyboardButton(text=text)
        keyboard.add(btn)

    return keyboard  

def create_keyboard_for_new_user_ask_suggestion():

    button1 = InlineKeyboardButton(text="Согласен", callback_data="type_new_user_send_suggestion")
    button2 = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2]
        ]
    )    
    return keyboard


def create_keyboard_for_cancel():    
    button = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button],            
        ]
    )    
    return keyboard

def create_keyboard_start_welcome_prize():

    button1 = InlineKeyboardButton(text="Проверить подписку", callback_data="type_start_welcome_prize")    

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1]            
        ]
    )    
    return keyboard

def create_keyboard_go_sushi_master_chanel():
     
    #button1 = InlineKeyboardButton(text="Подписаться на канал Суши Мастер", url=f"https://t.me/{CHANNEL_USERNAME}")    
    button2 = InlineKeyboardButton(text="Проверить подписку", callback_data="type_start_welcome_prize")    

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            #[button1]
            [button2]            
        ]
    )    
    return keyboard   

    