from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from os import getenv
from Bot.config import TOKEN, DEVELOPMENT, TEST_TOKEN
import Bot.views.settings as view_settings
import Bot.views.admin as view_admin
from Bot.CALLBACKS import ADMIN_MENU, ADMIN_API_LOG, ADMIN_API_LOG_5, ADMIN_API_LOG_MAX, SETTINGS, \
    SETTINGS_PLACES, SETTINGS_FEEDBACK


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

bot = Bot(get_token(), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

# Регистрация handlers
# -- settings --
dp.register_message_handler(view_settings.settings_menu, commands=["settings"], state="*")
dp.register_callback_query_handler(view_settings.settings_menu_callback,
                                   lambda callback: callback.data == SETTINGS, state="*")
dp.register_callback_query_handler(view_settings.settings_places_menu,
                                   lambda callback: callback.data == SETTINGS_PLACES, state="*")
dp.register_callback_query_handler(view_settings.settings_feed_menu,
                                   lambda callback: callback.data == SETTINGS_FEEDBACK, state="*")

# -- admin --
dp.register_callback_query_handler(view_admin.admin_menu,
                                   lambda callback: callback.data == ADMIN_MENU, state="*")
dp.register_callback_query_handler(view_admin.admin_log_api,
                                   lambda callback: callback.data == ADMIN_API_LOG, state="*")
dp.register_callback_query_handler(view_admin.admin_api_log_5_day,
                                   lambda callback: callback.data == ADMIN_API_LOG_5, state="*")
dp.register_callback_query_handler(view_admin.admin_api_log_max,
                                   lambda callback: callback.data == ADMIN_API_LOG_MAX, state="*")


async def set_commands(disp: Dispatcher):
    await disp.bot.set_my_commands([BotCommand("weather", "Погода"),
                                    BotCommand("settings", "Настройки")])


# Создаем классы для машины состояний
class WeatherState(StatesGroup):
    weather_time = State()
    weather_type = State()
    weather_place = State()
