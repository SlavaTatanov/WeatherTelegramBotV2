from aiogram import types
import asyncio
from Bot import dp, set_commands
from Bot.callbacks import EXIT
from Bot.background_task import back_task
from Bot.database import create_indexes
from Bot.geocoder.geocoder import get_place_coord


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Я могу подсказать вам прогноз погоды! Если вам нужна помощь нажмите\n\n" \
                      "↠ /help ↞"
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
    res = await get_place_coord("Челябинскыая область, увильды")
    if res:
        msg = await message.answer_location(res['lat'], res['lon'])
        await msg.reply(res['place'])
    else:
        await message.answer("Что то пошло не так")


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
