from aiogram.fsm.state import State, StatesGroup


class StatisticSG(StatesGroup):
    start = State()
    general = State()
    current_month = State()
    last_month = State()
    report = State()
    individual = State()
