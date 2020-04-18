# Generated by Django 2.1.15 on 2020-04-17 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productos_aprobados',
            name='product_photo_mid',
            field=models.CharField(default='noPhoto', max_length=200),
        ),
        migrations.AddField(
            model_name='productos_aprobados',
            name='product_photo_small',
            field=models.CharField(default='noPhoto', max_length=200),
        ),
        migrations.AlterField(
            model_name='productos_aprobados',
            name='product_description',
            field=models.TextField(default='noDescription'),
        ),
        migrations.AlterField(
            model_name='productos_aprobados',
            name='product_photo_full',
            field=models.CharField(default='noPhoto', max_length=200),
        ),
    ]
