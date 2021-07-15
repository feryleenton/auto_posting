import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import calendar

from keyboards.inline.callback_datas import data_pick_callback


def calendar_():
    key = InlineKeyboardMarkup(row_width=7)
    month = calendar.TextCalendar(calendar.MONDAY)
    today = datetime.datetime.today()

    month_days = month.itermonthdays(today.year, today.month)

    week_days = ['ПН', "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]  # key.add(InlineKeyboardButton())
    day_buttons = []
    date_btns = []

    month_btn = InlineKeyboardButton((str(datetime.datetime.today().month)), callback_data="###")
    key.add(month_btn)
    for w in week_days:
        day_buttons.append(InlineKeyboardButton(w, callback_data="###"))

        if len(day_buttons) == 7:
            key.add(*day_buttons)
            day_buttons.clear()

    for d in month_days:
        day = d
        c_data = data_pick_callback.new(day=d, month=today.month, year=today.year)

        if d == 0:
            d = " "
            date_btns.append(InlineKeyboardButton(f"{d}", callback_data="###"))

        else:
            if int(d) < int(today.day):
                c_data = "###"
            if int(d) == int(today.day):
                day = f"[{d}]"
            date_btns.append(InlineKeyboardButton(day, callback_data=c_data))

        if len(date_btns) == 7:
            key.add(*date_btns)
            date_btns.clear()
    return key