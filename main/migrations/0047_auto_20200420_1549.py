# Generated by Django 3.0.5 on 2020-04-20 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20200420_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listadeproductos',
            name='ldp_Cod',
            field=models.CharField(default='000000', max_length=6, verbose_name='Código de listado'),
        ),
    ]
