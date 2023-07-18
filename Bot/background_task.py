import asyncio
from Bot.Weather.core import req_counter
from Bot.Weather.core import Weather
from Bot.Database.models import BotLogInfo
from datetime import datetime


async def back_task():
    """
    Каждый час чистим кеш от запросов к апи, в конце дня перекидываем счетчик за сутки в mongo
    """
    while True:
        await asyncio.sleep(3600)
        Weather.clean_api_cache()
        now = datetime.now()
        if now.hour == 23:
            counter = req_counter.storage.get('API_REQ')
            if counter:
                obj = BotLogInfo(counter)
            else:
                obj = BotLogInfo(0)
            await obj.save()
            req_counter.storage.pop('API_REQ')
