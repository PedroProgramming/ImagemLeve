from ninja import NinjaAPI
from optimizer.api import optimizer_router
from scalar_django_ninja import ScalarViewer

api = NinjaAPI(
    docs=ScalarViewer(),
    docs_url="/docs/"
)

api.add_router("/", optimizer_router)