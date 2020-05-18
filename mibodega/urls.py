from django.contrib import admin
from django.urls import path, include
from ..dashboard import views

#DG
from django.conf import settings
from django.conf.urls.static import static
#

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('main.urls')),
    path("dashboard", views.dashboard, name="dashboard"),
]

#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
