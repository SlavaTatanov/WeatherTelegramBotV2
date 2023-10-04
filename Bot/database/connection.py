from motor.motor_asyncio import AsyncIOMotorClient
from Bot.config import MONGO_USER, MONGO_PWD, MONGO_HOST


def get_local_mongo_client():
    """
    Создание локального подключения
    """
    return AsyncIOMotorClient('mongodb://localhost:27017/weather_bot')


def get_server_mongo_client():
    return AsyncIOMotorClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:27017/weather_bot')
