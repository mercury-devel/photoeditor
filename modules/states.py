from aiogram.fsm.state import State, StatesGroup

class GenAIState(StatesGroup):
    gen_param = State()

class IllusionAIState(StatesGroup):
    image = State()
    gen_param = State()

class CutAIState(StatesGroup):
    image = State()

class EditState(StatesGroup):
    get_photo = State()

class SpamState(StatesGroup):
    start = State()

class AddUpText(StatesGroup):
    text = State()

class AddDownText(StatesGroup):
    text = State()
