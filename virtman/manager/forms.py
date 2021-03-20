from django import forms
from django.forms import ModelForm
from django.forms import inlineformset_factory
from .models import VM
from .models import StorageDisk

class VMForm(ModelForm):
    class Meta:
        model = VM
        fields = "__all__"

class storageForm(ModelForm):
    class Meta:
        model = StorageDisk
        fields = "__all__"

class isoForm(forms.Form):
    file = forms.FileField()
