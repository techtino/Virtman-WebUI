from django import forms
from django.forms import ModelForm, Textarea
from django.forms import inlineformset_factory
from .models import VM, StorageDisk, OpticalDisk, customVM, container, UploadedDisk

class VMForm(ModelForm):
    class Meta:
        model = VM
        fields = ['name', 'cpus', 'ram', 'hypervisor', 'os', 'storage_disk', 'optical_disk']

class storageForm(ModelForm):
    class Meta:
        model = StorageDisk
        fields = "__all__"

class StorageUploadForm(ModelForm):
    class Meta:
        model = UploadedDisk
        fields = "__all__"



class isoForm(ModelForm):
    class Meta:
        model = OpticalDisk
        fields = "__all__"

class ContainerForm(ModelForm):
    class Meta:
        model = container
        fields = ['name', 'cpus', 'ram', 'app']

class XMLForm(ModelForm):
    class Meta:
        model = customVM
        fields = ['name','hypervisor','content']
        widgets = {
            'content': Textarea(attrs={'cols': 80, 'rows': 100}),
        }