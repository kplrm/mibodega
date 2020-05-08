from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Cart,CartItem
from django.contrib.gis.admin import OSMGeoAdmin

# Register your models here.
admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(ProductosEnBodega)
class ProductosEnBodegaAdmin(OSMGeoAdmin):
    list_display = ('peb_bodega','peb_product','peb_status','peb_discount_status')
@admin.register(ProductosAprobados)
class ProductosAprobadosAdmin(OSMGeoAdmin):
    list_display = ('pa_product','pa_category','pa_brand')
@admin.register(Cliente)
class ClienteAdmin(OSMGeoAdmin):
    list_display = ('cl_user','cl_first_name','cl_last_name','cl_phone','cl_address','cl_geolocation')
@admin.register(Bodega)
class BodegaAdmin(OSMGeoAdmin):
    list_display = ('bd_ID','bd_user','bd_is_active','bd_name','bd_ruc','bd_raz_soc','bd_geolocation')