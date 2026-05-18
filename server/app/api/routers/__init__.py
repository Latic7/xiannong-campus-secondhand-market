from .admin import router as admin_router
from .auth import router as auth_router
from .orders import router as orders_router
from .products import router as products_router
from .reports import router as reports_router
from .users import router as users_router

ROUTERS = [
    auth_router,
    users_router,
    products_router,
    orders_router,
    reports_router,
    admin_router,
]
