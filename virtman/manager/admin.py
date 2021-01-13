from django.contrib import admin

# Register your models here.

from .models import VM 

from .models import Storage 
admin.site.register(VM)
admin.site.register(Storage)