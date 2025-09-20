from aiogram.fsm.state import StatesGroup, State


class NewsletterState(StatesGroup):
    text = State()


class Dialog(StatesGroup):
    date = State()
    time = State()
    city = State()
    life = State()
