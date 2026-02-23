from aiogram.fsm.state import State, StatesGroup


class CoursesSG(StatesGroup):
    start = State()
    fill_link_to_course = State()
    confirm_curse = State()
    selection_courses = State()
    confirm_delete_course = State()
    list_courses = State()
