from bot.dialogs.flows.courses.dialog import courses_dialog
from bot.dialogs.flows.mentors.dialog import mentors_dialog
from bot.dialogs.flows.settings.dialog import settings_dialog
from bot.dialogs.flows.settings.visitor_settings.dialog import user_settings
from bot.dialogs.flows.start.dialog import start_dialog
from bot.dialogs.flows.start.handlers import start_router
from bot.dialogs.flows.statistic.dialog import statistic_dialog

DIALOGS = [
    start_dialog,
    mentors_dialog,
    courses_dialog,
    statistic_dialog,
    settings_dialog,
    user_settings,
]

ROUTERS = [
    start_router,
]

__all__ = [
    'DIALOGS',
    'ROUTERS',
    'start_router',
    'start_dialog',
    'mentors_dialog',
    'courses_dialog',
    'statistic_dialog',
    'settings_dialog',
    'user_settings',
]
