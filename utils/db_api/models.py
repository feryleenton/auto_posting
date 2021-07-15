from tortoise.models import Model
from tortoise import fields


class Schedule(Model):
    title = fields.CharField(max_length=100)
    date = fields.DateField()

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = "Расписания"
        table = 'schedule'


class TimeSlot(Model):
    schedule = fields.ForeignKeyField('models.Schedule', on_delete=fields.CASCADE)
    time = fields.DatetimeField()

    class Meta:
        verbose_name = 'Время'
        table = 'time_slot'


class Post(Model):
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        table = 'post'

    text = fields.CharField(max_length=3000)
    time_slot = fields.ForeignKeyField('models.TimeSlot', on_delete=fields.CASCADE)
    is_republished = fields.BooleanField(default=True)
    author_id = fields.CharField(max_length=1000, default=None)


class Image(Model):
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        table = 'image'

    image = fields.CharField(max_length=3000)
    post = fields.ForeignKeyField('models.Post', on_delete=fields.CASCADE)


class Video(Model):
    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        table = 'video'

    video = fields.CharField(max_length=3000)
    post = fields.ForeignKeyField('models.Post', on_delete=fields.CASCADE)


class Gif(Model):
    class Meta:
        verbose_name = 'Гифка'
        verbose_name_plural = 'Гифки'
        table = 'gif'

    gif = fields.CharField(max_length=3000)
    post = fields.ForeignKeyField('models.Post', on_delete=fields.CASCADE)
