from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

post_types = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Единоразовый', callback_data='once'),
        InlineKeyboardButton(text='Ежидневный', callback_data='repeat'),
    ]
])