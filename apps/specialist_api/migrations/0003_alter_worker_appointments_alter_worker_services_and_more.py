# Generated by Django 4.0 on 2022-07-09 14:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_api', '0003_alter_customuser_is_superuser'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('specialist_api', '0002_alter_worker_appointments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='appointments',
            field=models.ManyToManyField(blank=True, through='specialist_api.Appointment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='worker',
            name='services',
            field=models.ManyToManyField(blank=True, through='specialist_api.WorkerService', to='specialist_api.Service'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='work_schedule',
            field=models.ManyToManyField(blank=True, through='specialist_api.Schedule', to='specialist_api.Location'),
        ),
    ]
