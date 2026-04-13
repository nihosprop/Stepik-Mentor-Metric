from aiogram.fsm.state import State, StatesGroup


class AdminSettingsSG(StatesGroup):
    start = State()
    add_rights = State()
    confirm_rights = State()
    remove_rights = State()
    list_admins = State()
