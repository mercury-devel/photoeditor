from aiogram.filters.callback_data import CallbackData


class Ban(CallbackData, prefix="ban"):
    id: int

class AddText(CallbackData, prefix="add_text"):
    font: str
