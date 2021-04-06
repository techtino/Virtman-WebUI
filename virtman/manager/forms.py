from django import forms
from django.forms import ModelForm, Textarea
from django.forms import inlineformset_factory
from .models import VM, StorageDisk, OpticalDisk, XML

class VMForm(ModelForm):
    class Meta:
        model = VM
        fields = ['name', 'cpus', 'ram', 'hypervisor', 'os', 'storage_disk', 'optical_disk']

class AdvancedVMForm(ModelForm):
    class Meta:
        model = VM
        fields = ['name', 'cpus', 'ram', 'hypervisor', 'os', 'storage_disk']

class storageForm(ModelForm):
    class Meta:
        model = StorageDisk
        fields = "__all__"

class isoForm(ModelForm):
    class Meta:
        model = OpticalDisk
        fields = "__all__"

class XMLForm(ModelForm):
    class Meta:
        model = XML
        fields = "__all__"
        widgets = {
            'content': Textarea(attrs={'cols': 80, 'rows': 100}),
        }