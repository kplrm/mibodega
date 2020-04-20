from django.contrib import admin
from .models import ProductosAprobados, ListaDeProductos

#DG
from .models import OrderItem, Order

# Register your models here.

admin.site.register(ProductosAprobados)
admin.site.register(ListaDeProductos)

admin.site.register(OrderItem)
admin.site.register(Order)