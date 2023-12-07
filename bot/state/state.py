from aiogram.fsm.state import StatesGroup, State



class OrderFood(StatesGroup):
    lesson_name = State()
    lesson_message= State()