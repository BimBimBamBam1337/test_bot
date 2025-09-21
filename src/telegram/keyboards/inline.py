from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_panel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить товар", callback_data="add_product"),
        ],
        [
            InlineKeyboardButton(
                text="Редактировать товар", callback_data="edit_products"
            ),
        ],
        [
            InlineKeyboardButton(text="Список заказов", callback_data="view_orders"),
        ],
        [
            InlineKeyboardButton(
                text="Изменить статус заказа", callback_data="change_order_status"
            ),
        ],
    ]
)


def edit_product_panel_kb(product) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Изменить фото",
                    callback_data=f"edit_field:photo_url:{product.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Изменить цену",
                    callback_data=f"edit_field:price:{product.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Изменить количество",
                    callback_data=f"edit_field:stock:{product.id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_products")],
        ]
    )


def change_order_status_panel_kb(order_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏳ В обработке", callback_data=f"status:{order_id}:processing"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚚 Отправлен", callback_data=f"status:{order_id}:shipped"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Доставлен", callback_data=f"status:{order_id}:delivered"
                )
            ],
        ]
    )


def orders_panel_kb(orders) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Заказ #{o.id} ({o.status})",
                    callback_data=f"set_status:{o.id}",
                )
            ]
            for o in orders
        ]
    )
