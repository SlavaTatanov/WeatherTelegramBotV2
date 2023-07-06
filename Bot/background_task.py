import asyncio
from Bot.Weather.core import req_counter


async def back_task():
    """
    Заглушка для фоновой задачи
    Логгер, чистильщик кеша
    """
    while True:
        await asyncio.sleep(20)
        print(f"Было {req_counter.storage.get('API_REQ')} запросов к API")
