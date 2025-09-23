import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from datetime import datetime


def build_inline_keyboard(items: list, prefix: str = "edit") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item.name, callback_data=f"{prefix}:{item.id}")]
            for item in items
        ]
    )


def generate_order_number() -> str:
    # Пример: ORD-20250920-6E4A1B
    short = uuid.uuid4().hex[:6].upper()
    return f"{short}"
