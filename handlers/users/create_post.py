import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from loader import db

from keyboards.default import cancel
from keyboards.inline import post_creation_media_actions, calendar_, data_pick_callback, time_pick_callback, post_types
from loader import dp

from states import PostCreation
from utils.db_api.funcs import get_schedule_by_date, create_schedule, create_time_slot, get_all_posts, \
    get_posts_to_republish


@dp.message_handler(state=PostCreation.WAITING_FOR_TEXT)
async def bot_echo(message: types.Message, state: FSMContext):
    post_text = message.text
    await state.update_data(post_text=post_text)
    await message.answer('Выбирете действие: ', reply_markup=post_creation_media_actions)
    await PostCreation.WAITING_FOR_ACTION.set()


@dp.callback_query_handler(time_pick_callback.filter(), state=PostCreation.WAITING_FOR_TIME)
async def callbacks(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    await call.message.delete()
    slot_id = callback_data.get('slot_id')
    await state.update_data(slot_id=slot_id)
    await call.message.answer('Введите текст поста: ')
    await PostCreation.WAITING_FOR_TEXT.set()


@dp.callback_query_handler(data_pick_callback.filter(), state=PostCreation.WAITING_FOR_DATE)
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    await call.message.delete()

    day = callback_data.get('day')
    month = callback_data.get('month')
    year = callback_data.get('year')

    # форматируем обьект даты
    if int(day) < 10:
        day = '0' + str(day)

    if int(month) < 10:
        month = '0' + str(month)

    date = datetime.datetime.strptime('' + str(day) + '-' + str(month) + '-' + str(year) + '', '%d-%m-%Y').date()

    # проверяем, есть ли расписание на этот день в БД
    try:
        schedule = await get_schedule_by_date(str(date))
        logging.info('Найдено созданное расписание на указанную дату: ' + str(date))

    except IndexError:
        schedule = await create_schedule(date)
        logging.info('Созданно новое расписание на указанную дату: ' + str(date))

        # создаем таймслоты с заданым интервалом

        day_start_string = '' + year + '-' + month + '-' + day + ' ' + '00:00:00'
        start_day_date_object = datetime.datetime.strptime(day_start_string, '%Y-%m-%d %H:%M:%S')
        time_delta = datetime.timedelta(minutes=0)

        if start_day_date_object.day == datetime.datetime.now().day:
            # если создаеться расписание на сегодня (нужно создавать слоты со времени не позже текущего)
            logging.info('Обработано создание таймслотов на сегодняшний день')

            current_time_hrs = datetime.datetime.now().time().hour
            free_time_from_hr = current_time_hrs + 1
            hour_counter = free_time_from_hr

            while hour_counter < 24:
                time_slot = await create_time_slot(schedule, start_day_date_object + datetime.timedelta(hours=free_time_from_hr) + time_delta)
                print('Создан таймслот ' + str(time_slot.time))
                time_delta = time_delta + datetime.timedelta(minutes=30)
                hour_counter = hour_counter + 0.5
        else:
            logging.info('Обработано создание таймслотов на другой день (не сегодня)')
            for time_sector in range(48):
                time_slot = await create_time_slot(schedule, start_day_date_object + time_delta)
                print('Создан таймслот ' + str(time_slot.time))
                time_delta = time_delta + datetime.timedelta(minutes=30)
            logging.info('Таймслоты успешно созданы')

    # формируем список свободных на нужную дату слотов для вывода клавиатуры

    # говнокод

    posts = await get_all_posts()
    busy_timeslots_ids = []
    sch_slots_ids = []
    sch_slots_times = []
    times_reserved_for_republishing = []

    posts_to_republish = await get_posts_to_republish()

    for post in posts_to_republish: 
        ts = await db.get_time_slots_by_id(post.time_slot_id)
        for tslt in ts:
            times_reserved_for_republishing.append(tslt['time'])

    # получаем все айди занятых слотов

    for post in posts:
        busy_timeslots_ids.append(post.time_slot_id)

    schedule_slots = await db.get_time_slots_by_schedule(schedule.pk)

    # получаем все айди слотов на эту дату

    for schedule_slot in schedule_slots:
        sch_slots_ids.append(schedule_slot['id'])
        sch_slots_times.append(schedule_slot['time'])

    # исключаем айди занятых слотов из списка всех слотов \ удаляем время, раньше текущего, если дата сегодняшняя
    counter = 0

    while counter < len(sch_slots_ids):

        if sch_slots_ids[counter] in busy_timeslots_ids:
            sch_slots_ids.pop(counter)
            sch_slots_times.pop(counter)

        counter = counter + 1

    # формируем клавиатуру выбора времени

    key = 0
    markup_btns = []
    markup = types.InlineKeyboardMarkup(row_width=4)
    while key < len(sch_slots_times):

        if sch_slots_times[key] in times_reserved_for_republishing:
            pass
        else:
            if schedule.date == datetime.datetime.today().date():
                if sch_slots_times[key] <= datetime.datetime.today().time():
                    pass
                else:
                    markup_btns.append(types.InlineKeyboardButton(text=str(sch_slots_times[key]),
                                                                  callback_data=time_pick_callback.new(
                                                                      slot_id=str(sch_slots_ids[key]))))
            else:
                markup_btns.append(types.InlineKeyboardButton(text=str(sch_slots_times[key]),
                                                              callback_data=time_pick_callback.new(
                                                                  slot_id=str(sch_slots_ids[key]))))
        key = key + 1
    markup.add(*markup_btns)

    # конец говнокода

    await call.message.answer('Выберете время публикации: ', reply_markup=markup)
    await PostCreation.WAITING_FOR_TIME.set()


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_POST_TYPE, text='repeat')
async def callbacks(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await state.update_data(is_republished=True)
    await call.message.answer('Выберете дату публикации: ', reply_markup=calendar_())
    await PostCreation.WAITING_FOR_DATE.set()


@dp.callback_query_handler(state=PostCreation.WAITING_FOR_POST_TYPE, text='once')
async def callbacks(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    await state.update_data(is_republished=False)
    await call.message.answer('Выберете дату публикации: ', reply_markup=calendar_())
    await PostCreation.WAITING_FOR_DATE.set()


@dp.message_handler(text='Добавить в очередь', state=None)
async def bot_echo(message: types.Message, state: FSMContext):

    await message.answer('Создание нового поста', reply_markup=cancel)
    await message.answer('Выберете тип поста: ', reply_markup=post_types)
    await PostCreation.WAITING_FOR_POST_TYPE.set()