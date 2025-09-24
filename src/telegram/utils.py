import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message
from datetime import datetime

from src.database.uow import UnitOfWork
from src.services import CategoryService


# Функция для вывода кнопки с именем товара
def build_inline_keyboard(items: list, prefix: str = "edit") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item.name, callback_data=f"{prefix}:{item.id}")]
            for item in items
        ]
    )


def generate_order_number() -> str:
    # Пример: 6E4A1B
    short = uuid.uuid4().hex[:6].upper()
    return f"{short}"


# Общая функция для вывода категорий
async def show_categories(
    message: Message | None, callback: CallbackQuery | None, uow: UnitOfWork
):
    category_service = CategoryService(uow)
    categories = await category_service.list_categories()
    if not categories:
        if message:
            await message.answer("Категории пока отсутствуют")
        elif callback:
            await callback.message.answer("Категории пока отсутствуют")
        return

    keyboard = build_inline_keyboard(categories, prefix="category")
    if message:
        await message.answer("Выберите категорию:", reply_markup=keyboard)
    elif callback:
        await callback.message.answer("Выберите категорию:", reply_markup=keyboard)
