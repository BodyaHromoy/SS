# Generated by Django 5.0.4 on 2024-07-03 03:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0003_city_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='users',
            field=models.ManyToManyField(related_name='citys', to=settings.AUTH_USER_MODEL),
        ),
    ]