# Generated by Django 5.0.4 on 2024-09-24 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0017_remove_cell_last_sn_remove_cell_last_sn_is_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='cell',
            name='message',
            field=models.CharField(max_length=255, null=True, verbose_name='MESSAGE'),
        ),
    ]
