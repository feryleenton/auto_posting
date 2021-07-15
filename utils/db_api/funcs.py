import datetime
from tortoise import Tortoise
from data.config import POSTGRES_URI
from .models import Post, Image, Gif, Video, Schedule, TimeSlot


async def create_post(post_text, slot_id, is_republished, author_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    post = await Post.create(text=post_text, time_slot_id=slot_id, is_republished=is_republished, author_id=author_id)
    return post


async def create_image(image_link, post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    image = await Image.create(image=image_link, post_id=post_id)
    return image


async def delete_post(post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    await Post.filter(pk=post_id).delete()


async def delete_img(image_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    await Image.filter(pk=image_id).delete()


async def delete_video(image_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    await Video.filter(pk=image_id).delete()


async def delete_gif(image_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    await Gif.filter(pk=image_id).delete()


async def create_video(video_link, post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    video = await Video.create(video=video_link, post_id=post_id)
    return video


async def create_gif(gif_link, post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    gif = await Gif.create(gif=gif_link, post_id=post_id)
    return gif


async def get_post(post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    post = await Post.get_or_none(pk=post_id)
    return post


async def get_posts_to_republish():
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    post = await Post.filter(is_republished='true')
    return post


async def get_all_posts():
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    posts = await Post.filter()
    return posts


async def get_post_by_client_id(client_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    posts = await Post.filter(author_id=client_id)
    return posts


async def get_schedule_by_date(date):
    """Возвращает последнее созданное на указанную дату расписание"""
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    schedule = await Schedule.filter(date=date)
    return schedule[-1]


async def create_schedule(date):
    """Создает расписание по дате"""
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    schedule = await Schedule.create(title=str(date), date=date)
    return schedule


async def get_schedule_by_id(id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    schedule = await Schedule.filter(id=id)
    return schedule


async def create_time_slot(schedule, time):
    """Создает time_slot по времени, и привязке к schedule"""
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    time_slot = await TimeSlot.create(time=time, schedule_id=schedule.pk)
    return time_slot


async def get_related_images(post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    images = await Image.filter(post=post_id)
    return images


async def get_related_gifs(post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    gifs = await Gif.filter(post=post_id)
    return gifs


async def get_related_videos(post_id):
    await Tortoise.init(
        db_url=POSTGRES_URI,
        modules={'models': ['utils.db_api.models']}
    )
    videos = await Video.filter(post=post_id)
    return videos
