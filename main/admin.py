from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Basket

# Register your models here.

admin.site.register(ProductosAprobados)
admin.site.register(Cliente)
admin.site.register(Bodega)
admin.site.register(ProductosEnBodega)
admin.site.register(Basket)