from django.urls import path
from django.conf.urls import url
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard'  # here for namespacing of urls.

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dashboard/productos", views.productos, name="productos"),
]
