# Generated by Django 3.1.5 on 2021-03-26 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_auto_20210326_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagedisk',
            name='type',
            field=models.CharField(choices=[('qcow2', 'qcow2'), ('vhd', 'vhd')], default=None, max_length=30),
            preserve_default=False,
        ),
    ]
