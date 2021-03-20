from .models import VM
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from . import LibvirtManagement
from .forms import VMForm
from .forms import storageForm
from .forms import isoForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory
from .LibvirtManagement import handle_uploaded_file

def home(request):
    template = loader.get_template('index.html')
    username = request.user.get_username()

    context = {
        'username': username,
    }
    return HttpResponse(template.render(context, request))

@login_required
def listing(request):
    # pylint: disable=no-member
    VM_list = VM.objects.order_by('id')[:40]
    template = loader.get_template('listing.html')
    username = request.user.get_username()
    context = {
        'VM_list': VM_list,
        'username': username,
    }
    return HttpResponse(template.render(context, request))

@login_required
def add(request):
    if request.method == "POST":
        form = VMForm(request.POST)
        if form.is_valid():
           form.save()
           vm_info = form.cleaned_data
           LibvirtManagement.createQemuXML(vm_info)

           return redirect('/manager/listing')
    else:
        form = VMForm()
        return render(request, 'add.html', {'form': form})

def createDisk(request):
    if request.method == "POST":
        form = storageForm(request.POST)
        if form.is_valid():
           form.save()
           disk_info = form.cleaned_data
           LibvirtManagement.CreateStorageDrive(disk_info)
           return redirect('/manager/listing')
    else:
        form = storageForm()
        return render(request, 'createDisk.html', {'form': form})

def uploadISO(request):
    if request.method == 'POST':
        form = isoForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/manager/listing')
    else:
        print("fail")
        form = isoForm()
    return render(request, 'isoUpload.html', {'form': form})

@login_required
def edit(request,id):
    instance = get_object_or_404(VM, id=id)
    form = VMForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        

        return redirect('/manager/listing')
    return render(request, 'edit.html', {'form': form})

@login_required
def delete(request,id):
    instance = get_object_or_404(VM, id=id)
    instance.delete()
    return redirect('/manager/listing')

@login_required
def logout_view(request):
    logout(request)

@login_required
def startVM_View(request,id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    cpus = machine.cpus
    RAM = machine.ram
    drivePath = machine.storage_disk.path
    driveName = machine.storage_disk.name
    
    #LibvirtManagement.createQemuXML(name, cpus, RAM, drivePath, driveName)
    return redirect('/manager/listing')

@login_required
def stopVM_View(request,id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    
    LibvirtManagement.shutdownVM(name)
    return redirect('/manager/listing')