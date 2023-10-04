from Bot.database import mongo_db
from datetime import date
import re


class BaseModel:
    """
    Базовая модель для взаимодействия с Mongo,
    предоставляет методы:
    save() - сохраняет объект в БД
    При наследовании вызвать метод init и передать в него имя коллекции с которой работает модель.
    """

    DB = mongo_db

    def __init__(self, collection):
        self.__collection = collection

    def _get_mongo_dict(self) -> dict:
        """
        Получить словарь который можно сохранять в БД.
        Вставляет только неприватные аттрибуты и не пустые.
        Фильтрует так: if not k.startswith(private_attrs) and v.
        """
        def check(x):
            return bool(re.match(r"^_\w+__", x))
        return {k: v for (k, v) in self.__dict__.items() if not check(k) and v}

    async def save(self):
        obj = self._get_mongo_dict()
        await self.DB[self.__collection].insert_one(obj)


class UserInfo(BaseModel):
    """
    Модель описывающая информацию пользователя.
    Предоставляет интерфейс для взаимодействия с БД

    Создаем объект: obj = UserInfo(2340, {"Место1": (55.33, 55.54)})
    Сохраняем obj.save()

    Получаем объект по id пользователя: UserInfo.get_user(2340)
    Меняем его.
    Сохраняем obj.save().
    """

    def __init__(self, user_id: int, places: dict | None = None, in_db: bool = False):
        super().__init__("user_info")
        self._id = user_id
        self._places = places
        # Определяем есть ли этот пользователь в БД
        self.__in_db = in_db

    @classmethod
    async def get_user(cls, user_id) -> 'UserInfo':
        """
        Запрос пользователя из БД
        """
        query = await BaseModel.DB["user_info"].find_one({"_id": user_id})
        if not query:
            return cls(user_id)
        places = query.get("_places", None)
        return cls(user_id, places, in_db=True)

    def add_place(self, name, coord):
        """
        Добавить место в профиль пользователя
        """
        if not self._places:
            self._places = {}
        self._places[name] = coord

    def del_place(self, name):
        """
        Удалить место
        """
        if self._places:
            if name in self._places:
                del self._places[name]

    async def save(self):
        """
        Метод сохранения или обновления данных в дб
        """

        # Если объекта еще нет в базе данных, то просто сохраняем
        if not self.__in_db:
            await super().save()
            return
        # Если объект есть, то просто меняем его на новый
        obj = super()._get_mongo_dict()
        await self.DB["user_info"].replace_one({"_id": self._id}, obj)

    def get_places_names(self) -> list:
        """
        Получить список мест
        """
        if self._places:
            return [k for k, v in self._places.items()]
        else:
            return []

    def get_place_coord(self, place_name):
        """
        Получить координаты места
        """
        return self._places[place_name]


class BotLogInfo(BaseModel):
    """
    Класс описывающий логи, запросы к API и другое
    """

    def __init__(self, api_req_counter: int | None = None):
        super().__init__("bot_log_info")
        self.date_log = str(date.today())
        self.api_req = str(api_req_counter)

    @classmethod
    def _get_info(cls, lim, sort_tag):
        """
        Функция, которая составляет запрос к базе данных MongoDB.
        В нем есть агрегация запроса, в которой строковые значения парсятся в числа.
        """
        pipeline = [{
            '$project': {
                'api_req_number': {
                    '$function': {
                        'body': 'function(str) {return parseInt(str);}',
                        'args': ['$api_req'],
                        'lang': 'js'
                    }
                },
                'date_log': 1,
                'api_req': 1,
            }
        }, {'$sort': {sort_tag: -1}},
            {'$limit': lim}
        ]
        res = cls.DB["bot_log_info"].aggregate(pipeline)
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
        req = cls._get_info(5, 'api_req_number')
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


class Feedback(BaseModel):
    """
    Модель, описывающая обратную связь от пользователей
    """
    def __init__(self, user_id: int, msg: str, bug: bool = False) -> None:
        super().__init__("feedback")
        self.user = user_id
        if bug:
            self.feed_type = "bug"
        else:
            self.feed_type = "feature"
        self.date = str(date.today())
        self.msg = msg
