from django.db import models
from main.models import Bodega, Cliente

# Always DecimalField for money because float has rounding issues
class BodegaDashboard(models.Model):
    bd_ID = models.OneToOneField(Bodega,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_user = models.ForeignKey(Cliente,null=True,on_delete=models.CASCADE,verbose_name="Usuario")
    bd_last_update = models.DateTimeField(default=None,blank=True,null=True,verbose_name="¿Last update")    

    bd_daily_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_weekly_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_monthly_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_day_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_week_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_last_month_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_daily_change_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_weekly_change_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)
    bd_monthly_change_sales = models.DecimalField(default=0.00,max_digits=10,decimal_places=2,blank=True,null=True)

    def __str__(self):
        return str(self.bd_ID)