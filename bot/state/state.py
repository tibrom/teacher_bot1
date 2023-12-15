from aiogram.fsm.state import StatesGroup, State



class LessonState(StatesGroup):
    lesson_name = State()
    lesson_message= State()



class LessonInfoState(StatesGroup):
    key_name = State()
    infodata = State()