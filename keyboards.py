from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_keyboard_for_choose_avatar_photo ():

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    load_button = types.InlineKeyboardButton(text="Загрузить фото своей половинки", callback_data='load_own')
    select_standard_button = types.InlineKeyboardButton(text="Выбрать стандартное", callback_data='select_standard')
    keyboard.add(load_button, select_standard_button)
    
    return keyboard

def create_keyboard_for_choose_gender ():

    buttons = [
        'Мужской',
        'Женский'        
    ]
    return create_keyboard (buttons, True)    

def create_keyboard_for_new_user():

    buttons = [
        'Условия программы лояльности',        
        'Вступить',
    ]
    return create_keyboard (buttons, False)

def create_keyboard_for_info():

    buttons = [
        'Правила игры',        
        'Сколько до финиша'        
    ]
    return create_keyboard (buttons, False)

def create_keyboard_for_continue():
    buttons = [("Проведать любимку ❤️", "visit_avatar")]
    return create_inline_keyboard(buttons)

def create_keyboard_for_chatacter_avatar(gender):
    buttons = []
    
    if gender == 'female':
        actions = {
            "Покормить роллами 🍣": "action_hunger",
            "Сводить в SPA 🛀": "action_fatigue",
            "Скинуть денежки на развлечения 💳": "action_entertainment",
            "Обнять и поцеловать 😘": "action_kiss"
        }
    else:
        actions = {
            "Заказать WOK 🍜": "action_hunger",
            "Положить на диван перед телевизором 📺": "action_fatigue",
            "Отпустить с пацанами в баню 🏖️": "action_entertainment",
            "Похвалить и сказать «ты лучший» 👌": "action_kiss"
        }

    for label, callback_data in actions.items():
        buttons.append([InlineKeyboardButton(label, callback_data=callback_data)])

    return InlineKeyboardMarkup(buttons)
        

def create_keyboard(buttons, one_time):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=one_time)    
    for text in buttons:
        btn = types.KeyboardButton(text=text)
        keyboard.add(btn)

    return keyboard  

def create_inline_keyboard(buttons, callback_prefix=''):
        
    markup = InlineKeyboardMarkup(row_width=len(buttons))
    for button_text, callback_data in buttons:
        full_callback_data = f"{callback_prefix}{callback_data}"
        button = InlineKeyboardButton(text=button_text, callback_data=full_callback_data)
        markup.add(button)
    return markup