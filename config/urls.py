from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("apps.pages.urls")),
    path('', include('apps.content.urls')),
    path('learning/', include('apps.learning.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('tinymce/', include('tinymce.urls')),
    path("select2/", include("django_select2.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
