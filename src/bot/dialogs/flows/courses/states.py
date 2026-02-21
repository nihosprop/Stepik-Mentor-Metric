from aiogram.fsm.state import State, StatesGroup


class CoursesSG(StatesGroup):
    start = State()
    fill_link_to_course = State()
