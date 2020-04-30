from django.urls import path
from django.conf.urls import url
from . import views


app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register", views.register, name="register"),
    path("login", views.login_request, name="login_request"),
    path("logout", views.logout_request, name="logout_request"),
    #url(r'^add-to-cart/(?P<slug>\d{8,11}[\-].*)/$', cart_update, name="single"),
    path("update", views.cart_add, name="cart_add"),
    path("remove", views.remove_cart, name="remove_cart")
]