# Generated by Django 3.1.5 on 2021-02-01 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='stock',
        ),
    ]
