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
delivery_panel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚚 Курьер", callback_data="delivery:courier")],
        [InlineKeyboardButton(text="📦 Самовывоз", callback_data="delivery:pickup")],
    ]
)

confirm_panel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")],
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


def build_cart_panel_kb(cart):
    buttons = []
    for item in cart.items:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="➖", callback_data=f"decrease:{item.product_id}"
                ),
                InlineKeyboardButton(
                    text=f"{item.product.name} ({item.quantity})", callback_data="noop"
                ),
                InlineKeyboardButton(
                    text="➕", callback_data=f"increase:{item.product_id}"
                ),
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="❌ Удалить", callback_data=f"remove_item:{item.product_id}"
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_categories_panel_kb(categories: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat.name, callback_data=f"category:{cat.id}")]
            for cat in categories
        ]
    )


def build_products_panel_kb(product) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Добавить в корзину", callback_data=f"add:{product.id}"
            )
        ],
        [InlineKeyboardButton(text="Назад к категориям", callback_data="categorys")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
