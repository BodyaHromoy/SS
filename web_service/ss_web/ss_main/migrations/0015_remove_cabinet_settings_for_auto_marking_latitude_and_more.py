# Generated by Django 5.0.4 on 2025-03-14 01:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0014_cabinet_settings_for_auto_marking_latitude_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cabinet_settings_for_auto_marking',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='cabinet_settings_for_auto_marking',
            name='longitude',
        ),
    ]
