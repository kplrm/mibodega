from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Basket

# Register your models here.
class DiscountRateCalculator(admin.ModelAdmin):
    pass
    
admin.site.register(ProductosEnBodega)

admin.site.register(ProductosAprobados)
admin.site.register(Cliente)
admin.site.register(Bodega)
admin.site.register(Basket)