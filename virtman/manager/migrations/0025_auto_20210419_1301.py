# Generated by Django 3.1.5 on 2021-04-19 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0024_auto_20210415_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opticaldisk',
            name='ISOFile',
            field=models.FileField(upload_to='ISOs'),
        ),
        migrations.AlterField(
            model_name='storagedisk',
            name='path',
            field=models.CharField(default='~/Disks/', max_length=30),
        ),
    ]