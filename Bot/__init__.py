from aiogram import Bot, Dispatcher
from os import getenv
from Bot.config import TOKEN, DEVELOPMENT, TEST_TOKEN


def get_token() -> str:
    """
    Определяем какого бота необходимо использовать
    """
    # Смотрим есть ли ключик в переменных среды, если нет то дефолтный
    dev_status = int(getenv("DEVELOPMENT", DEVELOPMENT))
    if dev_status:
        return TEST_TOKEN
    return TOKEN


bot = Bot(get_token())
dp = Dispatcher(bot)
