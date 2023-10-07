from core.api import router as core_router
from ninja import NinjaAPI
from poem.api import router as poem_router

api = NinjaAPI()

api.add_router("poem/", poem_router)
api.add_router("", core_router)
