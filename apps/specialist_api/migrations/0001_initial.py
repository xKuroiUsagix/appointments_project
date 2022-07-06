# Generated by Django 4.0 on 2022-07-05 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=128)),
                ('street', models.CharField(max_length=128)),
                ('street_number', models.CharField(max_length=64)),
                ('appartment_address', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.SmallIntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.location')),
            ],
            options={
                'db_table': 'schedule',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('price', models.PositiveIntegerField()),
                ('currency', models.CharField(choices=[('USD', 'United States Dollar'), ('EUR', 'Euro'), ('GBP', 'Great Britain Pound'), ('JPY', 'Japanese Yen'), ('CNY', 'Chinese Yuan'), ('UAH', 'Ukrainian Hryvnia')], max_length=3)),
                ('seconds_length', models.FloatField(verbose_name='seconds length')),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('surname', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'worker',
            },
        ),
        migrations.CreateModel(
            name='WorkerService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.service')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.worker')),
            ],
        ),
        migrations.AddField(
            model_name='worker',
            name='services',
            field=models.ManyToManyField(related_name='services', through='specialist_api.WorkerService', to='specialist_api.Service'),
        ),
        migrations.AddField(
            model_name='worker',
            name='work_schedule',
            field=models.ManyToManyField(through='specialist_api.Schedule', to='specialist_api.Location'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.worker'),
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_for', models.DateTimeField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client_api.client')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.service')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specialist_api.worker')),
            ],
            options={
                'db_table': 'appointment',
            },
        ),
    ]
