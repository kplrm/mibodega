from django.db import models
from django.utils import timezone

# Create your models here.
#This adds a new table called productos_aprobados
class productos_aprobados(models.Model):
    EMBUTIDOS = 'EM'
    LACTEOS = 'LA'
    ABARROTES = 'AB'
    LIMPIEZA = 'LI'
    LICORES = 'LC'
    VEGETALES = 'VE'
    OTROS = 'OT'
    CATEGORY_CHOICES = [
        (EMBUTIDOS, 'Embutidos'),
        (LACTEOS, 'Lácteos'),
        (ABARROTES, 'Abarrotes'),
        (LIMPIEZA, 'Limpieza'),
        (LICORES, 'Licores'),
        (VEGETALES, 'Vegetales') ,
        (OTROS, 'Otros'),
    ]
    product_category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default=OTROS,
    )

    #product_ID  = AutoField() # id automatic gnerated
    product_title = models.CharField(max_length=100)
    product_introduced = models.DateTimeField(default=timezone.now())
    product_description = models.TextField(default='noDescription')
    product_status = models.BooleanField(null=False) # if it is currently being offered
    product_photo_full = models.CharField(max_length=200, default='noPhoto') # Link to large size photos
    product_photo_mid = models.CharField(max_length=200, default='noPhoto') # Link to mid size photos
    product_photo_small = models.CharField(max_length=200, default='noPhoto') # Link to small size photos

    # This is to change what is display when self referencing.
    # It displays the product title instead of making a list of objects.
    def __str__(self):
        return self.product_title

    