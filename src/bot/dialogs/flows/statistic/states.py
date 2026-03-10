from aiogram.fsm.state import State, StatesGroup


class StatisticSG(StatesGroup):
    start = State()
    general = State()
    individual = State()
