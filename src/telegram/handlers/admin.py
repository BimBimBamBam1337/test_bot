from loguru import logger
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.database.uow import UnitOfWork
from src.telegram.texts import admin_text
from src.telegram.keyboards import inline
from src.telegram.states import AddProductForm, ChangeProduct
from src.telegram.utils import build_inline_keyboard
from src.services import ProductService, OrderService

router = Router()


@router.message(Command("admin"))
async def admin(message: Message, uow: UnitOfWork):
    await message.answer(
        text=admin_text,
        reply_markup=inline.admin_panel_kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "add_product")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название товара ✏️")
    await state.set_state(AddProductForm.name)


@router.message(AddProductForm.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание товара 📄")
    await state.set_state(AddProductForm.description)


@router.message(AddProductForm.description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите цену товара 💵")
    await state.set_state(AddProductForm.price)


@router.message(AddProductForm.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Введите число, а не текст 🚫")
        return
    await state.update_data(price=price)
    await message.answer("Введите количество на складе 📦")
    await state.set_state(AddProductForm.stock)


@router.message(AddProductForm.stock)
async def add_product_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer("Введите целое число 🚫")
        return
    await state.update_data(stock=stock)
    await message.answer("Отправте котегорию")
    await state.set_state(AddProductForm.category)


@router.message(AddProductForm.category)
async def add_product_category(message: Message, state: FSMContext, uow: UnitOfWork):
    category_name = message.text.strip()
    # проверка на пустую строку
    if not category_name:
        await message.answer("Название категории не может быть пустым 🚫")
        return
    # проверка на тип (на всякий случай)
    if not isinstance(category_name, str):
        await message.answer("Введите корректное название категории ✏️")
        return
    async with uow:
        # ищем категорию в базе
        category = await uow.categories_repo.get_by_field("name", category_name)
        print(category)
        if category is None:
            # создаём новую категорию
            category = await uow.categories_repo.create({"name": category_name})
            await message.answer("Вы создали новую котегорию")

            logger.success(f"Успешно создана категория {category.name}")
    # сохраняем category_id в state
    await state.update_data(category_id=category.id)

    # переходим к шагу фото
    await message.answer("Отправьте фото товара 🖼️")
    await state.set_state(AddProductForm.photo)


@router.message(AddProductForm.photo)
async def add_product_photo(message: Message, state: FSMContext, uow: UnitOfWork):
    if not message.photo:
        await message.answer("Пришлите фото 📸")
        return

    photo_url = message.photo[-1].file_id
    data = await state.get_data()

    async with uow:
        await uow.products_repo.create(
            {
                "name": data["name"],
                "description": data["description"],
                "price": data["price"],
                "stock": data["stock"],
                "photo_url": photo_url,
                "category_id": data["category_id"],
            }
        )

    await state.clear()
    await message.answer("✅ Товар добавлен!")


@router.callback_query(F.data == "edit_products")
async def edit_products(callback: CallbackQuery, uow: UnitOfWork):
    async with uow:
        products = await uow.products_repo.get_all()

    if not products:
        await callback.message.answer("❌ Нет товаров для редактирования")
        return

    kb = build_inline_keyboard(products, "edit_product")

    await callback.message.answer("Выберите товар:", reply_markup=kb)


@router.callback_query(F.data.startswith("edit_product"))
async def edit_product(callback: CallbackQuery, uow: UnitOfWork):
    product_id = int(callback.data.split(":")[1])
    async with uow:
        product = await uow.products_repo.get(product_id)

    if not product:
        await callback.message.answer("❌ Товар не найден")
        return

    caption = (
        f"📝 Редактируем {product.name}\n"
        f"💰 Цена: {product.price}\n"
        f"📦 Количество: {product.stock}\n"
        f"📝 Описание: {product.description}"
    )

    await callback.message.answer_photo(
        photo=product.photo_url,
        caption=caption,
        reply_markup=inline.edit_product_panel_kb(product),
    )


@router.callback_query(F.data.startswith("edit_field"))
async def edit_product_field(callback: CallbackQuery, state: FSMContext):
    field, product_id = callback.data.split(":")[1:]
    if field == "photo_url":
        await callback.message.answer("Отправьте новое фото товара")
        await state.set_state(ChangeProduct.photo_url)
    elif field == "price":
        await callback.message.answer("Отправьте новую цену товара")
        await state.set_state(ChangeProduct.price)
    elif field == "stock":
        await callback.message.answer("Отправьте новое кол-во товара")
        await state.set_state(ChangeProduct.stock)

    await state.update_data(product_id=product_id, field=field)


@router.message(StateFilter(ChangeProduct))
async def process_change(message: Message, state: FSMContext, uow: UnitOfWork):
    data = await state.get_data()
    product_id = int(data["product_id"])
    field = data["field"]
    async with uow:
        product = await uow.products_repo.get(product_id)
        new_value = message.text
        if not product:
            await message.answer("❌ Товар не найден")
            await state.clear()
            return
        if field == "price":
            try:
                new_value = float(new_value)
                await message.answer(f"✅ Поле цена была обновлена: {new_value}")
                logger.info(f"Цена была обновленна {product_id}: {new_value}")
            except ValueError:
                await message.answer("❌ Цена должна быть числом")
                return
        if field == "stock":
            try:
                new_value = int(new_value)
                await message.answer(f"✅ Поле кол-во было обновлено: {new_value}")
                logger.info(f"Кол-вол было обновленно {product_id}: {new_value}")
            except ValueError:
                await message.answer("❌ Количество должно быть числом")
                return
        if field == "photo_url":
            if not message.photo:
                await message.answer("❌ Нужно отправить картинку")
                return
            new_value = message.photo[-1].file_id
            await message.answer(f"✅ Поле фото было обновлено")
            logger.info(f"Фото было обновленно {product_id}: {new_value}")
        await uow.products_repo.update(product_id, {field: new_value})

    await state.clear()


@router.callback_query(F.data == "view_orders")
async def view_orders(callback: CallbackQuery, uow: UnitOfWork):
    service = OrderService(uow)
    orders = await service.list_orders()

    if not orders:
        await callback.message.answer("📭 Заказов пока нет")
        return

    text = "\n\n".join(
        f"📦 Заказ #{o.id}\n"
        f"Пользователь: {o.user_id}\n"
        f"Статус: {o.status}\n"
        f"Дата: {o.created_at.strftime('%d.%m.%Y %H:%M')}"
        for o in orders
    )
    await callback.message.answer(text)


@router.callback_query(F.data == "change_order_status")
async def change_order_status(callback: CallbackQuery, uow: UnitOfWork):
    async with uow:
        orders = await uow.orders_repo.get_all()

    if not orders:
        await callback.message.answer("📭 Нет заказов для изменения статуса")
        return

    await callback.message.answer(
        "Выберите заказ:", reply_markup=inline.orders_panel_kb(orders)
    )


@router.callback_query(F.data.startswith("set_status:"))
async def set_status(callback: CallbackQuery, uow: UnitOfWork):
    order_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "Выберите новый статус:", reply_markup=inline.change_order_status_kb(order_id)
    )


@router.callback_query(F.data.startswith("status:"))
async def update_status(callback: CallbackQuery, uow: UnitOfWork):
    _, order_id, status = callback.data.split(":")
    order_id = int(order_id)

    async with uow:
        order = await uow.orders_repo.get(order_id)
        if order:
            order.status = message.text
            await uow.session.commit()
            await callback.message.answer(
                f"✅ Статус заказа #{order.id} изменён на {status}"
            )
        else:
            await callback.message.answer("❌ Заказ не найден")
