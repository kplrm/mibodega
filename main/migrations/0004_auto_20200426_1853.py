# Generated by Django 3.0.5 on 2020-04-26 16:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0003_auto_20200425_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='crt_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ID Usuario'),
        ),
    ]
