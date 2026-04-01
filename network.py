import aiohttp
import json

API_URL = "https://venus-api-customers.snet.su/v1/sendCode/partner"
PARTNER_ID = "f0bab507-02b4-4199-aaec-da6d0348e516"
HEADERS = {
    "x-partner-id": PARTNER_ID,
    "Content-Type": "application/json"
}

async def send_verification_code(phone: str, retail_network_id: str):
    """
    Асинхронно отправляет код подтверждения через API.
    """
    payload = {
        "RetailNetworkId": retail_network_id,
        "Recipient": phone
    }

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(API_URL, json=payload) as response:
            return await response.text(), response.status


async def validate_sms_code(retail_network_id: str, recipient: str, code: int, source: str) -> dict:
    """
    Проверяет код из SMS, отправленный пользователю.
    
    Параметры:
    - retail_network_id (str): Идентификатор розничной сети.
    - recipient (str): Телефон получателя (например, '+79999999999').
    - code (int): Код подтверждения из SMS.
    - source (str): Источник (например, 'PARTNER').
    
    Возвращает:
    - dict: Данные пользователя, полученные в результате успешной проверки.
    """
    url = "https://venus-api-customers.snet.su/v1/validateCode"
    
    # Формирование тела запроса
    payload = {
        "RetailNetworkId": retail_network_id,
        "Recipient": recipient,
        "Code": code,
        "Source": source
    }
    
    # Выполнение асинхронного POST-запроса
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            # Обработка ответа
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Ошибка проверки кода ({response.status}): {await response.text()}")        

async def get_user_info(user_id: str) -> dict:
    """Асинхронно получает информацию о пользователе по user_id."""
    base_url = "https://venus-api-customers.snet.su/v1/get/"
    url = f"{base_url}{user_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Ошибка запроса: {response.status}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None        