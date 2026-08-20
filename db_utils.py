
from datetime import date
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
db_name = os.getenv("DB_NAME")
db_path = os.getenv("DB_PATH")

async def create_db():    
    
    execute_query(f'''
        CREATE TABLE IF NOT EXISTS {db_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,      
            user_id INTEGER,
            username TEXT,
            phone TEXT,
            idloyaty TEXT,
            email TEXT,
            birthday TEXT,
            bonus BIGINT DEFAULT 0,
            notification BOOLEAN DEFAULT FALSE,
            subscription BOOLEAN,      
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

def connect_db():        
    return sqlite3.connect(f'{db_path}')  # Подключение к базе данных

def get_user_by_phone(phone):  
    
    query = f"""
        SELECT user_id, username, phone, idloyaty, email, birthday, 
               bonus, notification, subscription, created_at 
        FROM {db_name} WHERE phone = ?
    """    
    result, error = execute_query(query, (phone,))

    if error:
        return None, error
    if result:
        return result[0], None  
    return None, None  # Пользователь не найден    

def get_users_with_birthday_today():
    """
    Возвращает список пользователей, у которых сегодня день рождения.
    Работает с базой, где birthday хранится строго в формате DD.MM.YYYY.
    """
    today = date.today()
    # Ваш эталон поиска: "день.месяц."
    day_month_format = today.strftime("%d.%m.") 
        
    query = f"""
    SELECT user_id, username FROM {db_name} WHERE TRIM(birthday) LIKE ? 
        """
    result, error = execute_query(query, (day_month_format + '%',))

    if error:
        return None, error
        
    return result, None

def execute_query(query, params=None):
    """
    Выполняет SQL-запрос и возвращает результат (для SELECT).
    :param query: строка с SQL-запросом
    :param params: кортеж с параметрами для подставления в запрос
    :return: список кортежей с результатами (если применимо)
    """
    conn = connect_db()    
    result = []
    error = None
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Проверяем, является ли запрос SELECT
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()  # Получаем все записи
            
        conn.commit()  # Сохраняем изменения для остальных типов запросов
    except Exception as e:
        print(f'Ошибка при выполнении запроса: {e}')
        error = f'Ошибка при выполнении запроса: {e}'
    finally:
        close_connection(conn)  # Закрываем соединение вне зависимости от результата
    
    return result,error

def get_idloyaty_by_user_id(user_id):
    query = f"SELECT idloyaty FROM {db_name} WHERE user_id = ?"
    result, error = execute_query(query, (user_id,))
    if error:
        return None, error
    if result:
        return result[0][0], None  # Возвращаем значение idloyaty
    return None, None  # Пользователь не найден

def add_user_to_database(user_id, username,phone,idloyaty,email,birthday,subscription):
        
    # Формулируем запрос с использованием плейсхолдеров
    query = f"INSERT INTO {db_name} (user_id, username, phone, idloyaty,email, birthday, subscription) VALUES (?,?,?,?,?,?,?)"        
    _, error = execute_query(query, (user_id, username, phone, idloyaty,email, birthday, subscription))
    return error  # Возвращаем ошибку (None, если всё хорошо)

def update_user_subscription(user_id, subscription):
    """
    Обновляет статус подписки (поле 'subscription') для пользователя с указанным user_id.

    :param user_id: ID пользователя в Telegram.
    :param subscription: Новое значение подписки (True или False).
    :return: Возвращает ошибку, если она возникла, или None в случае успеха.
    """    
    query = f"UPDATE {db_name} SET subscription = ? WHERE user_id = ?"    
    
    _, error = execute_query(query, (subscription, user_id))
    
    return error  # Возвращаем ошибку (None, если всё хорошо)

def get_total_users_count():
    """
    Возвращает общее количество записей в таблице пользователей.
    :return: (количество, ошибка). Если всё хорошо, количество будет целым числом, а ошибка - None.
    """
    query = f"SELECT COUNT(*) FROM {db_name};"       
    result, error = execute_query(query)
    
    if error:
        return 0, error   
    
    return result[0][0], None


def close_connection(conn):    
    if conn is not None:
        conn.close()
      
    
