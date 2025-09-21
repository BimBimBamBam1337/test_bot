from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_inline_keyboard(items: list, prefix: str = "edit") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item.name, callback_data=f"{prefix}:{item.id}")]
            for item in items
        ]
    )
