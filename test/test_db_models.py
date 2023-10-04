import unittest
from mongomock_motor import AsyncMongoMockClient
from Bot.database.models import BaseModel, UserInfo, BotLogInfo, Feedback


class TestDataBaseModel(unittest.TestCase):

    def setUp(self) -> None:
        self.obj = BaseModel("coll")
        self.obj.attr = 1

    def test_db_model(self):
        self.assertEqual(self.obj._get_mongo_dict(), {"attr": 1})


class TestUserInfoModel(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        # Меняем базу данных для базового класса и передаем ей мок
        BaseModel.DB = AsyncMongoMockClient()["test_db"]
        self.obj = UserInfo(100)
        self.obj.add_place("test_place", (100, 100))
        await self.obj.save()

    async def test_01_get_places_names(self):
        # Место было, проверяем метод, который возвращает список мест
        user = await UserInfo.get_user(100)
        self.assertEqual(user.get_places_names(), ["test_place"])

    async def test_02_del_place(self):
        user = await UserInfo.get_user(100)
        user.del_place("test_place")
        await user.save()
        user_new = await UserInfo.get_user(100)
        self.assertEqual(user_new.get_places_names(), [])

    async def test_03_add_place(self):
        # Проверяем добавление мест
        user = await UserInfo.get_user(100)
        user.add_place("test_place_2", (100, 10))
        await user.save()

        user_new = await UserInfo.get_user(100)
        self.assertEqual(user_new.get_places_names(), ["test_place", "test_place_2"])

    async def test_04_get_coord(self):
        """
        Проверяем функцию получения координат по месту
        """
        user = await UserInfo.get_user(100)
        self.assertEqual(user.get_place_coord('test_place'), [100, 100])
