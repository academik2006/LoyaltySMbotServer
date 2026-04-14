from aiogram.types import CallbackQuery

async def get_user_info_from_message(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    return user_name, user_id

async def get_user_info_from_callback_query(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name    
    return user_name, user_id