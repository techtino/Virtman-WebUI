from django.db import models

# Create your models here.

class StorageDisk(models.Model):
    def _str_(self):
        return self.path
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=30)
    size = models.IntegerField()
    pass

class VM(models.Model):
    def _str_(self):
        return self.name
    name = models.CharField(max_length=30)
    cpus = models.IntegerField()
    ram = models.IntegerField()
    HYPERVISOR_CHOICES = (
        ('QEMU', 'QEMU'),
        ('Virtualbox', 'Virtualbox'),
        ('VMWare', 'VMWare'),)
    hypervisor = models.CharField(max_length=30,choices=HYPERVISOR_CHOICES)
    OS = (
        ('Linux', 'Linux'),
        ('Windows', 'Windows'),
        ('Mac', 'Mac'),)
    os = models.CharField(max_length=30,choices=OS)
    xml = models.CharField(max_length=100)
    storage_disk = models.ForeignKey(StorageDisk, on_delete=models.CASCADE)