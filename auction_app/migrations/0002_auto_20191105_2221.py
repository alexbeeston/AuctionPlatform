# Generated by Django 2.2.6 on 2019-11-06 05:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liveitem',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 5, 22, 21, 6, 520070), verbose_name=datetime.datetime(2019, 11, 5, 22, 21, 6, 520070)),
        ),
        migrations.AlterField(
            model_name='silentitem',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 5, 22, 21, 6, 520070), verbose_name=datetime.datetime(2019, 11, 5, 22, 21, 6, 520070)),
        ),
    ]