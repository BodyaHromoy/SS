# Generated by Django 5.0.4 on 2024-09-13 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0011_cell_last_sn'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='last_sn_is_error',
            field=models.BooleanField(default=False, verbose_name='LAST_SN_IS_ERROR'),
        ),
    ]
