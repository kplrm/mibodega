import uuid # universally unique identifiers
from django.db import models
from django.utils import timezone
from django.conf import settings # to import global conf for user

# Create your models here.
#This adds a new table called ProductosAprobados
class ProductosAprobados(models.Model):
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
    pa_category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default=OTROS,
        verbose_name="Categoría",
    )
    pa_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,verbose_name="Código de listado")
    pa_product = models.CharField(max_length=100,default="",verbose_name="Producto")
    pa_brand = models.CharField(max_length=100,default="",verbose_name="Marca")
    pa_introduced = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de introducción")
    pa_description = models.TextField(default='sinDsescripción',verbose_name="Descripción")
    pa_rating = models.IntegerField(default='0',verbose_name="Calificación (0-5)") # 1 low 5 top
    pa_status = models.BooleanField(default=True,null=False,verbose_name="Activo") # if it is currently being offered
    pa_photo_full = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto grande") # Link to large size photos
    pa_photo_mid = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto mediana") # Link to mid size photos
    pa_photo_small = models.CharField(max_length=200,blank=True,default='noPhoto',verbose_name="Foto pequeña") # Link to small size photos
    pa_reg_sanitario = models.CharField(max_length=100,blank=True,default="",verbose_name="Registro sanitario")

    class Meta:
        verbose_name_plural = "Productos aceptados"

    @property
    def ProductosAprobados(self):
        return self.pa_ID

    # This is to change what is display when self referencing.
    # It displays the product title instead of making a list of objects.
    def __str__(self):
        return self.pa_product

class ListaDeProductos(models.Model):
    class Meta:
        verbose_name_plural = "Lista De Productos"
    
    ldp_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,verbose_name="Código de listado")
    ldp_product = models.ForeignKey(ProductosAprobados, on_delete=models.CASCADE,verbose_name="Producto") # when deleted, all values will also be deleted
    ldp_regular_price = models.FloatField(verbose_name="Precio regular")
    ldp_discount_price = models.FloatField(blank=True,null=True,verbose_name="Precio con descuento")
    ldp_discount_status = models.BooleanField(default=False,null=False,verbose_name="Vender con el descuento") # if it is currently being offered
    ldp_discount_rate = models.FloatField(default=0,editable=True,verbose_name="'%' de descuento")
    ldp_status = models.BooleanField(default=True,null=False,verbose_name="Disponible") # if it is currently being offered

#    slug = models.SlugField()

    @property
    def discount_rate(self):
        if (self.ldp_regular_price!=0) and (self.ldp_discount_price!=0) and isinstance(self.ldp_discount_price,float):
            return (self.ldp_discount_price-self.ldp_regular_price)/self.ldp_regular_price*100
        else:
            return 0

    @property
    def ProductoOfertado(self):
        return self.ldp_ID
    
    def __str__(self):
        return str(self.ldp_product)

    # This is for redirecting to every product individual page
#    def get_absolute_url(self):
#        return reverse("main:product",
#                       kwargs={'slug': self.slug})

class Item(models.Model):
    def get_add_to_cart_url(self):
        return reverse("main:add-to-cart",kwags=)


class OrderItem(models.Model): # items in the basket
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


class Order(models.Model): # items paid
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username