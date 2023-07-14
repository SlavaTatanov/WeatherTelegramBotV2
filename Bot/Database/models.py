from Bot.Database import mongo_db
from datetime import date


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
        private_attrs = f"_{self.__class__.__name__}__"
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith(private_attrs) and v}

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
    def __init__(self, api_req_counter: int):
        super().__init__("bot_log_info")
        self.date_log = str(date.today())
        self.api_req = api_req_counter

    def _get_info(self):
        pass

    def get_5_day_info(self):
        pass
