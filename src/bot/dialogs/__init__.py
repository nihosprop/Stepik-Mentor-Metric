from bot.dialogs.flows.start.dialog import start_dialog
from bot.dialogs.flows.start.handlers import start_router

ROUTERS = [start_router, start_dialog]

__all__ = ['ROUTERS', 'start_router', 'start_dialog']
