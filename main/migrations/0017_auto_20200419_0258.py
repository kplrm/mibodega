# Generated by Django 3.0.5 on 2020-04-19 00:58

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20200419_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='productosaprobados',
            name='pa_rating',
            field=models.IntegerField(default='0', verbose_name='Calificación (0-5)'),
        ),
        migrations.AlterField(
            model_name='productosaprobados',
            name='pa_introduced',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 19, 0, 58, 46, 429689, tzinfo=utc), verbose_name='Fecha de introducción'),
        ),
    ]
