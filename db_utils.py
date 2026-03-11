
import sqlite3

async def create_db():
    # Исправляем структуру таблицы и удаляем лишнюю закрывающую скобку
    execute_query('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            phone TEXT,
            email TEXT,
            birthday TEXT,
            bonus BIGINT DEFAULT 0,
            notification BOOLEAN DEFAULT FALSE,
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
    finally:
        close_connection(conn)  # Закрываем соединение вне зависимости от результата
    
    return result


def add_user_to_database(user_id, username,phone,email,birthday):
        
    # Формулируем запрос с использованием плейсхолдеров
    query = "INSERT INTO users (user_id, username, phone, email, birthday) VALUES (?, ?, ?, ?, ?)"    
    # Передаем параметры через tuple
    execute_query(query, (user_id, username,phone,email,birthday))


def close_connection(conn):    
    if conn is not None:
        conn.close()
      
    
