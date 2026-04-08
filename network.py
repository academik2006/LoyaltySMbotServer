import aiohttp
import json


PARTNER_ID = "f0bab507-02b4-4199-aaec-da6d0348e516"
HEADERS = {
    "x-partner-id": PARTNER_ID,
    #"Content-Type": "application/json"
}
retail_network_id = "A79C5050-1EE7-11EB-9B6E-05B5FC40DF2A"
SOURCE = "PARTNER"

async def send_verification_code(phone: str):

    url = "https://venus-api-customers.snet.su/v1/sendCode/partner"
    
    payload = {
        "RetailNetworkId": retail_network_id,
        "Recipient": phone,        
    }

    return await safe_request(url, payload)    

async def validate_sms_code(phone: str, code: int) -> dict:
 
    url = "https://venus-api-customers.snet.su/v1/validateCode"
    # Формирование тела запроса
    payload = {
        "RetailNetworkId": retail_network_id,
        "Recipient": phone,
        "Code": code,
        "Source": "PARTNER"
    }

    return await safe_request(url, payload) 
         

async def get_user_info(idloyaty_id: str) -> dict:
    
    base_url = "https://venus-api-customers.snet.su/v1/get/"
    url = f"{base_url}{idloyaty_id}"
    
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Если статус 200, пытаемся распарсить JSON
                try:
                    data = await response.json()
                    return {
                        "success": True,
                        "status": response.status,
                        "data": data
                    }
                except aiohttp.ContentTypeError:
                    # Если это не JSON (например, просто текст или пустой ответ)
                    text = await response.text()
                    return {
                        "success": True,
                        "status": response.status,
                        "data": text or "Пустой ответ (200 OK)"
                    }
            else:
                # 2. Если статус НЕ 200, возвращаем текст ошибки
                # Иногда при ошибках (4xx, 5xx) сервер присылает текст с описанием
                error_text = await response.text()
                return {
                    "success": False,
                    "status": response.status,
                    "error": error_text or f"Ошибка {response.status} без описания"
                }

                


async def safe_request(url: str, payload: dict) -> dict:
    """
    Выполняет POST-запрос и возвращает результат в удобном формате.
    Возвращает словарь с ключами 'success', 'status', 'data'.
    """
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(url, json=payload) as response:
            # 1. Проверяем статус
            if response.status == 200:
                # Если статус 200, пытаемся распарсить JSON
                try:
                    data = await response.json()
                    return {
                        "success": True,
                        "status": response.status,
                        "data": data
                    }
                except aiohttp.ContentTypeError:
                    # Если это не JSON (например, просто текст или пустой ответ)
                    text = await response.text()
                    return {
                        "success": True,
                        "status": response.status,
                        "data": text or "Пустой ответ (200 OK)"
                    }
            else:
                # 2. Если статус НЕ 200, возвращаем текст ошибки
                # Иногда при ошибках (4xx, 5xx) сервер присылает текст с описанием
                error_text = await response.text()
                return {
                    "success": False,
                    "status": response.status,
                    "error": error_text or f"Ошибка {response.status} без описания"
                }
            
