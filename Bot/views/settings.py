from aiogram import types
from Bot.keboards import inline_settings_menu, inline_settings_places, inline_settings_feedback, inline_places
import Bot
from Bot.utils import state_clean_with_messages, state_save_related_msg


# /settings
async def settings_menu(message: types.Message):
    """
    Основной хендлер для настроек, возвращает пользователю меню настроек
    """
    user_id = message.from_user.id
    await message.answer("Меню настроек", reply_markup=inline_settings_menu(user_id))
    await message.delete()


# callback = SETTINGS
async def settings_menu_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text("Меню настроек", reply_markup=inline_settings_menu(user_id))


# callback = SETTING_PLACES
async def settings_places_menu(callback: types.CallbackQuery):
    # Получаем id пользователя
    user_id = callback.from_user.id
    # Чистим состояние пользователя
    await state_clean_with_messages(user_id, ignor_state_msg='UserPlaces')
    # Отправляем сообщение
    await callback.message.edit_text("Избранные места", reply_markup=inline_settings_places(user_id))


# callback = SETTINGS_FEEDBACK
async def settings_feed_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text("Сообщите об ошибке или опишите какой"
                                     " функционал вы бы хотели увидеть в боте",
                                     reply_markup=inline_settings_feedback())


# callback = SETTINGS_PLC_ADD
async def settings_place_add(callback: types.CallbackQuery):
    # Чистим предыдущие состояния перед установкой своего
    await state_clean_with_messages(callback.from_user.id)
    # Устанавливаем новое состояние
    await Bot.UserPlaces.places_add.set()
    msg = await callback.message.edit_text("Введите название места", reply_markup=inline_places())
    state = Bot.dp.current_state(user=callback.from_user.id)
    # Запоминаем связанное с состоянием сообщение
    await state_save_related_msg(state, msg)
