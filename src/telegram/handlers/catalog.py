from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.database.uow import UnitOfWork
from src.services import ProductService, CategoryService
from src.telegram.utils import build_inline_keyboard
from src.telegram.keyboards import inline
from src.telegram.utils import show_categories

router = Router()


@router.message(Command("catalog"))
async def show_categories_message(message: Message, uow: UnitOfWork):
    await show_categories(message, None, uow)


@router.callback_query(F.data == "categorys")
async def show_categories_callback(callback: CallbackQuery, uow: UnitOfWork):
    await show_categories(None, callback, uow)


@router.callback_query(F.data.startswith("category:"))
async def show_products(callback: CallbackQuery, uow: UnitOfWork):
    product_service = ProductService(uow)
    category_service = CategoryService(uow)
    category_id = int(callback.data.split(":")[1])
    category = await category_service.get_category(category_id)
    products = await product_service.list_products_by_category(category.id)
    if not products:
        await callback.message.answer("В этой категории пока нет товаров")
        return

    await callback.message.answer(
        "Выберите товар:",
        reply_markup=build_inline_keyboard(products, prefix="product"),
    )


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    product_service = ProductService(uow)
    product = await product_service.get_product(product_id)
    if not product:
        await callback.message.answer("Товар не найден")
        return

    text = f"{product.name}\n\n" f"{product.description}\n\n" f"Цена: {product.price} ₽"

    if product.photo_url:
        await callback.message.answer_photo(
            photo=product.photo_url,
            caption=text,
            reply_markup=inline.build_products_panel_kb(product),
        )
    else:
        await callback.message.answer(
            text=text,
            reply_markup=inline.build_products_panel_kb(product),
        )
