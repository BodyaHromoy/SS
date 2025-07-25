# Generated by Django 5.1.8 on 2025-07-10 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0021_cabinet_sticker'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabinet',
            name='device_vendor',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='energy_counter_sn',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='iot_imei_locker',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='iot_imei_rpi',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='mobile_n_locker',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='mobile_n_rpi',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='n_inventar',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='qr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='cabinet',
            name='smoke_state',
            field=models.BooleanField(default=False),
        ),
    ]
