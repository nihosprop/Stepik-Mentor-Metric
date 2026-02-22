from aiogram.fsm.state import State, StatesGroup


class MentorSG(StatesGroup):
    start = State()
    fill_link_to_mentor = State()
    confirm_mentor = State()
    selection_mentors = State()
    confirm_delete_mentor = State()
    list_mentors = State()
