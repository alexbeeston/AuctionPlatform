# Generated by Django 2.2.6 on 2019-11-06 03:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction_app', '0003_auto_20191105_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liveitem',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 5, 20, 11, 36, 70823), verbose_name=datetime.datetime(2019, 11, 5, 20, 11, 36, 70823)),
        ),
        migrations.AlterField(
            model_name='silentitem',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2019, 11, 5, 20, 11, 36, 70823), verbose_name=datetime.datetime(2019, 11, 5, 20, 11, 36, 70823)),
        ),
    ]
