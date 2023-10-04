from os import getenv
from Bot.database.connection import get_local_mongo_client, get_server_mongo_client
from Bot.config import DEFAULT_LOCAL_DB


def get_client():
    """
    Функция диспетчер которая предоставит нужный класс реализующий подключение к БД
    в зависимости от статуса запускаемой программы
    """
    # Ожидаем 1 или 0, переменная среды приходит str, поэтому приводим к int
    local_mongo = int(getenv("LOCAL_MONGO", DEFAULT_LOCAL_DB))
    if local_mongo:
        return get_local_mongo_client()
    return get_server_mongo_client()


# Класс, который реализует метод подключения к БД, в зависимости от статуса (локально, сервер)
mongo_client = get_client()
mongo_db = mongo_client.get_database()


# Индексы
async def create_indexes():
    await mongo_db["bot_log_info"].create_index([("date_log", -1)])
