from aiogram import types
from aiogram.dispatcher.storage import FSMContext

import Bot
from Bot.keboards import inline_admin_menu, inline_admin_api_log, inline_admin_feedback_type
from Bot.database.models import BotLogInfo, Feedback
from Bot import keboards
from Bot.utils import state_clean_with_messages, check_state


# callback "admin-panel"
async def admin_menu(callback: types.CallbackQuery):
    """
    Базовое меню администратора.
    Отсюда ходим к логам и другой инфо.
    """
    await state_clean_with_messages(callback.from_user.id)
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


# callback "admin_feedback"
async def admin_feedback(callback: types.CallbackQuery):
    """
    Представление реализующее выбор типа фидбека (пожелания, баги)
    """
    await state_clean_with_messages(callback.from_user.id)
    await callback.message.edit_text("Выберете тип", reply_markup=inline_admin_feedback_type())


# callback "admin_feedback_feed"
async def admin_feedback_feed_choice(callback: types.CallbackQuery):
    """
    Представление реализует запрос пожеланий пользователей
    """
    await callback.message.edit_text("Запрос пожеланий пользователей")
    await Feedback.get_feed("feature")


# callback "admin_feedback_bug"
async def admin_feedback_bug_choice(callback: types.CallbackQuery, state: FSMContext):
    """
    Представление реализует запрос багов
    """

    async def save_page_info(state_inf, prev_page_inf, next_page_inf, curr_page_inf):
        """
        Функция сохраняет информацию о страницах в текущее состояние
        """
        async with state_inf.proxy() as data_inf:
            data_inf["prev_page"] = prev_page_inf
            data_inf["next_page"] = next_page_inf
            data_inf["curr_page"] = curr_page_inf

    current_state = await state.get_state()
    if current_state:
        if await check_state(current_state, Bot.FeedPages):
            async with state.proxy() as data:
                prev_page = data["prev_page"]
                next_page = data["next_page"]
                feed_list = data["feed_list"]
                pages = data["pages"]
                curr_page = data["curr_page"]
                if "next" in callback.data:
                    # Если пришло next в callback
                    curr_page += 1
                    next_page += 1
                    if not prev_page:
                        prev_page = 0
                    prev_page += 1
                    if next_page >= pages:
                        next_page = None
                    await save_page_info(state, prev_page, next_page, curr_page)
                elif "prev" in callback.data:
                    # Если perv в callback
                    curr_page -= 1
                    if next_page:
                        next_page -= 1
                    else:
                        next_page = pages - 1
                    if prev_page <= 1:
                        prev_page = None
                    await save_page_info(state, prev_page, next_page, curr_page)
                await callback.message.edit_text("Запрос багов добавленных пользователями",
                                                 reply_markup=keboards.inline_feed_list(feed_list[curr_page],
                                                                                        prev_page=prev_page,
                                                                                        next_page=next_page))

    else:
        feed_list = await Feedback.get_feed("bug")
        if len(feed_list) > 1:
            # Ситуация когда страниц несколько и пока нет состояния.
            # Устанавливаем состояние.
            await Bot.FeedPages.page_counter.set()
            # Меняем state на только что установленный
            state = Bot.dp.current_state(user=callback.from_user.id)
            # Меняем страницы с дефолтных
            prev_page = None
            next_page = 1
            async with state.proxy() as data:
                data["prev_page"] = prev_page
                data["next_page"] = next_page
                data["feed_list"] = feed_list
                data["pages"] = len(feed_list)
                data["curr_page"] = 0
            await callback.message.edit_text("Запрос багов добавленных пользователями",
                                             reply_markup=keboards.inline_feed_list(feed_list[0],
                                                                                    next_page=next_page))


