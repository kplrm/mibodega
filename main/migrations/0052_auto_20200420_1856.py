# Generated by Django 3.0.5 on 2020-04-20 16:56

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20200420_1716'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='listadeproductos',
            options={'verbose_name_plural': 'Listas de productos'},
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_discount_price',
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_discount_rate',
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_discount_status',
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_product',
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_regular_price',
        ),
        migrations.RemoveField(
            model_name='listadeproductos',
            name='ldp_status',
        ),
        migrations.AlterField(
            model_name='basket',
            name='bkt_ID',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Cesta'),
        ),
        migrations.AlterField(
            model_name='bodega',
            name='bd_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre comercial'),
        ),
        migrations.AlterField(
            model_name='bodega',
            name='bd_raz_soc',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Razón social'),
        ),
        migrations.AlterField(
            model_name='bodega',
            name='bd_ruc',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='RUC'),
        ),
        migrations.AlterField(
            model_name='listadeproductos',
            name='ldp_cod',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Bodega', verbose_name='Código de lista'),
        ),
        migrations.AlterField(
            model_name='listadeproductos',
            name='lpd_ID',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Lista de productos'),
        ),
        migrations.CreateModel(
            name='Listado',
            fields=[
                ('lp_ID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Listado')),
                ('ld_regular_price', models.FloatField(verbose_name='Precio regular')),
                ('ld_discount_price', models.FloatField(blank=True, null=True, verbose_name='Precio con descuento')),
                ('ld_discount_status', models.BooleanField(default=False, verbose_name='Vender con el descuento')),
                ('ld_discount_rate', models.FloatField(default=0, verbose_name="'%' de descuento")),
                ('ld_status', models.BooleanField(default=True, verbose_name='Disponible')),
                ('ld_cod', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.ListaDeProductos', verbose_name='Código de listado')),
                ('ld_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ProductosAprobados', verbose_name='Producto')),
            ],
            options={
                'verbose_name_plural': 'Listados',
            },
        ),
    ]
