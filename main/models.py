import uuid # universally unique identifiers
from random import seed, randint
#from django.db import models
from django.contrib.gis.db import models    
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.db.models.aggregates import Count
from random import randint

User = settings.AUTH_USER_MODEL

# Create your models here.
class ProductosAprobados(models.Model):
    class Meta:
        verbose_name_plural = "Productos aprobados"

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
    cl_email = models.CharField(max_length=50,blank=True,null=True,verbose_name="E-mail")
    cl_address = models.CharField(max_length=50,blank=True,null=True,verbose_name="Dirreción")
    cl_geolocation = models.PointField(blank=True,null=True,verbose_name="Ubicación")
    cl_date_reg = models.DateTimeField(auto_now_add=True,verbose_name="Fecha de registro")
    cl_bodega_ID = models.CharField(max_length=36,default="",blank=True,null=True,verbose_name="ID Bodega")

    def __str__(self):
        return str(self.cl_user)
    
class Bodega(models.Model):
    bd_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,verbose_name="ID Bodega")
    bd_user = models.ForeignKey(Cliente,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_is_active = models.BooleanField(default=True,verbose_name="¿Está activo?")
    bd_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="Nombre comercial")
    bd_ruc = models.CharField(max_length=11,unique=True,blank=False,null=False,verbose_name="RUC (o DNI)")
    bd_raz_soc = models.CharField(max_length=100,blank=True,null=True,verbose_name="Razón social")
    bd_geolocation = models.PointField(blank=True,null=True,verbose_name="Sede")
    bd_email = models.CharField(max_length=50,blank=True,null=True,verbose_name="E-mail")
    bd_phone = models.CharField(max_length=9,blank=False,null=True,verbose_name="Celular")

    def __str__(self):
        return str(self.bd_name)

class ProductosEnBodega(models.Model):
    class Meta:
        verbose_name_plural = "Productos en bodegas"
        unique_together = ['peb_bodega', 'peb_product']
    
    #FORGET NOT TO DEACTIVATE EDITION OF UUIDFIELD!!!!!!!!!!!!!
    peb_ID = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=True,verbose_name="ID Productos en bodegas")
    peb_bodega = models.ForeignKey(Bodega,default="",blank=True,null=False,on_delete=models.CASCADE,verbose_name="Bodega")
    peb_product = models.ForeignKey(ProductosAprobados,default="",blank=True,null=False,on_delete=models.CASCADE,verbose_name="Producto")
    peb_regular_price = models.FloatField(default=0,blank=False,null=False,verbose_name="Precio regular")
    peb_discount_price = models.FloatField(default="",blank=True,null=True,verbose_name="Precio con descuento") # not mandatory to have a discount price
    peb_discount_status = models.BooleanField(default=False,null=False,verbose_name="Vender con descuento") # if it is currently being offered
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
    
class CartManager(models.Manager):
    # Like get_or_create, but related to our specific use case: Cart
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        #Look for the cart ID session
        qs = self.get_queryset().filter(crt_ID=cart_id)
        # Check if there is a cart in the session
        if qs.count() == 1:
            # Loads the current session cart
            cart_obj = qs.first()
            new_obj = False
            # Verify if user is authenticated and current session's cart has no user
            if request.user.is_authenticated and cart_obj.crt_user is None:
                print("Buscando coche de usuario...")
                # Look for a previous user's Cart
                qs2 = self.get_queryset().filter(crt_user=request.user)
                if qs2.exists():
                    print("El usuario tiene multiples coches...")
                    previous_cart_obj = qs2.first()
                    print("Coche previo:")
                    print(previous_cart_obj)
                    print("Coche actual:")
                    print(cart_obj)
                    # Update products
                    for product in previous_cart_obj.crt_product.all():
                        # Merging previous cart with current cart
                        print("Buscando objetos...")
                        if cart_obj.crt_product.filter(pk=product.pk).exists():
                            print("Product previously found. Do nothing.")
                        else:
                            print("Found nothing. Adding previously added product.")
                            cart_obj.crt_product.add(product)
                    # Update items
                    for item in CartItem.objects.all():
                        print("Buscando Items...")
                        print(item)
                        print(item.ci_cart_ID)
                        print(previous_cart_obj.crt_ID)
                        if item.ci_cart_ID == previous_cart_obj.crt_ID:
                            item.ci_cart_ID = cart_obj.crt_ID
                            item.save()
                    previous_cart_obj.delete()
                    print("exit product search")
                    # Update price
                    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()
                    total_price = 0
                    for item in cart_list:
                        if item.ci_product.peb_discount_status:
                            total_price += item.ci_quantity * item.ci_product.peb_discount_price
                        else:
                            total_price += item.ci_quantity * item.ci_product.peb_regular_price
                    cart_obj.crt_total_price = total_price
                    cart_obj.save()
                else:
                    # There is no previous cart, so no item to recover
                    print("El usuario no tiene coche")
                
                cart_obj.crt_user = request.user
                cart_obj.save()
        else:
            cart_obj = self.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.crt_ID
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            print("Sin usuario")
            if user.is_authenticated:
                print("Hay una autenticación")
                user_obj = user
        return self.model.objects.create(crt_user=user_obj)

