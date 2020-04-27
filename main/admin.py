from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Cart,CartItem

# Register your models here.
admin.site.register(ProductosEnBodega)
admin.site.register(ProductosAprobados)
admin.site.register(Cliente)
admin.site.register(Bodega)
admin.site.register(Cart)
admin.site.register(CartItem)