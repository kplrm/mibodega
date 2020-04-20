import uuid # universally unique identifiers
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
#This adds a new table called ProductosAprobados
class ProductosAprobados(models.Model):
    class Meta:
        verbose_name_plural = "Productos aceptados"

    # These are the folders in /media/ and the url address
    EMBUTIDOS = 'embutidos'
    LACTEOS = 'lacteos'
    ABARROTES = 'abarrotes'
    LIMPIEZA = 'limpieza'
    LICORES = 'licores'
    VEGETALES = 'vegetales'
    OTROS = 'otros'
    CATEGORY_CHOICES = [
        (EMBUTIDOS, 'Embutidos'), #(what does on the db, what it's displayed)
        (LACTEOS, 'Lácteos'),
        (ABARROTES, 'Abarrotes'),
        (LIMPIEZA, 'Limpieza'),
        (LICORES, 'Licores'),
        (VEGETALES, 'Vegetales') ,
        (OTROS, 'Otros'),
    ]

    #ID automatic generated as 'pk'
    pa_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Producto")
    pa_product = models.CharField(max_length=100,default="",verbose_name="Producto")
    pa_category = models.CharField(max_length=10,choices=CATEGORY_CHOICES,default=OTROS,verbose_name="Categoría")
    pa_brand = models.CharField(max_length=100,default="",verbose_name="Marca")
    pa_introduced = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de introducción")
    pa_description = models.TextField(default='sinDsescripción',verbose_name="Descripción")
    pa_rating = models.IntegerField(default='0',verbose_name="Calificación (0-5)") # 1 low 5 top
    pa_status = models.BooleanField(default=True,null=False,verbose_name="Activo") # if it is currently being offered
    pa_photo_full = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto grande") # Link to large size photos
    pa_photo_mid = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto mediana") # Link to mid size photos
    pa_photo_small = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto pequeña") # Link to small size photos
    pa_reg_sanitario = models.CharField(max_length=100,blank=True,default="",verbose_name="Registro sanitario")

    @property
    def ProductosAprobados(self):
        return self.pa_ID

    def __str__(self):
        return self.pa_product

class Cliente(models.Model):
    cl_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Cliente")
    cl_user = models.OneToOneField(User,null=True,on_delete=models.CASCADE,verbose_name="Cliente (usuario)")
    cl_first_name = models.CharField(max_length=50,blank=True,null=True,verbose_name="Nombre")
    cl_last_name = models.CharField(max_length=50,blank=True,null=True,verbose_name="Apellido")
    cl_phone = models.CharField(max_length=9,blank=False,null=True,verbose_name="Celular")
    cl_address = models.CharField(max_length=50,blank=True,null=True,verbose_name="Dirreción")
    cl_geolocation = models.CharField(max_length=50,blank=True,null=True,verbose_name="Ubicación")
    cl_date_reg = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de registro")

    def __str__(self):
        return str(self.cl_user)
    
class Bodega(models.Model):
    bd_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Bodega")
    bd_user = models.ForeignKey(Cliente,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_is_active = models.BooleanField(default=True,verbose_name="¿Está activo?")
    bd_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="Nombre comercial")
    bd_ruc = models.CharField(max_length=11,blank=True,null=True,verbose_name="RUC")
    bd_raz_soc = models.CharField(max_length=100,blank=True,null=True,verbose_name="Razón social")

    def __str__(self):
        return str(self.bd_raz_soc)

class ListaDeProductos(models.Model):
    class Meta:
        verbose_name_plural = "Listas de productos"
    
    lpd_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Lista de productos")
    ldp_cod = models.ForeignKey(Bodega,null=True,on_delete=models.CASCADE,verbose_name="Bodega")

    def __str__(self):
        return str(self.lpd_ID)

class Listado(models.Model):
    class Meta:
        verbose_name_plural = "Listados"
    
    lp_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Listado")
    ld_cod = models.ForeignKey(ListaDeProductos,null=True,on_delete=models.CASCADE,verbose_name="Código de listado")
    ld_product = models.ForeignKey(ProductosAprobados,on_delete=models.CASCADE,verbose_name="Producto")
    ld_regular_price = models.FloatField(verbose_name="Precio regular")
    ld_discount_price = models.FloatField(blank=True,null=True,verbose_name="Precio con descuento")
    ld_discount_status = models.BooleanField(default=False,null=False,verbose_name="Vender con el descuento") # if it is currently being offered
    ld_discount_rate = models.FloatField(default=0,editable=True,verbose_name="'%' de descuento")
    ld_status = models.BooleanField(default=True,null=False,verbose_name="Disponible") # if it is currently being offered

    @property
    def discount_rate(self):
        if (self.ld_regular_price!=0) and (self.ld_discount_price!=0) and isinstance(self.ld_discount_price,float):
            return (self.ld_discount_price-self.ld_regular_price)/self.ld_regular_price*100
        else:
            return 0
    
    def __str__(self):
        return str(self.ld_product)
    
class Basket(models.Model):
    bkt_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Cesta")
    bkt_cod = models.OneToOneField(Cliente,null=True,on_delete=models.CASCADE,verbose_name="ID Cliente")
    bkt_product = models.ManyToManyField(ListaDeProductos,verbose_name="Producto")
    bkt_quantity = models.IntegerField(default=1,verbose_name="Cantidad")

    def __str__(self):
        return self.bkt_product.ldp_product.pa_product

class OrderItem(models.Model):

    pass

class Order(models.Model):
    pass