from Bot.Database import mongo_db
from datetime import date
import re


class BaseModel:
    """
    Базовая модель для взаимодействия с Mongo,
    предоставляет методы:
    save() - сохраняет объект в БД
    При наследовании вызвать метод init и передать в него имя коллекции с которой работает модель.
    """

    def __init__(self, collection):
        self.__collection = collection

    def _get_mongo_dict(self) -> dict:
        """
        Получить словарь который можно сохранять в БД.
        Вставляет только неприватные аттрибуты и не пустые.
        Фильтрует так: if not k.startswith(private_attrs) and v.
        """
        def check(x):
            return bool(re.match(r"_\w+__", x))
        return {k: v for (k, v) in self.__dict__.items() if not check(k) and v}

    async def save(self):
        obj = self._get_mongo_dict()
        await mongo_db[self.__collection].insert_one(obj)


class UserInfo(BaseModel):
    """
    Модель описывающая информацию пользователя.
    Предоставляет интерфейс для взаимодействия с БД

    Создаем объект: obj = UserInfo(2340, {"Место1": (55.33, 55.54)})
    Сохраняем obj.save()

    Получаем объект по id пользователя: UserInfo.get_user(2340)
    Меняем его
    Сохраняем obj.save()
    """

    def __init__(self, user_id: int, places: dict | None = None, in_db: bool = False):
        super().__init__("user_info")
        self._id = user_id
        self.places = places
        # Определяем есть ли этот пользователь в БД
        self.__in_db = in_db

    @classmethod
    def get_user(cls, user_id):
        """
        Запрос пользователя из БД
        """
        query = mongo_db["user_info"].find_one({"_id": user_id})
        return cls(user_id)


class BotLogInfo(BaseModel):
    """
    Класс описывающий логи, запросы к API и другое
    """

    def __init__(self, api_req_counter: int | None = None):
        super().__init__("bot_log_info")
        self.date_log = str(date.today())
        self.api_req = api_req_counter

    @staticmethod
    def _get_info(lim, sort_tag):
        res = mongo_db["bot_log_info"].find().sort(sort_tag, -1).limit(lim)
        return res

    @classmethod
    async def get_5_day_info(cls):
        """
        Возвращает строку с сообщением о логах за последние 5 дней
        """
        req = cls._get_info(5, "date_log")
        res = await cls.create_msg(req)
        return res

    @classmethod
    async def get_max_api_req(cls):
        """
        Дни с максимальным количеством запросов
        """
        req = cls._get_info(5, "api_req")
        res = await cls.create_msg(req)
        return res

    @staticmethod
    async def create_msg(req):
        """
        Метод принимает результат множественного запроса и формирует сообщение
        """
        res = []
        async for it in req:
            res.append(it)
        res_msg = ""
        for it in res:
            res_msg += f"{it['date_log']} -> {it['api_req']}\n"
        return res_msg
