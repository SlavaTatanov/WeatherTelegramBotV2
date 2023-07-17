from aiogram import types
from Bot.keboards import inline_settings_menu, inline_settings_places, inline_settings_feedback


# /settings
async def settings_menu(message: types.Message):
    """
    Основной хендлер для настроек, возвращает пользователю меню настроек
    """
    user_id = message.from_user.id
    await message.answer("Меню настроек", reply_markup=inline_settings_menu(user_id))


# callback = SETTINGS
async def settings_menu_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text("Меню настроек", reply_markup=inline_settings_menu(user_id))


# callback = SETTING_PLACES
async def settings_places_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text("Избранные места", reply_markup=inline_settings_places(user_id))


# callback = SETTINGS_FEEDBACK
async def settings_feed_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text("Сообщите об ошибке или опишите какой"
                                     " функционал вы бы хотели увидеть в боте",
                                     reply_markup=inline_settings_feedback())
