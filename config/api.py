from django.core.handlers.wsgi import WSGIRequest
from ninja.openapi.docs import Redoc
from ninja_extra import NinjaExtraAPI

from features.bot import apis as bot_apis

api = NinjaExtraAPI(
    title="Django Template",
    version="1.0.0",
    app_name="django_template",
    docs=Redoc(),
    docs_url="docs/",
)


@api.get("", tags=["health_check"])
def api_root_health_check(request: WSGIRequest):  # noqa: ARG001
    """Check api health."""
    return {"status": "healthy"}


@api.get("health_check/", tags=["health_check"])
def health_check(request: WSGIRequest):  # noqa: ARG001
    """Check api health."""
    return {"status": "healthy"}


api.register_controllers(bot_apis.BotAPI)
