from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


class Registration(StatesGroup):
    name = State()
    phone = State()
    address = State()


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


class CheckoutStates(StatesGroup):
    name = State()
    phone = State()
    address = State()
    delivery = State()
    confirmation = State()


class Cart(StatesGroup):
    confirm = State()
    how_many = State()
