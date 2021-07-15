import datetime
import os

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline import manage_posts
from loader import dp, bot, db

from crontab import CronTab

from states import ManagePosts
from utils.db_api.funcs import get_post_by_client_id, get_related_images, get_related_gifs, get_related_videos, \
    get_post, delete_img, delete_video, delete_gif, delete_post, get_schedule_by_id


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


@dp.message_handler(state=None, text='/posts')
async def bot_echo(message: types.Message):
    posts = await get_post_by_client_id(message.chat.id)

    await message.answer('Список ваших постов в очереди на публикацию: ')

    for post in posts:

        # получаем пренадлежащие к посту медиа
        images = await get_related_images(post.pk)
        gifs = await get_related_gifs(post.pk)
        videos = await get_related_videos(post.pk)

        # достаем дату и время публикации

        time_slot = await db.get_time_slots_by_id(int(post.time_slot_id))
        pub_time = datetime.datetime.strptime(str(time_slot[0]['time']), '%H:%M:%S').time()
        schedule_id = time_slot[0]['schedule_id']
        schedule = await get_schedule_by_id(int(schedule_id))
        pub_date = schedule[-1].date

        # формируем медиагруппу
        media = aiogram.types.MediaGroup()

        for image in images:
            media.attach_photo(aiogram.types.InputFile("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(image.image)))

        for video in videos:
            media.attach_video(aiogram.types.InputFile("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(video.video)))

        for gif in gifs:
            media.attach_video(aiogram.types.InputFile("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(gif.gif)))

        # публикуем сообщение в канал

        try:
            await bot.send_media_group(message.chat.id, media)
        except aiogram.utils.exceptions.BadRequest:
            pass

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Удалить', callback_data=manage_posts.new(post_id=post.pk)))

        if post.is_republished == 'true' or post.is_republished == True:
            is_rep = 'Ежидневный'
        else:
            is_rep = 'Единоразовый'

        await bot.send_message(message.chat.id, str(post.text) + f'\n\n\nПубликация назначена на: {str(pub_date)} {str(pub_time)}\nТип поста: {is_rep}', reply_markup=markup)