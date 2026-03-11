from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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

def create_keyboard_for_user_after_registration():

    button1 = InlineKeyboardButton(text="Бонусный баланс", callback_data="type_balans")
    button2 = InlineKeyboardButton(text="История начисления бонусов", callback_data="type_balans_history")
    button3 = InlineKeyboardButton(text="Адреса", callback_data="type_address")
    button4 = InlineKeyboardButton(text="Заказать доставку", callback_data="type_make_order")
    button5 = InlineKeyboardButton(text="Задать вопрос", callback_data="type_answer")
    button6 = InlineKeyboardButton(text="Условия программы лояльности", callback_data="type_about_loyalty")
    button7 = InlineKeyboardButton(text="Персональные предложения", callback_data="type_personal_offer")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [button1, button2],              # Линия с двумя кнопками
    [button3, button4],              # Линия с двумя кнопками
    [button5, button6],              # Линия с двумя кнопками
    [button7]                        # Последняя одиночная кнопка
        ]
    )    
    return keyboard