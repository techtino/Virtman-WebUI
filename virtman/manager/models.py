from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    state = models.CharField(max_length=3)
    storage_disk = models.ForeignKey(StorageDisk, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    advanced_mode = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()