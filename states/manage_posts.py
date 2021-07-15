from aiogram.dispatcher.filters.state import StatesGroup, State


class ManagePosts(StatesGroup):
    MANAGING_POSTS = State()