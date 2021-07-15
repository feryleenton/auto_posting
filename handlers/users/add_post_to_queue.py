import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from crontab import CronTab
from keyboards.default import main_menu
from loader import dp, db

import logging


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
from states import PostCreation
from utils.db_api.funcs import create_post, create_image, create_video, create_gif, get_schedule_by_id


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_ACTION, text='continue')
async def bot_echo(call: types.CallbackQuery, state: FSMContext):

    """Создание объекта поста и всех его медиа в БД и отправка задачи в cron"""

    global create_image
    await call.answer()
    await call.message.delete()

    # достаем данные поста
    state_data = await state.get_data()
    post_text = state_data['post_text']
    slot_id = state_data['slot_id']
    is_republished = state_data['is_republished']
    author_id = call.message.chat.id

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

    # создаем пост
    try:
        post = await create_post(post_text, slot_id, is_republished, author_id)
        logging.info('Пост с id = ' + str(post.pk) + ' успешно создан')
    except Exception as e:
        logging.error('Пост не был создан, произошла ошибка: ' + str(e))
        await state.reset_state()
        await call.message.answer('Пост НЕ опубликован из за неизвестной ошибки !', reply_markup=main_menu)

    # создаем обьекты медиа, с привязкой к посту

    if len(post_images) > 0:
        for image in post_images:
            created_image = await create_image(image_link=image, post_id=post.pk)
            logging.info('Изображение ' + str(created_image.image) + ' успешно создано')

    if len(post_videos) > 0:
        for video in post_videos:
            created_video = await create_video(video_link=video, post_id=post.pk)
            logging.info('Видео ' + str(created_video.video) + ' успешно создано')

    if len(post_gifs) > 0:
        for gif in post_gifs:
            created_gif = await create_gif(gif_link=gif, post_id=post.pk)
            logging.info('Гифка ' + str(created_gif.gif) + ' успешно создана')

    # достаем дату и время публикации

    time_slot = await db.get_time_slots_by_id(int(slot_id))
    pub_time = datetime.datetime.strptime(str(time_slot[0]['time']), '%H:%M:%S').time()
    schedule_id = time_slot[0]['schedule_id']
    schedule = await get_schedule_by_id(int(schedule_id))
    pub_date = schedule[-1].date

    # создаем cron job

    cron = CronTab(user=True)
    job = cron.new(f'python3 /home/feryleeton/PycharmProjects/auto_posting/sender.py {post.pk} {post.is_republished}', comment=str(post.pk))
    if is_republished == 'True' or is_republished == 'true' or is_republished == True:
        pass
    else:
        job.day.on(pub_date.day)
    job.hour.on(pub_time.hour)
    job.minute.on(pub_time.minute)
    cron.write()

    # возвращаемся в главное меню
    await state.reset_state()
    await call.message.answer('Пост добавлен в очередь !', reply_markup=main_menu)