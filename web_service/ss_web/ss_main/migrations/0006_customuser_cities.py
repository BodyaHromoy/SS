# Generated by Django 5.0.4 on 2024-07-03 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_main', '0005_remove_city_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cities',
            field=models.ManyToManyField(blank=True, help_text='The cities this user is associated with.', related_name='users', to='ss_main.city'),
        ),
    ]