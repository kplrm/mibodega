from django.urls import path, re_path
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

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
    # Password Reset View
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="main/password_reset.html"), name='password_reset'),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="main/password_reset_done.html"), name='password_reset_done'),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="main/password_reset_confirm.html"), name='password_reset_confirm'),
    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(template_name="main/password_reset_confirm.html"), name='password_reset_confirm'),
    #path("password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/", auth_views.PasswordResetConfirmView.as_view(template_name="main/password_reset_confirm.html"), name='password_reset_confirm'),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="main/password_reset_complete.html"), name='password_reset_complete'),

    #url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),

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
