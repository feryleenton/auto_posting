from django.db import models

# Create your models here.


class Schedule(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название", null=True)
    date = models.DateField(verbose_name='Дата', blank=True, null=True)

    # time = models.ManyToManyField('TimeSlot', verbose_name="Время", related_name="rel_schedule")

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = "Расписания"
        db_table = 'schedule'


class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule, related_name="rel_time", on_delete=models.CASCADE)
    time = models.TimeField(verbose_name="Время")

    def __str__(self):
        return str(self.time)[:5]

    class Meta:
        verbose_name = 'Время'
        db_table = 'time_slot'


class Post(models.Model):
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        db_table = 'post'

    text = models.CharField(max_length=3000, verbose_name='Текст поста')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_republished = models.BooleanField(default=True)
    author_id = models.CharField(max_length=1000, default=None)

    def __str__(self):
        return self.text


class Image(models.Model):
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        db_table = 'image'

    image = models.ImageField(verbose_name='Изображение')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'Изображение ({self.pk})'


class Video(models.Model):
    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        db_table = 'video'

    video = models.FileField(verbose_name='Видеозапись')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'Видео ({self.pk})'


class Gif(models.Model):
    class Meta:
        verbose_name = 'Гифка'
        verbose_name_plural = 'Гифки'
        db_table = 'gif'

    gif = models.ImageField(verbose_name='Гифка')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'Гифка ({self.pk})'




