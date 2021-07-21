import datetime
import logging
import os
import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType

from keyboards.default import main_menu
from keyboards.inline import manage_posts, posts_callback, edit_post_text, post_edit_media_actions, edit_post_callback
from keyboards.inline.callback_datas import edit_post_media
from loader import dp, bot, db

from crontab import CronTab

from states import ManagePosts, EditPost
from utils.db_api.funcs import get_post_by_client_id, get_related_images, get_related_gifs, get_related_videos, \
    get_post, delete_img, delete_video, delete_gif, delete_post, get_schedule_by_id, create_video, create_gif, create_image


@dp.callback_query_handler(manage_posts.filter(), state=None)
async def bot_echo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()

    post = await get_post(callback_data.get('post_id'))

    # удаляем такску из cron

    cron = CronTab(user=True)
    cron.remove_all(comment=str(post.pk))
    cron.write()

    # получаем пренадлежащие к посту медиа
    images = await get_related_images(post.pk)
    gifs = await get_related_gifs(post.pk)
    videos = await get_related_videos(post.pk)

    for image in images:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(image.image))
        await delete_img(image.pk)

    for video in videos:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(video.video))
        await delete_video(video.pk)

    for gif in gifs:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(gif.gif))
        await delete_gif(gif.pk)

    await delete_post(post.pk)

    await call.message.edit_text('Пост удален')
    await call.answer('Пост удален')

    posts = await get_post_by_client_id(call.message.chat.id)

    if len(posts) == 0:
        await call.message.answer('У вас 0 постов в очереди на данный момент !', reply_markup=main_menu)
    else:
        markup_btns = []

        for post in posts:
            markup_btns.append(types.InlineKeyboardButton(text='#' + str(post.pk) + ' ' + str(post.text) + '',
                                                          callback_data=posts_callback.new(
                                                              post_id=post.pk)))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*markup_btns)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='cancel'))

        await call.message.answer('Постов в очереди на публикацию ' + str(len(posts)), reply_markup=markup)


@dp.callback_query_handler(text='cancel', state=None)
async def bot_echo(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()


@dp.callback_query_handler(text='back', state='*')
async def bot_echo(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    await call.message.delete()

    posts = await get_post_by_client_id(call.message.chat.id)

    if len(posts) == 0:
        await call.message.answer('У вас 0 постов в очереди на данный момент !', reply_markup=main_menu)
    else:
        markup_btns = []

        for post in posts:
            markup_btns.append(types.InlineKeyboardButton(text='#' + str(post.pk) + ' ' + str(post.text) + '',
                                                          callback_data=posts_callback.new(
                                                              post_id=post.pk)))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*markup_btns)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='cancel'))

        await call.message.answer('Постов в очереди на публикацию ' + str(len(posts)), reply_markup=markup)


@dp.callback_query_handler(posts_callback.filter(), state=None)
async def bot_echo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.delete()
    post_id = callback_data.get('post_id')
    post = await get_post(post_id)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text='Редактировать', callback_data=edit_post_callback.new(post_id=post.pk)))
    markup.add(types.InlineKeyboardButton(text='Удалить', callback_data=manage_posts.new(post_id=post.pk)))
    markup.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))

    await call.message.answer('<b>Управление обьявлением #' + str(post.pk) + '</b>\n\n' + str(post.text) + '\n\n'
                                                                                                           'Статус: ожидает публикации',
                              reply_markup=markup)


@dp.message_handler(state=None, text='/posts')
async def bot_echo(message: types.Message):
    posts = await get_post_by_client_id(message.chat.id)

    if len(posts) == 0:
        await message.answer('У вас 0 постов в очереди на данный момент !', reply_markup=main_menu)
    else:
        markup_btns = []

        for post in posts:
            markup_btns.append(types.InlineKeyboardButton(text='#' + str(post.pk) + ' ' + str(post.text) + '',
                                                          callback_data=posts_callback.new(
                                                              post_id=post.pk)))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*markup_btns)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='cancel'))

        await message.answer('Постов в очереди на публикацию ' + str(len(posts)), reply_markup=markup)


@dp.callback_query_handler(edit_post_callback.filter(), state=None)
async def bot_echo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    post_id = callback_data.get('post_id')
    post = await get_post(post_id)

    await state.update_data(post_id=post.pk)

    await call.message.delete()

    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(text='Редактировать текст', callback_data=edit_post_text.new(post_id=post.pk)))
    markup.add(types.InlineKeyboardButton(text='Редактировать медиа', callback_data=edit_post_media.new(post_id=post.pk)))
    markup.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))

    await call.message.answer('<b>Управление обьявлением #' + str(post.pk) + '</b>\n\n' + str(post.text) + '\n\n'
                                                                                                           'Статус: ожидает публикации \n\n'
                                                                                                           'Выберете действие: ',
                              reply_markup=markup)
    await EditPost.CHOOSE_ACTION.set()


@dp.callback_query_handler(edit_post_text.filter(), state=EditPost.CHOOSE_ACTION)
async def bot_echo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Введите новый текст поста: ')

    await EditPost.EDIT_POST_TEXT.set()


@dp.message_handler(state=EditPost.EDIT_POST_TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    post_text = message.text
    state_data = await state.get_data()
    post_id = state_data['post_id']
    post = await get_post(int(post_id))

    post.text = message.text
    await post.save()

    await state.reset_state()

    posts = await get_post_by_client_id(message.chat.id)

    if len(posts) == 0:
        await message.answer('У вас 0 постов в очереди на данный момент !', reply_markup=main_menu)
    else:
        markup_btns = []

        for post in posts:
            markup_btns.append(types.InlineKeyboardButton(text='#' + str(post.pk) + ' ' + str(post.text) + '',
                                                          callback_data=posts_callback.new(
                                                              post_id=post.pk)))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*markup_btns)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='cancel'))

        await message.answer('Постов в очереди на публикацию ' + str(len(posts)), reply_markup=markup)


