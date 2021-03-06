# Generated by Django 4.0 on 2022-07-09 16:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_api', '0003_alter_customuser_is_superuser'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('specialist_api', '0008_remove_service__seconds_length_service_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='appointments',
            field=models.ManyToManyField(blank=True, through='specialist_api.Appointment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='worker',
            name='schedules',
            field=models.ManyToManyField(blank=True, through='specialist_api.Schedule', to='specialist_api.Location'),
        ),
    ]
