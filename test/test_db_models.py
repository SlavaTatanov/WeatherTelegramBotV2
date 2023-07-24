import unittest
from Bot.Database.models import BaseModel
from Bot import *


class TestDataBaseModel(unittest.TestCase):

    def setUp(self) -> None:
        self.obj = BaseModel("coll")
        self.obj.attr = 1

    def test_db_model(self):
        self.assertEqual(self.obj._get_mongo_dict(), {"attr": 1})
