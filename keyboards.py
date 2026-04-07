from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def create_keyboard_for_new_user():

    button1 = InlineKeyboardButton(text="Условия программы лояльности", callback_data="type_about_loyalty")
    button2 = InlineKeyboardButton(text="Вступить", callback_data="type_new_user")

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
        [KeyboardButton(text="Персональные предложения 👑")],
        [KeyboardButton(text="Задать вопрос 💬")], 
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return reply_markup

def create_keyboard_for_ask_phone():
    button1 = InlineKeyboardButton(text="Написать в чат боту", callback_data="type_send_phone_manual")
    button2 = InlineKeyboardButton(text="Передать понтакт из профиля Telegram", callback_data="type_send_contact_from_telegram")
    button3 = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2],
            [button3]
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
        resize_keyboard=True
    )
    
    return keyboard

def create_keyboard(buttons, one_time):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=one_time)    
    for text in buttons:
        btn = KeyboardButton(text=text)
        keyboard.add(btn)

    return keyboard  


def create_keyboard_for_cancel():    
    button = InlineKeyboardButton(text="Отмена", callback_data="type_cancel")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button],            
        ]
    )    
    return keyboard
    