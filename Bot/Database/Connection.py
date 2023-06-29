from abc import ABC, abstractmethod
from pymongo import MongoClient


class AbstractMongoConnection(ABC):
    """
    Базовый класс для реализации подключения к МонгоДБ
    """
    @staticmethod
    @abstractmethod
    def get_db():
        pass


class LocalMongoConnection(AbstractMongoConnection):
    @staticmethod
    def get_db():
        return MongoClient('mongodb://localhost:27017')
