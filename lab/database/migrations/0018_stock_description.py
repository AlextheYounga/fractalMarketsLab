# Generated by Django 3.0.3 on 2020-10-27 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0017_auto_20201027_0400'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
