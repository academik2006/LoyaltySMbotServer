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