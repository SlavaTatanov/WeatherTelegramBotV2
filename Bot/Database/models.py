from Bot.Database import mongo_db


class BaseModel:
    """
    Базовая модель для взаимодействия с Mongo
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
