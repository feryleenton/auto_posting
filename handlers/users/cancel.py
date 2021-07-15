from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import main_menu
from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state='*', text='Вернуться в меню')
async def bot_echo(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer('Возвращаемся в главное меню', reply_markup=main_menu)