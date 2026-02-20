from aiogram.fsm.state import State, StatesGroup


class MentorSG(StatesGroup):
    start = State()
    fill_link_to_mentor = State()
