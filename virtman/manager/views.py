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
from .forms import VMForm, storageForm, isoForm, XMLForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory
import os
import socket

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
    ip = socket.gethostname()
    context = {
        'VM_list': VM_list,
        'ip': ip,
    }

    if request.method == "POST":
        IDs = request.POST.getlist('VMs')
        for id in IDs:
            VirtualMachine = VM.objects.get(id=id)
            LibvirtManagement.delVM(VirtualMachine)
            VirtualMachine.delete()
    return HttpResponse(template.render(context, request))

@login_required
def add(request):
    if request.user.profile.advanced_mode:
        print("hello")
        form = XMLForm(request.POST)
        return render(request, 'advancedadd.html', {'form': form})
    else:
        if request.method == "POST":
            form = VMForm(request.POST)
            if form.is_valid():
                form.save()
                vm_info = form.cleaned_data
                if vm_info['hypervisor'] == "QEMU":
                    LibvirtManagement.createQemuXML(vm_info)
                elif vm_info['hypervisor'] == "Virtualbox":
                    LibvirtManagement.createVirtualboxXML(vm_info)
                return redirect('/manager/listing')
        else:
            form = VMForm()
            return render(request, 'add.html', {'form': form})

@login_required
def createDisk(request):
    if request.method == "POST":
        form = storageForm(request.POST)
        if form.is_valid():
           disk_info = form.cleaned_data
           form.save()
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
            #LibvirtManagement.handle_uploaded_file(request.FILES['file'])
            form.save()
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
        vm = VM.objects.get(id=id)
        LibvirtManagement.delVM(vm)
        vm_info = form.cleaned_data
        if vm_info['hypervisor'] == "QEMU":
            LibvirtManagement.createQemuXML(vm_info)
        elif vm_info['hypervisor'] == "Virtualbox":
            LibvirtManagement.createVirtualboxXML(vm_info)
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
    action = "forceoff"
    LibvirtManagement.stopVM(machine, action)
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
    action = "shutdown"
    LibvirtManagement.stopVM(machine, action)
    VM.objects.filter(id=id).update(state='OFF')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def restartVM(request, id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    action = "reset"
    LibvirtManagement.stopVM(machine, action)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def viewStatsPerVM(request,id):
    get_object_or_404(VM, id=id)
    machine = VM.objects.get(id=id)
    name = machine.name
    cpu_stats = LibvirtManagement.getGuestCPUStats(name)
    disk_stats = LibvirtManagement.getDiskStats(name)
    memory_stats = LibvirtManagement.getMemoryStats(name)

    free_mem = float(memory_stats['unused'])
    total_mem = float(memory_stats['available'])
    util_mem = ((total_mem-free_mem) / total_mem)*100
    
    context = {
        'cpu_stats': cpu_stats,
        'disk_stats': disk_stats,
        'memory_stats': memory_stats,
        'memory_usage': util_mem
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

@login_required
def vnc_proxy_http(request,id):
    machine = get_object_or_404(VM, id=id)
    VMport = LibvirtManagement.getVNCPort(machine)
    os.system("./statics/novnc/utils/launch.sh --idle-timeout 15 --vnc localhost:" + VMport + " &")
    template = loader.get_template('novnc/vnc.html')
    context = {
        'vm': machine,
    }
    return HttpResponse(template.render(context, request))

def profilePage(request):
    template = loader.get_template('profile.html')
    context = {}
    return HttpResponse(template.render(context, request))