from datetime import date
from aiogram.dispatcher import FSMContext
from aiogram import types
import Bot
from aiogram.utils.exceptions import MessageToDeleteNotFound


def req_counter(key):
    """
    Счетчик запросов к API
    Если функция до этого закеширована то счетчик не меняется,
    так как нет запуска функции
    """
    req_counter.storage = {}

    def req_counter_dec(fun):
        async def wrapper(*args, **kwargs):
            counter = req_counter.storage.get(key, 0)
            counter += 1
            req_counter.storage[key] = counter
            return await fun(*args, **kwargs)

        return wrapper

    return req_counter_dec


def is_sunday(day: date):
    year, week, _ = day.isocalendar()
    return day == date.fromisocalendar(year, week, 7)


async def state_clean_with_messages(user_id, ignor_state_msg: str = 'NotIgnorState'):
    """
    Функция очищающее состояние пользователя и удаляющая связанные с ним сообщения
    """
    state = Bot.dp.current_state(user=user_id)
    user_state = await state.get_state()
    if user_state:
        if ignor_state_msg not in user_state:
            user_data = await state.get_data()
            if 'msg' in user_data:
                try:
                    await user_data['msg'].delete()
                except MessageToDeleteNotFound:
                    pass
        await state.reset_state(with_data=True)


async def state_save_related_msg(state: FSMContext, msg: types.Message):
    async with state.proxy() as data:
        # Запоминаем сообщение, потом удалим
        data["msg"] = msg
