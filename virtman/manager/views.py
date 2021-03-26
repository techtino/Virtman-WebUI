from .models import VM
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from . import LibvirtManagement
from .forms import VMForm, storageForm, isoForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory

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
    context = {
        'VM_list': VM_list,
    }

    if request.method == "POST":
        IDs = request.POST.getlist('VMs')
        for id in IDs:
            VM.objects.filter(id=id).delete()
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

@login_required
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

@login_required
def uploadISO(request):
    if request.method == 'POST':
        form = isoForm(request.POST, request.FILES)
        if form.is_valid():
            LibvirtManagement.handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/manager/listing')
    else:
        form = isoForm()
    return render(request, 'isoUpload.html', {'form': form})

@login_required
def edit(request,id):
    instance = get_object_or_404(VM, id=id)
    form = VMForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        vm_name = VM.objects.get(id=id).name
        LibvirtManagement.delXML(vm_name)
        vm_info = form.cleaned_data
        LibvirtManagement.createQemuXML(vm_info)

        return redirect('/manager/listing')
    return render(request, 'edit.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)

@login_required
def startVM_View(request,id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    LibvirtManagement.startQemuVM(machine)
    VM.objects.filter(id=id).update(state='ON')
    return redirect('/manager/listing')

@login_required
def stopVM_View(request,id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    action = "forceoff"
    LibvirtManagement.stopVM(name, action)
    VM.objects.filter(id=id).update(state='OFF')
    return redirect('/manager/listing')

@login_required
def AdvancedMode(request):
    userid = request.user.id
    user = User.objects.get(pk=userid)
    if user.profile.advanced_mode == False:
        user.profile.advanced_mode = True
    else:
        user.profile.advanced_mode = False 
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def shutdownVM(request, id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    action = "shutdown"
    LibvirtManagement.stopVM(name, action)
    VM.objects.filter(id=id).update(state='OFF')
    return redirect('/manager/listing')

@login_required
def restartVM(request, id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    action = "reset"
    LibvirtManagement.stopVM(name, action)
    return redirect('/manager/listing')

@login_required
def viewStatsPerVM(request,id):
    get_object_or_404(VM, id=id)
    machine = VM.objects.get(id=id)
    name = machine.name
    cpu_stats = LibvirtManagement.getGuestCPUStats(name)
    disk_stats = LibvirtManagement.getDiskStats(name)
    memory_stats = LibvirtManagement.getMemoryStats(name)
    context = {
        'cpu_stats': cpu_stats,
        'disk_stats': disk_stats,
        'memory_stats': memory_stats
    }
    template = loader.get_template('stats.html')
    return HttpResponse(template.render(context, request))

@login_required
def viewHostStats(request):
    cpu_usage = LibvirtManagement.getHostCPUStats()
    mem_usage = LibvirtManagement.getHostMemoryStats()

    mem_percent = mem_usage['free'] / mem_usage['total'] * 100

    context = {
        'cpu_usage': cpu_usage,
        'mem_usage': mem_percent,
    }
    template = loader.get_template('host_stats.html')
    return HttpResponse(template.render(context, request))