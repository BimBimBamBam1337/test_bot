from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class AddProductForm(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    category = State()
    photo = State()


class ChangeProduct(StatesGroup):
    photo_url = State()
    stock = State()
    price = State()
