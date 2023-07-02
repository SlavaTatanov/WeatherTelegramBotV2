from Bot.Database import MongoConnection


class UserInfo(MongoConnection):
    """
    Модель описывающая информацию пользователя.
    Предоставляет интерфейс для взаимодействия с БД

    Создаем объект: obj = UserInfo(2340, {"Место1": (55.33, 55.54)})
    Сохраняем obj.save()

    Получаем объект по id пользователя: UserInfo.get_user(2340)
    Меняем его
    Сохраняем obj.save()
    """
    def __init__(self, user_id: int, places: dict | None = None):
        self._id = user_id
        self.places = places
        self.__connection = self.get_db()

    @classmethod
    def get_user(cls, user_id):
        """
        Запрос пользователя из БД
        """
        return cls(user_id)

    def _get_mongo_dict(self) -> dict:
        """
        Получить словарь который можно сохранять в БД.
        Вставляет только неприватные аттрибуты и не пустые.
        Фильтрует так: if not k.startswith(private_attrs) and v.
        """
        private_attrs = f"_{self.__class__.__name__}__"
        return {k: v for (k, v) in self.__dict__.items() if not k.startswith(private_attrs) and v}
