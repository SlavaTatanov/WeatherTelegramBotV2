from aiogram import types
from Bot.keboards import (inline_settings_menu, inline_settings_places, inline_settings_feedback,
                          inline_places, inline_places_del, inline_places_del_confirm, inline_feedback_cancel,
                          inline_find_places, inline_place_confirm)
import Bot
from Bot.utils import state_clean_with_messages, state_save_related_msg
from aiogram.dispatcher import FSMContext
from Bot.database.models import UserInfo, Feedback
from Bot.geocoder.geocoder import get_place_coord


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
    await state_clean_with_messages(user_id)
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


# message - text, state - UserPlaces.places_add
async def settings_place_add_coord(message: types.Message, state: FSMContext):
    await message.answer(f'Отправьте гео-позицию места для "{message.text}" либо нажмите кнопку найти место',
                         reply_markup=inline_find_places())
    await Bot.UserPlaces.places_add_coord.set()
    async with state.proxy() as data:
        data['place_name'] = message.text


# callback - SETTINGS_PLC_FIND
async def settings_place_find(callback: types.CallbackQuery, state: FSMContext):
    """
    Запрос подтверждения, что выбранное место верное.
    """
    async with state.proxy() as data:
        place_name = data['place_name']
        place_info = await get_place_coord(place_name)
        if place_info:
            lat, lon, place_full_name = place_info['lat'], place_info['lon'], place_info['place']
            msg = await Bot.bot.send_location(callback.from_user.id, lat, lon)
            # Запоминаем координаты
            data['lat'], data['lon'] = lat, lon
            await msg.reply(f"{place_full_name}\nЭто верное место?", reply_markup=inline_place_confirm())
            await Bot.UserPlaces.place_confirm.set()
        else:
            await callback.message.answer("Место не найдено, введите его заново", reply_markup=inline_places())
            await callback.message.delete()
            await Bot.UserPlaces.places_add.set()


# callback - SETTINGS_PLC_RIGHT, state - UserPlaces.place_confirm
async def settings_place_confirm(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    async with state.proxy() as data:
        lat, lon, place_name = data['lat'], data['lon'], data['place_name']
        # Добавляем место
        user_info = await UserInfo.get_user(user_id)
        user_info.add_place(place_name, (lat, lon))
        await user_info.save()
        await state_clean_with_messages(user_id)
        await callback.message.answer(f"Место {place_name} добавлено")


# message - location, state - UserPlaces.places_add_coord
async def settings_place_add_final(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        place_name = data['place_name']
        coord = (message.location.latitude, message.location.longitude)
        user_id = message.from_user.id

        # Берем инфу для пользователя, добавляем место, сохраняем
        user_info = await UserInfo.get_user(user_id)
        user_info.add_place(place_name, coord)
        await user_info.save()
        await message.answer(f'Место "{place_name}" успешно добавлено!')
    await state_clean_with_messages(message.from_user.id)


# callback = SETTINGS_PLC_DEL
async def settings_place_del(callback: types.CallbackQuery, state: FSMContext):
    # Чистим предыдущие состояния перед установкой своего
    await state_clean_with_messages(callback.from_user.id)
    # Устанавливаем новое состояние
    await Bot.UserPlaces.place_del.set()
    # Получаем информацию для юзера из БД и берем его места для клавиатуры
    user_info = await UserInfo.get_user(callback.from_user.id)
    places_list = user_info.get_places_names()
    keyboard = inline_places_del(places_list)
    msg = await callback.message.edit_text("Выберете место для удаления",
                                           reply_markup=keyboard)
    # Запоминаем связанное с состоянием сообщение
    await state_save_related_msg(state, msg)


# callback - text, state - UserPlaces.places_del
async def settings_place_del_confirm(callback: types.CallbackQuery, state: FSMContext):
    place = callback.data
    keyboard = inline_places_del_confirm()
    async with state.proxy() as data:
        data['place_name_del'] = place
    await callback.message.edit_text(f"Вы точно хотите удалить {place}?", reply_markup=keyboard)
    await Bot.UserPlaces.place_del_name.set()


# callback - SETTINGS_PLC_DEL_CONFIRM, state - UserPlaces.place_del_name
async def settings_place_del_final(callback: types.CallbackQuery, state: FSMContext):
    user_info = await UserInfo.get_user(callback.from_user.id)
    async with state.proxy() as data:
        place = data['place_name_del']
        user_info.del_place(place)
        await user_info.save()
        await Bot.bot.send_message(callback.from_user.id, f"{place} успешно удалено!")
    await state_clean_with_messages(callback.from_user.id)


# callback - SETTINGS_FEED_BAG, state - all
async def feedback_bag(callback: types.CallbackQuery):
    await Bot.Feedback.bug.set()
    await callback.message.edit_text("Опишите ошибку", reply_markup=inline_feedback_cancel())


# callback - SETTINGS_FEED_FEATURE, state - all
async def feedback_feature(callback: types.CallbackQuery):
    await Bot.Feedback.feature.set()
    await callback.message.edit_text("Опишите какой функционал вы бы еще хотели увидеть в боте",
                                     reply_markup=inline_feedback_cancel())


# message - text, state - Feedback.feature
async def feedback_text(message: types.Message, state: FSMContext):
    """
    Обратная связь от пользователя, принимаем сообщение о пожелании и сохраняем его
    """
    await state.finish()
    user_id = message.from_user.id
    feed = Feedback(user_id, message.text)
    await feed.save()
    await message.answer("Пожелание добавлено")


# message - text, state - Feedback.bug
async def bug_text(message: types.Message, state: FSMContext):
    """
    Обратная связь от пользователя, принимаем сообщение об ошибке и сохраняем его
    """
    await state.finish()
    user_id = message.from_user.id
    feed = Feedback(user_id, message.text, bug=True)
    await feed.save()
    await message.reply("Сообщение об ошибке добавлено, спасибо за обратную связь!")
