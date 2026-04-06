from aiogram.fsm.state import State, StatesGroup


class SettingsSG(StatesGroup):
    start = State()

    users = State()
    add_user = State()
    remove_user = State()

    admins = State()
    add_admin = State()
    remove_admin = State()
