# Generated by Django 3.0.5 on 2020-04-18 18:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20200418_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productos_aprobados',
            name='product_introduced',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 18, 18, 10, 33, 65191, tzinfo=utc)),
        ),
    ]
