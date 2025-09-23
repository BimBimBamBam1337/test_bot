from .admin import router as admin_router
from .start import router as start_router
from .order import router as order_router
from .cart import router as cart_router

routers = [admin_router, start_router, order_router, cart_router]
