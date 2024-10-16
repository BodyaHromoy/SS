# Generated by Django 5.0.4 on 2024-10-02 05:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0018_cell_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabinet_settings_for_auto_marking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn_error', models.BooleanField(default=False, verbose_name='SN_ERROR')),
                ('year_of_manufacture', models.IntegerField(max_length=255, null=True)),
                ('max_cycle_times', models.IntegerField(max_length=255, null=True)),
                ('vid', models.CharField(max_length=255, null=True)),
                ('sw_ver', models.CharField(max_length=255, null=True)),
                ('critical_temp', models.IntegerField(max_length=255, null=True)),
                ('lock_status', models.BooleanField(default=False, verbose_name='LOCK_STATUS')),
                ('temp_inside', models.IntegerField(max_length=255, null=True)),
                ('fan_status', models.BooleanField(default=False, verbose_name='FAN_STATUS')),
                ('mains_voltage', models.CharField(max_length=255, null=True)),
                ('reserve_voltage', models.CharField(max_length=255, null=True)),
                ('cabinet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ss_main.cabinet', to_field='shkaf_id')),
            ],
        ),
    ]
