# Generated by Django 3.0.5 on 2020-04-20 13:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_basket_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='listadeproductos',
            name='ldp_Cod',
            field=models.CharField(default='000000', max_length=6, unique=True, verbose_name='Código de listado'),
        ),
        migrations.AlterField(
            model_name='basket',
            name='bkt_product',
            field=models.ManyToManyField(to='main.ListaDeProductos', verbose_name='Producto'),
        ),
        migrations.AlterField(
            model_name='basket',
            name='bkt_quantity',
            field=models.IntegerField(default=1, verbose_name='Cantidad'),
        ),
        migrations.AlterField(
            model_name='listadeproductos',
            name='ldp_ID',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
