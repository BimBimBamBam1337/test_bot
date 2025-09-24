import pytest


@pytest.mark.asyncio
async def test_update_user(uow):
    # создаём пользователя
    user = await uow.users_repo.create(
        {"telegram_id": 1, "name": "old", "phone": "000", "address": "old address"}
    )

    # обновляем данные пользователя
    await uow.users_repo.update(
        user.id, {"name": "Test", "phone": "123", "address": "new address"}
    )

    # получаем обновлённого пользователя
    updated_user = await uow.users_repo.get(user.id)

    # проверяем результаты вне контекста
    assert updated_user.name == "Test"
    assert updated_user.phone == "123"
    assert updated_user.address == "new address"
