from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
# Create your models here.

class StorageDisk(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=30)

    TYPE_CHOICES = (
        ('qcow2', 'qcow2'),
        ('vmdk', 'vmdk'),
    )
    type = models.CharField(max_length=30,choices=TYPE_CHOICES)
    size = models.IntegerField()

class UploadedDisk(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30)
    DiskFile = models.FileField(upload_to='Disks')

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class OpticalDisk(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30)
    ISOFile = models.FileField(upload_to='ISOs')

class VM(models.Model):
    def __str__(self):
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

    # Link fields to other models via foreign keys
    storage_disk = models.ForeignKey(StorageDisk, on_delete=models.CASCADE, blank=True, null=True)
    optical_disk = models.ForeignKey(OpticalDisk, on_delete=models.CASCADE, blank=True, null=True)

class container(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=30)
    cpus = models.IntegerField()
    ram = models.IntegerField()
    app = models.CharField(max_length=30, default="/bin/sh")
    hypervisor = models.CharField(max_length=3, default="lxc")
    state = models.CharField(max_length=3, default="OFF")

# Profile class, advanced mode state
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    advanced_mode = models.BooleanField(default=False)

# When user is created, also create profile data
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Saves profile data after creating user
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class customVM(models.Model):
    name = models.CharField(max_length=30)
    state = models.CharField(max_length=3)
    HYPERVISOR_CHOICES = (
        ('QEMU', 'QEMU'),
        ('Virtualbox', 'Virtualbox'),
        ('VMWare', 'VMWare'),)
    hypervisor = models.CharField(max_length=30,choices=HYPERVISOR_CHOICES)
    content = models.TextField()