from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

post_creation_media_actions = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить видео', callback_data='add_video'),
        InlineKeyboardButton(text='Добавить фото', callback_data='add_photo'),
        InlineKeyboardButton(text='Добавить гифку', callback_data='add_gif'),
    ],
    [
        InlineKeyboardButton(text='Далее', callback_data='continue'),
    ]
])