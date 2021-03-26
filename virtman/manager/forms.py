from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from .models import VM, StorageDisk

class VMForm(ModelForm):
    class Meta:
        model = VM
        fields = ['name', 'cpus', 'ram', 'hypervisor', 'os', 'storage_disk']

class AdvancedVMForm(ModelForm):
    class Meta:
        model = VM
        fields = ['name', 'cpus', 'ram', 'hypervisor', 'os', 'storage_disk']

class storageForm(ModelForm):
    class Meta:
        model = StorageDisk
        fields = "__all__"

class isoForm(forms.Form):
    file = forms.FileField()