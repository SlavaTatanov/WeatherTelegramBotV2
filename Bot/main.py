from aiogram import types
import asyncio
from Bot import dp, set_commands
from Bot.CALLBACKS import EXIT
from Bot.background_task import back_task
from Bot.Database import create_indexes


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " в данный момент доступны только короткие прогнозы погоды. Часть функций может не работать"
    await message.answer(answer_for_user)


@dp.message_handler(commands=['help'], state="*")
async def help_command(message: types.Message):
    answer_for_user = ("Данный бот предоставляет прогноз погоды.\n\n"
                       "/weather - Для того чтобы узнать прогноз погоды.\n\n"
                       "/settings - Для того чтобы воспользоваться настройками. Можно добавить избранные места"
                       ", а так же поделится обратной связью с разработчиками.")
    await message.answer(answer_for_user)


@dp.callback_query_handler(lambda callback: callback.data == EXIT, state="*")
async def exit_menu(callback: types.CallbackQuery):
    await callback.message.delete()


@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    pass


# Запускаем бота и фоновую задачу
async def main():
    # Создаем индексы, устанавливаем команды бота
    await create_indexes()
    await set_commands(dp)
    # Запускаем фоновую задачу
    asyncio.create_task(back_task())
    # Запускаем бота
    await dp.start_polling()

# Получаем loop
loop = asyncio.new_event_loop()
# Запускаем
loop.run_until_complete(main())
