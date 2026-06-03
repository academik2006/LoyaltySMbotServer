
import sqlite3

async def create_db():    
    execute_query('''
        CREATE TABLE IF NOT EXISTS users (
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
    return sqlite3.connect('users.db')  # Подключение к базе данных

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
    query = "SELECT idloyaty FROM users WHERE user_id = ?"
    result, error = execute_query(query, (user_id,))
    if error:
        return None, error
    if result:
        return result[0][0], None  # Возвращаем значение idloyaty
    return None, None  # Пользователь не найден

def add_user_to_database(user_id, username,phone,idloyaty,email,birthday,subscription):
        
    # Формулируем запрос с использованием плейсхолдеров
    query = "INSERT INTO users (user_id, username, phone, idloyaty,email, birthday, subscription) VALUES (?,?,?,?,?,?,?)"        
    _, error = execute_query(query, (user_id, username, phone, idloyaty,email, birthday, subscription))
    return error  # Возвращаем ошибку (None, если всё хорошо)

def update_user_subscription(user_id, subscription):
    """
    Обновляет статус подписки (поле 'subscription') для пользователя с указанным user_id.

    :param user_id: ID пользователя в Telegram.
    :param subscription: Новое значение подписки (True или False).
    :return: Возвращает ошибку, если она возникла, или None в случае успеха.
    """    
    query = "UPDATE users SET subscription = ? WHERE user_id = ?"    
    
    _, error = execute_query(query, (subscription, user_id))
    
    return error  # Возвращаем ошибку (None, если всё хорошо)

def get_total_users_count():
    """
    Возвращает общее количество записей в таблице users.
    :return: (количество, ошибка). Если всё хорошо, количество будет целым числом, а ошибка - None.
    """
    # Используем COUNT(*) для эффективного подсчета строк
    query = "SELECT COUNT(*) FROM users;"
    
    # Выполняем запрос. execute_query вернет список с одним кортежем: [(count,)]
    result, error = execute_query(query)
    
    if error:
        return 0, error
    
    # result[0][0] достает число из результата [(count,)]
    return result[0][0], None


def close_connection(conn):    
    if conn is not None:
        conn.close()
      
    
