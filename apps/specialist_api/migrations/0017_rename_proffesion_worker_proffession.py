# Generated by Django 4.0 on 2022-07-14 02:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('specialist_api', '0016_worker_proffesion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='worker',
            old_name='proffesion',
            new_name='proffession',
        ),
    ]
