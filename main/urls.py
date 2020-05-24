from django.urls import path
from django.conf.urls import url
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("registro/", views.registro, name="registro"),
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
    path("save_store_location", views.save_store_location, name="save_store_location"),
    path("submit_checkout", views.submit_checkout, name="submit_checkout"),
    path("get_nearby_shops", views.get_nearby_shops, name="get_nearby_shops"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/productos", views.productos, name="productos"),
    path("dashboard/mibodega", views.mibodega, name="mibodega"),
    path("dashboard/pedidos", views.pedidos, name="pedidos"),
    path("dashboard/save_product_changes", views.save_product_changes, name="save_product_changes"),
    path("dashboard/see_sales_detail", views.see_sales_detail, name="see_sales_detail"),
    path("dashboard/remove_product", views.remove_product, name="remove_product"),

    # Landing page
    path("unete", views.unete, name="unete"),
]
