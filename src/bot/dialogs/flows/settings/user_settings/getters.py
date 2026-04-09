from aiogram_dialog import DialogManager


async def get_user_tg_id(dialog_manager: DialogManager, **_kwargs) -> dict:
    """
    Getter function for the dialog window to display user_tg_id.
    """
    return {'user_tg_id': dialog_manager.dialog_data.get('user_tg_id', '')}
