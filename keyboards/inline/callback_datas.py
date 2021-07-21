from aiogram.utils.callback_data import CallbackData

data_pick_callback = CallbackData("pick_date",
                                 "day",
                                 'month',
                                 'year')

time_pick_callback = CallbackData('pick_time',
                                 'slot_id')

manage_posts = CallbackData('delete_post',
                                 'post_id')

posts_callback = CallbackData('posts_callback',
                                 'post_id')

edit_post_callback = CallbackData('edit_post',
                                 'post_id')

edit_post_text = CallbackData('edit_post',
                                 'post_id')

edit_post_media = CallbackData('edit_post_media',
                                 'post_id')