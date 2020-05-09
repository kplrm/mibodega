from django.contrib import admin
from .models import ProductosAprobados,Cliente,Bodega,ProductosEnBodega,Cart,CartItem
from django.contrib.gis.admin import OSMGeoAdmin

# Register your models here.
#admin.site.register(Cart)

@admin.register(Cart)
class ProductosEnBodegaAdmin(OSMGeoAdmin):
    list_display = ('crt_ID','crt_user','crt_total_price','crt_ordered')
@admin.register(CartItem)
class ProductosEnBodegaAdmin(OSMGeoAdmin):
    list_display = ('ci_cart_ID','ci_user','ci_product','ci_quantity')
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