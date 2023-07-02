from abc import ABC, abstractmethod
from pymongo import MongoClient
from Bot.config import MONGO_USER, MONGO_PWD, MONGO_HOST


class AbstractMongoConnection(ABC):
    """
    Базовый класс для реализации подключения к МонгоДБ
    """
    @staticmethod
    @abstractmethod
    def get_db():
        pass


class LocalMongoConnection(AbstractMongoConnection):
    """
    Класс методом подключения MongoDB
    """
    @staticmethod
    def get_db():
        return MongoClient('mongodb://localhost:27017')


class ServerMongoConnection(AbstractMongoConnection):
    """
    Класс методом подключения MongoDB
    """
    @staticmethod
    def get_db():
        return MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:27017')
