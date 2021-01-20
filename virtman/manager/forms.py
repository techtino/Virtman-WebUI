from django import forms
from django.forms import ModelForm
from .models import VM

class VMForm(ModelForm):
    #name = forms.CharField(label='Name', max_length=100)
    #vm_id = forms.IntegerField(label='VM_ID')
    #cpus = forms.IntegerField(label='CPUs')
    #ram = forms.IntegerField(label='RAM')
    #hypervisor = forms.CharField(label='Hypervisor')
    class Meta:
        model = VM
        fields = "__all__"