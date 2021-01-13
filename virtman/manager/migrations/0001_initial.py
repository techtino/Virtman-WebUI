# Generated by Django 3.1.5 on 2021-01-13 17:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=30)),
                ('device_type', models.CharField(max_length=30)),
                ('bus', models.CharField(max_length=30)),
                ('size', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='VM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('vm_id', models.IntegerField()),
                ('cpus', models.IntegerField()),
                ('ram', models.IntegerField()),
                ('hypervisor', models.CharField(max_length=30)),
                ('os', models.CharField(max_length=30)),
                ('xml', models.CharField(max_length=100)),
                ('storage_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.storage')),
            ],
        ),
    ]
