# Generated by Django 3.1.5 on 2021-03-26 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0011_storagedisk_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagedisk',
            name='type',
            field=models.CharField(max_length=30),
        ),
    ]