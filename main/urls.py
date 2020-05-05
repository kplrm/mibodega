from django.urls import path
from django.conf.urls import url
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("login/", views.login_request, name="login_request"),
    path("logout/", views.logout_request, name="logout_request"),
    path("embutidos", views.embutidos, name="embutidos"),
    path("vegetales", views.vegetales, name="vegetales"),
    path("lacteos", views.lacteos, name="lacteos"),
    path("abarrotes", views.abarrotes, name="abarrotes"),
    path("limpieza", views.limpieza, name="limpieza"),
    path("licores", views.licores, name="licores"),
    #url(r'^add-to-cart/(?P<slug>\d{8,11}[\-].*)/$', cart_update, name="single"),
    path("update", views.cart_add, name="cart_add"),
    path("remove", views.remove_cart, name="remove_cart"),
    path("checkout", views.checkout, name="checkout"),
    path("select_shop", views.select_shop, name="select_shop")
]
