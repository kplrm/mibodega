from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ListaDeProductos,Basket,Listado

# Register your models here.

admin.site.register(ProductosAprobados)
admin.site.register(Cliente)
admin.site.register(Bodega)
admin.site.register(ListaDeProductos)
admin.site.register(Basket)
admin.site.register(Listado)