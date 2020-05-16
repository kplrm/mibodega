from django.db import models
from main.models import Bodega, Cliente

# Always DecimalField for money because float has rounding issues
class BodegaDashboard(models.Model):
    bd_ID = models.OneToOneField(Bodega,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_user = models.ForeignKey(Cliente,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_daily_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_weekly_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_monthly_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_day_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_month_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_year_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)

    def __str__(self):
        return str(self.bd_ID)