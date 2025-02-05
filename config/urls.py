from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.urls import include, path
from django.views import defaults as default_views

from config.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("allauth.headless.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("sentry-debug/", lambda request: 1 / 0),  # noqa: ARG005
    path("api/", api.urls),  # type: ignore
    path("", lambda request: redirect("admin/")),  # noqa: ARG005
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
