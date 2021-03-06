# Generated by Django 3.0.3 on 2020-11-30 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0032_auto_20201129_0827'),
    ]

    operations = [
        migrations.CreateModel(
            name='Correlation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comparand', models.CharField(max_length=10, null=True)),
                ('rvalue', models.FloatField(null=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Stock')),
            ],
        ),
    ]
