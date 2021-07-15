from aiogram.dispatcher.filters.state import StatesGroup, State


class PostCreation(StatesGroup):
    WAITING_FOR_POST_TYPE = State()
    WAITING_FOR_DATE = State()
    WAITING_FOR_TIME = State()
    WAITING_FOR_TEXT = State()
    WAITING_FOR_ACTION = State()
    WAITING_FOR_IMAGE = State()
    WAITING_FOR_VIDEO = State()
    WAITING_FOR_GIF = State()