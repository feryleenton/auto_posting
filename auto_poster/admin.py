from django.contrib import admin
from crontab import CronTab
from .models import Post, Image, Video, Gif, Schedule, TimeSlot
import logging

# Register your models here.

logger = logging.getLogger(__name__)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post
    actions = ['send_post', ]

    def send_post(self, request, queryset):
        '''Функция для постинга созданных ранее постов напрямую через админ панель'''
        for post in queryset:
            cron = CronTab(user=True)
            job = cron.new(f'python3 /home/feryleeton/PycharmProjects/auto_posting/sender.py {post.pk}')
            job.minute.every(1)
            cron.write()

    send_post.short_description = 'Опубликовать выбранные посты'


# admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Gif)


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['title', 'date']
    list_display_links = ['title']
    search_fields = ['title', 'date']

    inlines = [TimeSlotInline]