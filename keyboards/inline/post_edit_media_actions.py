from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

post_edit_media_actions = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Добавить видео', callback_data='edit_video'),
        InlineKeyboardButton(text='Добавить фото', callback_data='edit_photo'),
        InlineKeyboardButton(text='Добавить гифку', callback_data='edit_gif'),
    ],
    [
        InlineKeyboardButton(text='Далее', callback_data='continue'),
    ]
])