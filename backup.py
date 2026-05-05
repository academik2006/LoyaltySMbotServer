from datetime import datetime
import shutil
from asyncio.log import logger
from dotenv import load_dotenv
import os
from aiogram.types import FSInputFile
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()  # Загружаем переменные из .env 

db_path = os.getenv("DB_PATH") 
backup_dir = os.getenv("BACKUP_DIR") 

async def create_backup_dir():
    os.makedirs(backup_dir, exist_ok=True)


def create_backup() -> str | None:
    """
    Создает копию файла базы данных.
    Возвращает путь к файлу, если успешно, иначе None.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_filename = f"user_db_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copyfile(db_path, backup_path)
        logger.info(f"Создана копия базы данных {backup_path}")          
        return backup_path
    except FileNotFoundError:
        logger.error(f"Файл базы данных {db_path} не найден")  
    except Exception as e:
        logger.error(f"Не удалось создать бэкап {e}") 
    return None


async def send_backup_to_admins(backup_path: str, bot):
    """
    Отправляет файл бэкапа всем администраторам.
    """
    if not backup_path or not os.path.exists(backup_path):
        logger.error(f"Нет файла для отправки") 
        return
    
    dev_id = os.getenv("DEV_ID")   
    try:
        document = FSInputFile(backup_path)
        await bot.send_document(chat_id=dev_id, document=document, caption=f"Резервная копия базы данных\nДата: {datetime.now().strftime('%d.%m.%Y')}")                        
        logger.info (f"Бэкап успешно отправлен разработчику")
    except Exception as e:
        logger.info(f"Не удалось отправить бэкап разработчику: {e}")

async def daily_backup_job(bot):
    """
    Основная задача планировщика.
    Важно использовать dp.async_create_task(), чтобы избежать блокировки.
    """
    logger.info("Запуск задачи ежедневного бэкапа...")
    backup_path = create_backup()
    
    if backup_path:        
        await send_backup_to_admins(backup_path, bot)
        


async def start_scheduler_backup(bot):
    """
    Настраивает и запускает планировщик.
    """
    scheduler = AsyncIOScheduler()
    
    # Запускаем задачу каждый день в 12:00 ночи.
    # Вы можете изменить время на удобное вам.    
    scheduler.add_job(daily_backup_job, trigger=CronTrigger(hour=13, minute=57), kwargs={"bot": bot})        
    scheduler.start()
    logger.info("Планировщик задач запущен. Бэкап будет создаваться ежедневно в 03:00.")

