from aiogram import types
from Bot.keboards import inline_admin_menu, inline_admin_api_log
from Bot.Database.models import BotLogInfo


# callback "admin-panel"
async def admin_menu(callback: types.CallbackQuery):
    """
    Базовое меню администратора.
    Отсюда ходим к логам и другой инфо.
    """
    await callback.message.edit_text("Меню администратора", reply_markup=inline_admin_menu())


# callback "api_log"
async def admin_log_api(callback: types.CallbackQuery):
    """
    Выбираем тип логов запросов к API
    """
    await callback.message.edit_text("Какие логи необходимо получить?", reply_markup=inline_admin_api_log())


# callback "api_log_5_days"
async def admin_api_log_5_day(callback: types.CallbackQuery):
    res = await BotLogInfo.get_5_day_info()
    await callback.message.edit_text(res, reply_markup=inline_admin_api_log())


# callback "api_log_max"
async def admin_api_log_max(callback: types.CallbackQuery):
    res = await BotLogInfo.get_max_api_req()
    await callback.message.edit_text(res, reply_markup=inline_admin_api_log())

