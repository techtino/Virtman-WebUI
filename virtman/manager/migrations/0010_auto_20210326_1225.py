# Generated by Django 3.1.5 on 2021-03-26 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0009_auto_20210326_1221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opticaldisk',
            old_name='ImageFile',
            new_name='ISOFile',
        ),
    ]
