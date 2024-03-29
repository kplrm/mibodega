from django.urls import path
from django.conf.urls import url
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    # Index page
    path("", views.homepage, name="homepage"),

    # User accounts manage view
    path("registro/", views.registro, name="registro"),
    path("bodega", views.registroBodega, name="registroBodega"),
    path("login/", views.login_request, name="login_request"),
    path("logout/", views.logout_request, name="logout_request"),
    path("change_password/", views.change_password_request, name="change_password_request"),

    # Store front views and functions
    path("embutidos", views.embutidos, name="embutidos"),
    path("vegetales", views.vegetales, name="vegetales"),
    path("lacteos", views.lacteos, name="lacteos"),
    path("abarrotes", views.abarrotes, name="abarrotes"),
    path("limpieza", views.limpieza, name="limpieza"),
    path("licores", views.licores, name="licores"),
    #url(r'^add-to-cart/(?P<slug>\d{8,11}[\-].*)/$', cart_update, name="single"),
    path("cart_add", views.cart_add, name="cart_add"),
    path("remove_cart_item", views.remove_cart_item, name="remove_cart_item"),
    path("increase_quantity_cart_item", views.increase_quantity_cart_item, name="increase_quantity_cart_item"),
    path("reduce_quantity_cart_item", views.reduce_quantity_cart_item, name="reduce_quantity_cart_item"),
    path("checkout", views.checkout, name="checkout"),
    #path("save_store_location", views.save_store_location, name="save_store_location"),
    path("submit_checkout", views.submit_checkout, name="submit_checkout"),
    path("get_nearby_shops", views.get_nearby_shops, name="get_nearby_shops"),
    path("update_user_location", views.update_user_location, name="update_user_location"),
    path("search_query", views.search_query, name="search_query"),
    path("see_search_results", views.see_search_results, name="see_search_results"),
    path("search_username", views.search_username, name="search_username"),
    path("search_ruc", views.search_ruc, name="search_ruc"),
    path("pagar/<int:order_id>", views.pay, name="pay"),
    path("payment/<int:order_id>", views.payment, name="payment"),
    path("validate_payment", views.validate_payment, name="validate_payment"),
    path("payment_method", views.payment_method, name="payment_method"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/productos", views.productos, name="productos"),
    path("dashboard/mibodega", views.mibodega, name="mibodega"),
    path("dashboard/pedidos", views.pedidos, name="pedidos"),
    path("dashboard/tutorial", views.tutorial, name="tutorial"),
    path("dashboard/save_product_changes", views.save_product_changes, name="save_product_changes"),
    path("dashboard/see_sales_detail", views.see_sales_detail, name="see_sales_detail"),
    path("dashboard/remove_product", views.remove_product, name="remove_product"),

    # Landing page
    path("unete", views.unete, name="unete"),
]
