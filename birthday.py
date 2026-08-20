from asyncio.log import logger
import os
from aiogram import types
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_utils import get_users_with_birthday_today
from messages import BIRTHDAY_TEXT

blocked_users = set()
company_name = os.getenv("COMPANY_NAME")
dev_id = os.getenv("DEV_ID") 

async def daily_birthday_job(bot):   
    logger.info("Запуск задачи ежедневного поздравления пользователей...")
    await send_daily_birthday_greetings(bot)

async def send_daily_birthday_greetings(bot):   

    logger.info("Функция send_daily_birthday_greetings запущена")    
    
    birthday_users, error = get_users_with_birthday_today()

    logger.info(f"Список именниников {birthday_users}")        
    
    if error:
        logger.error(f"Ошибка при получении списка именинников из БД: {error}")
        await bot.send_message(dev_id, "❌ Ошибка базы данных при поиске именинников.")
        return

    if not birthday_users:
        logger.info("Именинников сегодня не найдено.")
        await bot.send_message(dev_id, "🟡 Задача запущена, но именинников сегодня нет.")
        return

    logger.info(f"Успешный запуск. Найдено {len(birthday_users)} пользователей: {birthday_users}")
    await bot.send_message(dev_id, f"✅ Рассылка начата для {len(birthday_users)} пользователей.")    
    
    for user in birthday_users:                
        chat_id = user[0] 
        user_name = user[1]
        
        birthday_text = BIRTHDAY_TEXT.format(username=user_name, company_name=company_name)        
        
        if chat_id in blocked_users:
            logger.info(f"Пропущен заблокированный пользователь {chat_id}")
            continue
        
        try:
            photo_path = 'birthday.jpg'
            await bot.send_photo (
                chat_id=chat_id,
                photo=types.FSInputFile(path=photo_path), 
                caption=birthday_text,
                parse_mode="HTML",
            )                                          
            logger.info(f"ДР-поздравление отправлено пользователю {chat_id}")                        
                
        except Exception as e:
            error_message = str(e)
            if 'bot was blocked by the user' in error_message or 'Forbidden: user is deactivated' in error_message:
                blocked_users.add(chat_id)
                logger.warning(f"Пользователь {chat_id} добавил бот в черный список и теперь считается заблокированным")
            else:
                logger.error(f"Ошибка при отправке сообщения пользователю {chat_id}, ошибка {e}")

async def start_scheduler_birthday(bot):
    """
    Настраивает и запускает планировщик.
    """
    scheduler = AsyncIOScheduler()       
    scheduler.add_job(daily_birthday_job, trigger=CronTrigger(hour=12, minute=00), kwargs={"bot": bot})        
    scheduler.start()
    logger.info("Планировщик задач с поздравлениями запущен. Рассылка будет уходить ежедневно в 12:00")