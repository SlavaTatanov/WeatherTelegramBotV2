from os import getenv
from Bot.Database.Connection import LocalMongoConnection, ServerMongoConnection
from Bot.config import DEFAULT_LOCAL_DB


def get_conn():
    """
    Функция диспетчер которая предоставит нужный класс реализующий подключение к БД
    в зависимости от статуса запускаемой программы
    """
    # Ожидаем 1 или 0, переменная среды приходит str, поэтому приводим к int
    local_mongo = int(getenv("LOCAL_MONGO", DEFAULT_LOCAL_DB))
    if local_mongo:
        return LocalMongoConnection
    return ServerMongoConnection


# Класс, который реализует метод подключения к БД, в зависимости от статуса (локально, сервер)
MongoConnection = get_conn()
