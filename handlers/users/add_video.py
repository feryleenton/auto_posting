from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from keyboards.inline import post_creation_media_actions
from loader import dp, bot

import logging


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
from states import PostCreation


@dp.message_handler(state=PostCreation.WAITING_FOR_VIDEO, content_types=ContentType.VIDEO)
async def bot_echo(message: types.Message, state: FSMContext):

    # обрабатываем неизвестную ошибку
    try:

        state_data = await state.get_data()

        # Если это первое изображение - нужно создать список, иначе - получить его из state_data[]
        try:
            post_videos = state_data['post_videos']
            logging.info('Обработана загрузка еще одного видео в текущий пост')
        except KeyError:
            logging.info('Обработана загрузка первого видео в текущий пост')
            post_videos = []

        # получаем данные загруженного фото
        video_id = message.video.file_id
        video_info = await bot.get_file(video_id)

        # добавляем путь новго изобрадения в state_data[]
        post_videos.append('/media/' + str(video_info.file_id) + '.mp4')
        await state.update_data(post_videos=post_videos)

        # сохраняем новое видео в папку media/
        await bot.download_file(video_info.file_path, 'auto_posting/media/' + str(video_info.file_id) + '.mp4')

        # ждем следующее действие от пользователя
        await PostCreation.WAITING_FOR_ACTION.set()
        await message.answer('Видео загружено !', reply_markup=post_creation_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Видео не загружено, произошла не известная ошибка !', reply_markup=post_creation_media_actions)


@dp.message_handler(state=PostCreation.WAITING_FOR_VIDEO)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте видео !')


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_ACTION, text='add_video')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте видео: ')
    await PostCreation.WAITING_FOR_VIDEO.set()