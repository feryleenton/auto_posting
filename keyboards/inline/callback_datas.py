from aiogram.utils.callback_data import CallbackData

data_pick_callback = CallbackData("pick_date",
                                 "day",
                                 'month',
                                 'year')

time_pick_callback = CallbackData('pick_time',
                                 'slot_id')

manage_posts = CallbackData('delete_post',
                                 'post_id')