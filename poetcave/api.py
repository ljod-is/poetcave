from core.api import router as core_router
from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("", core_router)