class CartItem(models.Model):
    ci_cart_ID = models.IntegerField(default=0,verbose_name="Cart ID")
    ci_user = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Usuario") # blank=True,null=True for unauthenticated users
    ci_product = models.ForeignKey(ProductosEnBodega,on_delete=models.CASCADE,verbose_name="Producto")
    ci_quantity = models.IntegerField(default=1)
    ci_date_updated = models.DateTimeField(auto_now=True) # when was it created
    ci_date_created = models.DateTimeField(auto_now_add=True) # when was it updated

    def __str__(self):
        return str("Cart ID:")+str(self.ci_cart_ID)+str(" || Usuario:")+str(self.ci_product)

class Cart(models.Model):
    crt_ID = models.AutoField(primary_key=True,editable=False,verbose_name="ID Cart")
    crt_user = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Usuario") # blank=True,null=True for unauthenticated users
    crt_item = models.ManyToManyField(CartItem,blank=True,verbose_name="Item") # blank=True for having an empty cart
    crt_product = models.ManyToManyField(ProductosEnBodega,blank=True,verbose_name="Producto") # blank=True for having an empty cart
    crt_total_price = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True) # or using better .FloatField()?
    crt_date_updated = models.DateTimeField(auto_now=True) # when was it created
    crt_date_created = models.DateTimeField(auto_now_add=True) # when was it updated
    crt_ordered = models.BooleanField(default=False,verbose_name="¿Ordered?") # to be delered?

    objects = CartManager()

    def __str__(self):
        return str("Cart ID:")+str(self.crt_ID)+str(" || Producto:")+str(self.crt_user)

class Orders(models.Model):
    ord_ID = models.AutoField(primary_key=True,editable=False,verbose_name="ID Order")
    ord_user = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Usuario") # blank=True,null=True for unauthenticated users
    ord_taxes = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True) # or using better .FloatField()?
    ord_total_price = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True) # or using better .FloatField()?
    ord_date_updated = models.DateTimeField(auto_now=True) # when was it created
    ord_date_created = models.DateTimeField(auto_now_add=True) # when was it updated

    def __str__(self):
        return str("Order ID:")+str(self.ord_ID)+str(" || User:")+str(self.ord_user)

class BodegaOrders(models.Model):
    bo_order = models.ForeignKey(Orders,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Orden de Compra")
    bo_bodega = models.ForeignKey(Bodega,blank=True,null=True,on_delete=models.CASCADE,verbose_name="Bodega")
    bo_taxes = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True)
    bo_total_price = models.DecimalField(default=0.00,max_digits=6,decimal_places=2,blank=True,null=True)

    def __str__(self):
        return str("Order ID:")+str(self.bo_order.ord_ID)+str(" || User:")+str(self.bo_user)

class OrderItem(models.Model):
    oi_ID = models.ForeignKey(Orders,blank=True,null=True,on_delete=models.CASCADE,verbose_name="ID Orden de Compra")
    oi_bo_ID = models.ForeignKey(BodegaOrders,blank=True,null=True,on_delete=models.CASCADE,verbose_name="Bodega Orden de compra")
    oi_id_product = models.CharField(max_length=100,default="",verbose_name="ID Producto")
    oi_product = models.CharField(max_length=100,default="",verbose_name="Producto")
    oi_price = models.CharField(max_length=100,default="",verbose_name="Precio")
    oi_prod_total = models.CharField(max_length=100,default="",verbose_name="Precio")
    oi_quantity = models.CharField(max_length=100,default="",verbose_name="Cantidad")
    oi_id_bodega = models.CharField(max_length=100,default="",verbose_name="ID Bodega")
    oi_ruc_bodega = models.CharField(max_length=100,default="",verbose_name="RUC Bodega")
    oi_bodega_name = models.CharField(max_length=100,default="",verbose_name="Nombre de Bodega")
    oi_bodega_phone = models.CharField(max_length=100,default="",verbose_name="Teléfono de Bodega")

    def __str__(self):
        return str("Order ID:")+str(self.oi_ID)+str(" || Product ID:")+str(self.oi_id_product)+str(" || Producto:")+str(self.oi_product)