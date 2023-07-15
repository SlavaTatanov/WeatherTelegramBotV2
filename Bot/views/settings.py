from aiogram import types
from Bot.keboards import inline_settings_menu


# /settings
async def settings_menu(message: types.Message):
    """
    Основной хендлер для настроек, возвращает пользователю меню настроек
    """
    user_id = message.from_user.id
    await message.answer("Меню настроек", reply_markup=inline_settings_menu(user_id))