@dp.callback_query_handler(edit_post_media.filter(), state=EditPost.CHOOSE_ACTION)
async def bot_echo(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.delete()

    state_data = await state.get_data()
    post_id = state_data['post_id']
    post = await get_post(int(post_id))

    await EditPost.WAITING_FOR_ACTION.set()

    # получаем и удаляем пренадлежащие к посту медиа
    images = await get_related_images(post.pk)
    gifs = await get_related_gifs(post.pk)
    videos = await get_related_videos(post.pk)

    for image in images:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(image.image))
        await delete_img(image.pk)

    for video in videos:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(video.video))
        await delete_video(video.pk)

    for gif in gifs:
        os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(gif.gif))
        await delete_gif(gif.pk)

    await call.message.answer('<b>Управление обьявлением #' + str(post.pk) + '</b>\n\n' + str(post.text) + '\n\n'
                                                                                                           'Статус: ожидает публикации \n\n'
                                                                                                           'Выберете действие: ',
                              reply_markup=post_edit_media_actions)


@dp.message_handler(state=EditPost.WAITING_FOR_IMAGE, content_types=ContentType.PHOTO)
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
        await EditPost.WAITING_FOR_ACTION.set()
        await message.answer('Фото загружено !', reply_markup=post_edit_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Фото не загружено, произошла не известная ошибка !', reply_markup=post_edit_media_actions)


@dp.message_handler(state=EditPost.WAITING_FOR_IMAGE)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте изображение !')


@dp.callback_query_handler(state=EditPost.WAITING_FOR_ACTION, text='edit_photo')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте изображение: ')
    await EditPost.WAITING_FOR_IMAGE.set()









@dp.message_handler(state=EditPost.WAITING_FOR_VIDEO, content_types=ContentType.VIDEO)
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
        await EditPost.WAITING_FOR_ACTION.set()
        await message.answer('Видео загружено !', reply_markup=post_edit_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Видео не загружено, произошла не известная ошибка !', reply_markup=post_edit_media_actions)


@dp.message_handler(state=EditPost.WAITING_FOR_VIDEO)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте видео !')


@dp.callback_query_handler(state=EditPost.WAITING_FOR_ACTION, text='edit_video')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте видео: ')
    await EditPost.WAITING_FOR_VIDEO.set()






@dp.message_handler(state=EditPost.WAITING_FOR_GIF, content_types=ContentType.ANIMATION)
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
        await EditPost.WAITING_FOR_ACTION.set()
        await message.answer('Гифка загружена !', reply_markup=post_edit_media_actions)

    except Exception as e:
        # если произошла неизвестная ошибка - возвращаемся назад
        logging.error('Обработана неизвестная ошибка: ' + str(e))
        await message.answer('Гифка не загружена, произошла не известная ошибка !', reply_markup=post_edit_media_actions)


@dp.message_handler(state=EditPost.WAITING_FOR_GIF)
async def bot_echo(message: types.Message):
    await message.answer('Отправьте гифку !')


@dp.callback_query_handler(state=EditPost.WAITING_FOR_ACTION, text='add_gif')
async def bot_echo(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Отправьте гифку: ')
    await EditPost.WAITING_FOR_GIF.set()





@dp.callback_query_handler(state=EditPost.WAITING_FOR_ACTION, text='continue')
async def bot_echo(call: types.CallbackQuery, state: FSMContext):

    """Создание объекта поста и всех его медиа в БД и отправка задачи в cron"""

    global create_image
    await call.answer()
    await call.message.delete()

    # достаем данные поста
    state_data = await state.get_data()

    post_id = state_data['post_id']
    post = await get_post(int(post_id))

    try:
        post_images = state_data['post_images']
    except KeyError:
        # если пользователь не добавил изображения
        post_images = []

    try:
        post_videos = state_data['post_videos']
    except KeyError:
        # если пользователь не добавил видео
        post_videos = []

    try:
        post_gifs = state_data['post_gifs']
    except KeyError:
        # если пользователь не добавил гифки
        post_gifs = []

    # создаем обьекты медиа, с привязкой к посту

    if len(post_images) > 0:
        for image in post_images:
            await create_image(image_link=image, post_id=post.pk)

    if len(post_videos) > 0:
        for video in post_videos:
            await create_video(video_link=video, post_id=post.pk)

    if len(post_gifs) > 0:
        for gif in post_gifs:
            await create_gif(gif_link=gif, post_id=post.pk)

    await state.reset_state()

    posts = await get_post_by_client_id(call.message.chat.id)

    if len(posts) == 0:
        await call.message.answer('У вас 0 постов в очереди на данный момент !', reply_markup=main_menu)
    else:
        markup_btns = []

        for post in posts:
            markup_btns.append(types.InlineKeyboardButton(text='#' + str(post.pk) + ' ' + str(post.text) + '',
                                                          callback_data=posts_callback.new(
                                                              post_id=post.pk)))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*markup_btns)
        markup.add(types.InlineKeyboardButton(text='Назад', callback_data='cancel'))

        await call.message.answer('Медиа группа успешно пересоздана! \n\nПостов в очереди на публикацию ' + str(len(posts)), reply_markup=markup)