from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Cart,CartItem
from django.contrib.gis.admin import OSMGeoAdmin

# Register your models here.
admin.site.register(ProductosEnBodega)
admin.site.register(ProductosAprobados)
#admin.site.register(Cliente)
#admin.site.register(Bodega)
admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Cliente)
class ClienteAdmin(OSMGeoAdmin):
    list_display = ('cl_user','cl_first_name','cl_last_name','cl_phone','cl_address','cl_geolocation','cl_date_reg','cl_bodega_ID')
@admin.register(Bodega)
class BodegaAdmin(OSMGeoAdmin):
    list_display = ('bd_ID','bd_user','bd_is_active','bd_name','bd_ruc','bd_raz_soc','bd_geolocation')