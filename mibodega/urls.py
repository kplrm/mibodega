from django.contrib import admin
from django.urls import path, include

#DG
from django.conf import settings
from django.conf.urls.static import static
#

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('main.urls')),
    path("dashboard/", include('mibodega.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
