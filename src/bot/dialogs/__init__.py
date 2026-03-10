from bot.dialogs.flows.courses.dialog import courses_dialog
from bot.dialogs.flows.mentors.dialog import mentors_dialog
from bot.dialogs.flows.start.dialog import start_dialog
from bot.dialogs.flows.start.handlers import start_router
from bot.dialogs.flows.statistic.dialog import statistic_dialog

ROUTERS = [
    start_router,
    start_dialog,
    mentors_dialog,
    courses_dialog,
    statistic_dialog,
]

__all__ = [
    'ROUTERS',
    'start_router',
    'start_dialog',
    'mentors_dialog',
    'courses_dialog',
    'statistic_dialog',
]
