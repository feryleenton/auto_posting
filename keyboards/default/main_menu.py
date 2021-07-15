from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton('Добавить в очередь')],
], resize_keyboard=True)