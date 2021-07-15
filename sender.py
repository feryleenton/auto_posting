import asyncio
import sys
from crontab import CronTab
import aiogram
import os
from data.config import CHANNEL
from loader import bot
from utils.db_api.funcs import get_related_images, get_related_gifs, get_related_videos, get_post, delete_post, \
    delete_img, delete_video, delete_gif


async def publish():

    # получаем пост по id из аргумента
    post_id = str(sys.argv[-2])
    is_republished = sys.argv[-1]
    post = await get_post(post_id)

    # получаем пренадлежащие к посту медиа
    images = await get_related_images(post_id)
    gifs = await get_related_gifs(post_id)
    videos = await get_related_videos(post_id)

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
        await bot.send_media_group(CHANNEL, media)
    except aiogram.utils.exceptions.BadRequest:
        pass

    await bot.send_message(CHANNEL, str(post.text))

    if is_republished == 'True' or is_republished == 'true' or is_republished == True:
        pass
    else:
        """Если пост единоразовый - после публикации удаляем таску в cron, удаляем пост из БД"""

        cron = CronTab(user=True)
        cron.remove_all(comment=str(post.pk))
        cron.write()

        for image in images:
            os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(image.image))
            await delete_img(image.pk)

        for video in videos:
            os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(video.video))
            await delete_video(video.pk)

        for gif in gifs:
            os.remove("/home/feryleeton/PycharmProjects/auto_posting/auto_posting" + str(gif.gif))
            await delete_gif(gif.pk)

        await delete_post(post_id)

loop = asyncio.get_event_loop()
coroutine = publish()
loop.run_until_complete(coroutine)
