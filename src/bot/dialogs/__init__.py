from bot.dialogs.start.dialog import start_dialog
from bot.dialogs.start.handlers import start_router

ROUTERS = [start_router, start_dialog]

__all__ = ['ROUTERS', 'start_router', 'start_dialog']
