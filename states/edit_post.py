from aiogram.dispatcher.filters.state import StatesGroup, State


class EditPost(StatesGroup):
    CHOOSE_ACTION = State()
    EDIT_POST_TEXT = State()
    WAITING_FOR_ACTION = State()
    WAITING_FOR_IMAGE = State()
    WAITING_FOR_VIDEO = State()
    WAITING_FOR_GIF = State()