from aiogram.fsm.state import State, StatesGroup


class UserSettingsSG(StatesGroup):
    start = State()
    add_user = State()
    remove_user = State()