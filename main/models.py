import uuid # universally unique identifiers
from random import seed, randint
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# Create your models here.
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
    bd_ruc = models.CharField(max_length=11,unique=True,blank=False,null=False,verbose_name="RUC (o DNI)")
    bd_raz_soc = models.CharField(max_length=100,blank=True,null=True,verbose_name="Razón social")

    def __str__(self):
        return str(self.bd_ruc)+str(" ")+str(self.bd_name)

class ProductosEnBodega(models.Model):
    class Meta:
        verbose_name_plural = "Productos en bodegas"
        unique_together = ['peb_bodega', 'peb_product']
    
    peb_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Productos en bodegas")
    peb_bodega = models.ForeignKey(Bodega,default="",blank=True,null=False,on_delete=models.CASCADE,verbose_name="Bodega")
    peb_product = models.ForeignKey(ProductosAprobados,default="",blank=True,null=False,on_delete=models.CASCADE,verbose_name="Producto")
    peb_regular_price = models.FloatField(default=0,blank=False,null=False,verbose_name="Precio regular")
    peb_discount_price = models.FloatField(default="",blank=True,null=True,verbose_name="Precio con descuento") # not mandatory to have a discount price
    peb_discount_status = models.BooleanField(default=False,null=False,verbose_name="Vender con el descuento") # if it is currently being offered
    peb_discount_rate = models.FloatField(default=0,editable=False,verbose_name="'%' de descuento")
    peb_status = models.BooleanField(default=True,null=False,verbose_name="Disponible") # if it is currently being offered
    peb_slug = models.SlugField(max_length=100,allow_unicode=True,editable=False,unique=True)
    
    def save(self,*args,**kwargs):
        try:
            sav_object = ProductosEnBodega.objects.get(pk=self.pk)
            print("object exists")
            self.pk = sav_object.pk
        except:
            print("object DO NOT exists")

        if (self.peb_regular_price!=0) and (self.peb_discount_price!=0) and isinstance(self.peb_discount_price,float):
            self.peb_discount_rate = (self.peb_discount_price-self.peb_regular_price)/self.peb_regular_price*100
        else:
            self.peb_discount_rate = 0

        self.peb_slug = str(self.peb_bodega.bd_ruc)+str("-")+str(self.peb_product.pa_product).replace(" ","_")

        super(ProductosEnBodega,self).save(*args,**kwargs)

    def __str__(self):
        return str(self.peb_bodega)+str(" || ")+str(self.peb_product)
    
class Cart(models.Model):
    crt_ID = models.AutoField(primary_key=True,editable=False,verbose_name="ID Cart")
    crt_user = models.ForeignKey(Cliente,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Cliente") # blank=True,null=True for unauthenticated users
    crt_product = models.ManyToManyField(ProductosEnBodega,blank=True,verbose_name="Producto") # blank=True for having an empty cart
    crt_total_price = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True) # or using better .FloatField()?
    crt_quantity = models.IntegerField(default=1,verbose_name="Cantidad")
    crt_date_updated = models.DateTimeField(auto_now=True) # when was it created
    crt_date_created = models.DateTimeField(auto_now_add=True) # when was it updated
    crt_ordered = models.BooleanField(default=False,verbose_name="¿Ordered?") # to be delered?

    def __str__(self):
        return str(self.crt_quantity)+str(" of ")+str(self.crt_product)
