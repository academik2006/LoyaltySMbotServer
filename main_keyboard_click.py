from asyncio.log import logger
from datetime import datetime
from db_utils import *
from network import *



async def get_bonus_balance_history_for_user(message, user_id):
    try:
        # Получаем ID лояльности по user_id
        idloyaty, error = get_idloyaty_by_user_id(user_id)
        if error:
            raise ValueError(error)        
        
        # Отправляем запрос на получение истории        
        #idloyaty = "060100CE-3059-4668-82B9-18F8D9E93837"        
        api_result = await get_history_bonus_for_user(idloyaty)        
        logger.info(f"Результат запроса истории начисления бонусов {api_result}")
        
        # Если успешный ответ
        if api_result.get("success"):
            # Формируем красивое сообщение с историей операций
            user_info_text = format_last_operations(api_result)            
            await message.answer(user_info_text)      
        else:
            error_code = api_result.get("status", "неизвестный")
            error_text = api_result.get("error", "Произошла ошибка на сервере.")
            logger.info(f"При запросе истории начисления бонусных балов произошла ошибка код {error_code}, причина {error_text}")
            await message.answer(f"❌ Ошибка {error_code}: {error_text}\n\nПожалуйста, попробуйте еще раз позже")
    
    except ValueError as e:
        await message.answer(f"⚠️ Произошла ошибка при запросе к базе данных: {e}")
        logger.error(f"Ошибка при запросе к базе данных {user_id}: {e}")         

def format_last_operations(response: dict) -> str:
    """Возвращает строку с последними 10 операциями для отправки в Telegram"""
    
    # Берём последние 10 операций из истории
    operations = response['data']['history']

    if not response.get('data') or not response['data'].get('history'):
        return "❗ Нет данных об операциях."
    
    # Вспомогательная функция для форматирования даты
    def format_date(date_str):
        dt = datetime.fromisoformat(date_str.split('.')[0]).strftime('%d.%m.%Y %H:%M')
        return dt
    
    # Формируем итоговую строку
    lines = []
    for op in operations:
        # Определяем сумму (либо начисление, либо списание)
        amount = op.get('points_delta', 0) or op.get('debited_points_delta', 0)
        
        # Определяем тип операции
        operation_type = {
            'PURCHASE': 'Покупка ',
            'MANUAL': 'Ручное     ',
            'EXPIRATION': 'Списание'
        }.get(op['action'], '')
        
        # Формируем строку
        lines.append(f"{format_date(op['action_date'])}  {operation_type}  {amount:+}")
            
    # Возвращаем полную строку
    return "\n".join(lines)   

                 

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