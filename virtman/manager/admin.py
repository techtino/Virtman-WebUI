from django.contrib import admin

# Register your models here.

from .models import VM 

from .models import StorageDisk 
admin.site.register(VM)
admin.site.register(StorageDisk)