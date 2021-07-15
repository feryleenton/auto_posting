from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from keyboards.inline import post_creation_media_actions
from loader import dp, bot

import logging


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
from states import PostCreation


@dp.message_handler(state=PostCreation.WAITING_FOR_GIF, content_types=ContentType.ANIMATION)
async def bot_echo(message: types.Message, state: FSMContext):

    # обрабатываем неизвестную ошибку
    try:

        state_data = await state.get_data()

        # Если это первое изображение - нужно создать список, иначе - получить его из state_data[]
        try:
            post_gifs = state_data['post_gifs']
            logging.info('Обработана загрузка еще одной гифки в текущий пост')
        except KeyError:
            logging.info('Обработана загрузка первой гифки в текущий пост')
            post_gifs = []

        # получаем данные загруженной гифки
        gif_id = message.animation.file_id
        gif_info = await bot.get_file(gif_id)

        # добавляем путь новой гифки в state_data[]
        post_gifs.append('/media/' + str(gif_info.file_id) + '.mp4')
        await state.update_data(post_gifs=post_gifs)

        # сохраняем новую гифку в папку media/
        await bot.download_file(gif_info.file_path, 'auto_posting/media/' + str(gif_info.file_id) + '.mp4')

        # ждем следующее действие от пользователя
        await PostCreation.WAITING_FOR_ACTION.set()
        await message.answer('Гифка загружена !', reply_markup=post_creation_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Гифка не загружена, произошла не известная ошибка !', reply_markup=post_creation_media_actions)


@dp.message_handler(state=PostCreation.WAITING_FOR_GIF)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте гифку !')


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_ACTION, text='add_gif')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте гифку: ')
    await PostCreation.WAITING_FOR_GIF.set()