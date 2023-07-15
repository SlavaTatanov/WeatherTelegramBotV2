from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from os import getenv
from Bot.config import TOKEN, DEVELOPMENT, TEST_TOKEN
import Bot.views.settings as view_settings
import Bot.views.admin as view_admin


def get_token() -> str:
    """
    Определяем какого бота необходимо использовать
    """
    # Смотрим есть ли ключик в переменных среды, если нет то дефолтный
    dev_status = int(getenv("DEVELOPMENT", DEVELOPMENT))
    if dev_status:
        return TEST_TOKEN
    return TOKEN


storage = MemoryStorage()

bot = Bot(get_token())
dp = Dispatcher(bot, storage=storage)

# Регистрация handlers
# -- settings --
dp.register_message_handler(view_settings.settings_menu, commands=["settings"])

# -- admin --
dp.register_callback_query_handler(view_admin.admin_menu, lambda callback: callback.data == "admin-panel")
dp.register_callback_query_handler(view_admin.admin_log_api, lambda callback: callback.data == "api_log")
dp.register_callback_query_handler(view_admin.admin_api_log_5_day, lambda callback: callback.data == "api_log_5_days")
dp.register_callback_query_handler(view_admin.admin_api_log_max, lambda callback: callback.data == "api_log_max")


async def set_commands(disp: Dispatcher):
    await disp.bot.set_my_commands([BotCommand("weather", "Погода")])


# Создаем классы для машины состояний
class WeatherState(StatesGroup):
    weather_time = State()
    weather_type = State()
    weather_place = State()
