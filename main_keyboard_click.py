
from asyncio.log import logger

from db_utils import *
from network import *


async def get_bonus_balance_history_for_user(message, user_id):
    try:
        phone, error = get_phone_by_user_id(user_id)
        if error:
            raise ValueError(error)       
        api_result = await get_history_bonus_for_user(phone)         
        logger.info(f"Результат запроса истории начисления бонусов {api_result}") 

        if api_result.get("success"):        
            #bonus=api_result['data']['bonusCount']

            if bonus is None:
                bonus=0                                   
            await message.answer(f"Пришла история начисления бонусов{api_result}")
                        
        else:
            error_code = api_result.get("status", "неизвестный")
            error_text = api_result.get("error", "Произошла ошибка на сервере.")        
            logger.info(f"При запросе истории начисления бонусных балов произошла ошибка код {error_code}, причина {error_text}") 
            await message.answer(f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз позже")                            
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе к базе данных {user_id}: {e}")         
                  

async def get_bonus_balance_for_user(message, user_id):
    try:
        idloyaty, error = get_idloyaty_by_user_id(user_id)
        if error:
            raise ValueError(error)       
        api_result = await get_user_info(idloyaty)         
        logger.info(f"Результат запроса бонусного баланса {api_result}") 

        if api_result.get("success"):        
            bonus=api_result['data']['bonusCount']
            if bonus is None:
                bonus=0                                   
            await message.answer(f"Баланс бонусных баллов {bonus} бонусов")
                        
        else:
            error_code = api_result.get("status", "неизвестный")
            error_text = api_result.get("error", "Произошла ошибка на сервере.")        
            logger.info(f"При запросе баланса бонусных балов произошла ошибка код {error_code}, причина {error_text}") 
            await message.answer(f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз позже")                            
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе к базе данных {user_id}: {e}")