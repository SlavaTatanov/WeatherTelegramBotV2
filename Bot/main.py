from aiogram import executor, types
from Bot import dp
from Bot.Database import MongoConnection


@dp.message_handler(content_types=['text'])
async def send_welcome(message: types.Message):
    if message.text == 'err':
        raise SystemExit
    elif message.text == 'db':
        await message.reply(f"Подключение к БД {MongoConnection}")
    else:
        await message.reply("Привет!")


executor.start_polling(dp, skip_updates=True)
