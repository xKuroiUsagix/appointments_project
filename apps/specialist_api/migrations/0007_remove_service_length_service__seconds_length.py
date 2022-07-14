# Generated by Django 4.0 on 2022-07-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specialist_api', '0006_remove_service__seconds_length_service_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='length',
        ),
        migrations.AddField(
            model_name='service',
            name='_seconds_length',
            field=models.FloatField(default=1200, verbose_name='length'),
            preserve_default=False,
        ),
    ]
