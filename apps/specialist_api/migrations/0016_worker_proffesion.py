# Generated by Django 4.0 on 2022-07-12 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specialist_api', '0015_alter_worker_appointments_alter_worker_schedules_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='proffesion',
            field=models.CharField(default='Dentist', max_length=128),
            preserve_default=False,
        ),
    ]
