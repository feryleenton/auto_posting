from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from keyboards.inline import post_creation_media_actions
from loader import dp, bot

import logging


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
from states import PostCreation


@dp.message_handler(state=PostCreation.WAITING_FOR_IMAGE, content_types=ContentType.PHOTO)
async def bot_echo(message: types.Message, state: FSMContext):

    # обрабатываем неизвестную ошибку
    try:

        state_data = await state.get_data()

        # Если это первое изображение - нужно создать список, иначе - получить его из state_data[]
        try:
            post_images = state_data['post_images']
            logging.info('Обработана загрузка еще одного фото в текущий пост')
        except KeyError:
            logging.info('Обработана загрузка первого фото в текущий пост')
            post_images = []

        # получаем данные загруженного фото
        photo_id = message.photo[-1].file_id
        photo_info = await bot.get_file(photo_id)

        # добавляем путь новго изобрадения в state_data[]
        post_images.append(f'/media/{photo_info.file_id}.jpg')
        await state.update_data(post_images=post_images)

        # сохраняем новое изображение в папку media/
        await message.photo[-1].download('auto_posting/media/' + str(photo_info.file_id) + '.jpg')

        # ждем следующее действие от пользователя
        await PostCreation.WAITING_FOR_ACTION.set()
        await message.answer('Фото загружено !', reply_markup=post_creation_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Фото не загружено, произошла не известная ошибка !', reply_markup=post_creation_media_actions)


@dp.message_handler(state=PostCreation.WAITING_FOR_IMAGE)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте изображение !')


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_ACTION, text='add_photo')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте изображение: ')
    await PostCreation.WAITING_FOR_IMAGE.set()