# Generated by Django 5.0.4 on 2024-07-03 03:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0002_alter_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='users',
            field=models.ManyToManyField(related_name='cities', to=settings.AUTH_USER_MODEL),
        ),
    ]
