# Generated by Django 3.0.5 on 2020-05-08 14:27

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bodega',
            fields=[
                ('bd_ID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Bodega')),
                ('bd_is_active', models.BooleanField(default=True, verbose_name='¿Está activo?')),
                ('bd_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre comercial')),
                ('bd_ruc', models.CharField(max_length=11, unique=True, verbose_name='RUC (o DNI)')),
                ('bd_raz_soc', models.CharField(blank=True, max_length=100, null=True, verbose_name='Razón social')),
                ('bd_geolocation', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Sede')),
            ],
        ),
        migrations.CreateModel(
            name='ProductosAprobados',
            fields=[
                ('pa_ID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Producto')),
                ('pa_product', models.CharField(default='', max_length=100, verbose_name='Producto')),
                ('pa_category', models.CharField(choices=[('embutidos', 'Embutidos'), ('lacteos', 'Lácteos'), ('abarrotes', 'Abarrotes'), ('limpieza', 'Limpieza'), ('licores', 'Licores'), ('vegetales', 'Vegetales'), ('otros', 'Otros')], default='otros', max_length=10, verbose_name='Categoría')),
                ('pa_brand', models.CharField(default='', max_length=100, verbose_name='Marca')),
                ('pa_introduced', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de introducción')),
                ('pa_description', models.TextField(default='sinDsescripción', verbose_name='Descripción')),
                ('pa_rating', models.IntegerField(default='0', verbose_name='Calificación (0-5)')),
                ('pa_status', models.BooleanField(default=True, verbose_name='Activo')),
                ('pa_photo_full', models.CharField(blank=True, default='noPhoto', max_length=200, verbose_name='Foto grande')),
                ('pa_photo_mid', models.CharField(blank=True, default='noPhoto', max_length=200, verbose_name='Foto mediana')),
                ('pa_photo_small', models.CharField(blank=True, default='noPhoto', max_length=200, verbose_name='Foto pequeña')),
                ('pa_reg_sanitario', models.CharField(blank=True, default='', max_length=100, verbose_name='Registro sanitario')),
            ],
            options={
                'verbose_name_plural': 'Productos aprobados',
            },
        ),
        migrations.CreateModel(
            name='ProductosEnBodega',
            fields=[
                ('peb_ID', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='ID Productos en bodegas')),
                ('peb_regular_price', models.FloatField(default=0, verbose_name='Precio regular')),
                ('peb_discount_price', models.FloatField(blank=True, default='', null=True, verbose_name='Precio con descuento')),
                ('peb_discount_status', models.BooleanField(default=False, verbose_name='Vender con descuento')),
                ('peb_discount_rate', models.FloatField(default=0, editable=False, verbose_name="'%' de descuento")),
                ('peb_status', models.BooleanField(default=True, verbose_name='Disponible')),
                ('peb_slug', models.SlugField(allow_unicode=True, editable=False, max_length=100, unique=True)),
                ('peb_bodega', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='main.Bodega', verbose_name='Bodega')),
                ('peb_product', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='main.ProductosAprobados', verbose_name='Producto')),
            ],
            options={
                'verbose_name_plural': 'Productos en bodegas',
                'unique_together': {('peb_bodega', 'peb_product')},
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('cl_ID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID Cliente')),
                ('cl_first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nombre')),
                ('cl_last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Apellido')),
                ('cl_phone', models.CharField(max_length=9, null=True, verbose_name='Celular')),
                ('cl_email', models.CharField(blank=True, max_length=50, null=True, verbose_name='E-mail')),
                ('cl_address', models.CharField(blank=True, max_length=50, null=True, verbose_name='Dirreción')),
                ('cl_geolocation', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Ubicación')),
                ('cl_date_reg', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')),
                ('cl_bodega_ID', models.CharField(blank=True, default='', max_length=36, null=True, verbose_name='ID Bodega')),
                ('cl_user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Cliente (usuario)')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ci_cart_ID', models.IntegerField(default=0, verbose_name='ID Cart ID')),
                ('ci_quantity', models.IntegerField(default=1)),
                ('ci_date_updated', models.DateTimeField(auto_now=True)),
                ('ci_date_created', models.DateTimeField(auto_now_add=True)),
                ('ci_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ProductosEnBodega', verbose_name='Producto')),
                ('ci_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ID Usuario')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('crt_ID', models.AutoField(editable=False, primary_key=True, serialize=False, verbose_name='ID Cart')),
                ('crt_total_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True)),
                ('crt_date_updated', models.DateTimeField(auto_now=True)),
                ('crt_date_created', models.DateTimeField(auto_now_add=True)),
                ('crt_ordered', models.BooleanField(default=False, verbose_name='¿Ordered?')),
                ('crt_item', models.ManyToManyField(blank=True, to='main.CartItem', verbose_name='Item')),
                ('crt_product', models.ManyToManyField(blank=True, to='main.ProductosEnBodega', verbose_name='Producto')),
                ('crt_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ID Usuario')),
            ],
        ),
        migrations.AddField(
            model_name='bodega',
            name='bd_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Cliente', verbose_name='Usuario'),
        ),
    ]
