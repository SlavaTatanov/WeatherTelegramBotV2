import asyncio

request_counter = {"counter": 0}


async def back_task():
    """
    Заглушка для фоновой задачи
    Логгер, чистильщик кеша
    """
    while True:
        await asyncio.sleep(20)
        print(f"Было {request_counter['counter']} запросов к API")
