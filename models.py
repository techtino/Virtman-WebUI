from django.db import models

class Storage(models.model):
    path = models.CharField(max_length=30)
    device_type = models.CharField(max_length=30) 
    bus = models.CharField(max_length=30)
    size = models.IntegerField()
    pass


class VM(models.Model):
    name = models.CharField(max_length=30)
    vm_id = models.IntegerField()
    cpus = models.IntegerField()
    ram = models.IntegerField()
    hypervisor = models.CharField(max_length=30)
    os = models.CharField(max_length=30)
    xml = models.CharField(max_length=100)
    storage_device = models.ForeignKey(Storage, on_delete=models.CASCADE)