from aiogram.fsm.state import State, StatesGroup


class UserSettingsSG(StatesGroup):
    start = State()
    add_user = State()
    confirm_add_user = State()
    remove_user = State()
    list_mentors = State()