# Generated by Django 5.0.4 on 2024-09-13 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0010_cell_is_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='last_sn',
            field=models.CharField(max_length=255, null=True, verbose_name='LAST_SN'),
        ),
    ]
