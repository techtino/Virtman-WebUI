from .models import VM, customVM, OpticalDisk, StorageDisk, container
from django.contrib.auth.models import User
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from . import LibvirtManagement
from .forms import VMForm, storageForm, StorageUploadForm, isoForm, XMLForm, ContainerForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory
import os
import psutil
import socket
import shutil

def home(request):
    template = loader.get_template('index.html')
    username = request.user.get_username()

    context = {
        'username': username,
    }
    return HttpResponse(template.render(context, request))

def ISOPage(request):
    template = loader.get_template('ISO.html')
    ISO_list = OpticalDisk.objects.order_by('id')[:40]
    username = request.user.get_username()
    context = {
            'username': username,
            'ISO_list': ISO_list,
        }
    if request.method == "POST":
        IDs = request.POST.getlist('ISOs')
        for id in IDs:
            ISO = OpticalDisk.objects.get(id=id)
            ISO.delete()
    return HttpResponse(template.render(context, request))

def DiskPage(request):
    template = loader.get_template('Disk.html')
    Disk_list = StorageDisk.objects.order_by('id')[:40]
    username = request.user.get_username()
    context = {
            'username': username,
            'Disk_list': Disk_list,
        }
    if request.method == "POST":
        IDs = request.POST.getlist('Disks')
        for id in IDs:
            Disk = StorageDisk.objects.get(id=id)
            LibvirtManagement.delDisk(Disk)
            Disk.delete()

    return HttpResponse(template.render(context, request))

@login_required
def listing(request):
    # pylint: disable=no-member
    
    # get list of virtual machines for page to use
    VM_list = VM.objects.order_by('id')[:40]
    # sets template to listing.html
    template = loader.get_template('listing.html')

    # get hostname (for vnc)
    ip = socket.gethostname()

    # vm list for advanced vms
    custom_VM_list = customVM.objects.order_by('id')[:40]

    # provide context to listing page, both standard and advanced vms and IP
    context = {
        'VM_list': VM_list,
        'ip': ip,
        'customVM_list' : custom_VM_list,
    }

    # If POSTing, get list of VMS delete VM from libvirt/vmware, then delete the object. this is identical for basic and advanced vms
    if request.method == "POST":
        IDs = request.POST.getlist('VMs')
        for id in IDs:
            VirtualMachine = VM.objects.get(id=id)
            LibvirtManagement.delVM(VirtualMachine)
            VirtualMachine.delete()
        IDs = request.POST.getlist('customVMs')
        for id in IDs:
            VirtualMachine = customVM.objects.get(id=id)
            LibvirtManagement.delVM(VirtualMachine)
            VirtualMachine.delete()
    return HttpResponse(template.render(context, request))

@login_required
def containers(request):
    print("hello")
    # get list of virtual machines for page to use
    container_list = container.objects.order_by('id')[:40]
    # sets template to listing.html
    template = loader.get_template('Containers.html')

    # provide context to listing page, both standard and advanced vms and IP
    context = {
        'container_list': container_list,
    }

    # If POSTing, get list of VMS delete VM from libvirt/vmware, then delete the object. this is identical for basic and advanced vms
    if request.method == "POST":
        IDs = request.POST.getlist('Containers')
        for id in IDs:
            LXCContainer = container.objects.get(id=id)
            LibvirtManagement.delVM(LXCContainer)
            LXCContainer.delete()
    return HttpResponse(template.render(context, request))

def addContainer(request):
    if request.method == "POST":
        form = ContainerForm(request.POST)
        if form.is_valid():
            container_info = form.cleaned_data
            LibvirtManagement.createLXCXML(container_info)
            form.save()
    else:
        form = ContainerForm()
        return render(request, 'form.html', {'form': form})

    return redirect('/manager/containers')
@login_required
def add(request):

    # If user is in advanced mode, serve XMLForm (more control, custom XML)
    if request.user.profile.advanced_mode:
        # If posting, set XML form and save data if valid, then create custom VM, if incorrect then load page again
        if request.method == "POST":
            form = XMLForm(request.POST)
            if form.is_valid():
                vmXML = form.cleaned_data['content']
                LibvirtManagement.createCustomVM(vmXML)
                form.save()
                return redirect('/manager/listing')
        # render form page if GET request
        else:
            form = XMLForm()
            return render(request, 'form.html', {'form': form})
    
    # if user is not in advanced mode, serve standard VM form
    else:
        # If posting, save data and run creation function based on hypervisor
        if request.method == "POST":
            form = VMForm(request.POST)
            if form.is_valid():
                vm_info = form.cleaned_data
                if vm_info['hypervisor'] == "QEMU":
                    LibvirtManagement.createQemuXML(vm_info)
                elif vm_info['hypervisor'] == "Virtualbox":
                    LibvirtManagement.createVirtualboxXML(vm_info)
                elif vm_info['hypervisor'] == "VMWare":
                    LibvirtManagement.createVMWareXML(vm_info)
                form.save()
                return redirect('/manager/listing')
        
        # Display form if GETting
        else:
            form = VMForm()
            return render(request, 'form.html', {'form': form})

@login_required
def createDisk(request):

    # if request is POST, set form and save data if valid, then create storage drive using data
    if request.method == "POST":
        form = storageForm(request.POST)
        if form.is_valid():
           disk_info = form.cleaned_data
           LibvirtManagement.CreateStorageDrive(disk_info)
           form.save()
           return redirect('/manager/listing')
    else:
        # render disk creation form
        form = storageForm()
        return render(request, 'form.html', {'form': form})

@login_required
def uploadISO(request):

    # if POSTing save file and details to disk
    if request.method == 'POST':
        form = isoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/manager/listing')
    
    else:
        form = isoForm()
        # render isoUpload form
    return render(request, 'form.html', {'form': form})

@login_required
def uploadDisk(request):

    # if POSTing save file and details to disk
    if request.method == 'POST':
        form = StorageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/manager/listing')
    
    else:
        form = StorageUploadForm()
        # render isoUpload form
    return render(request, 'form.html', {'form': form})


@login_required
def edit(request,id):
    # check if VM exists in database, if not 404
    instance = get_object_or_404(VM, id=id)

    # sets form to use
    form = VMForm(request.POST or None, instance=instance)
    # checks if post data is valid and saves it, deletes old VM, cleans data and creates new one based on hypervisor
    if form.is_valid():
        form.save()
        vm = VM.objects.get(id=id)
        LibvirtManagement.delVM(vm)
        vm_info = form.cleaned_data

        # depending on hypervisor, run specific creation command
        if vm_info['hypervisor'] == "QEMU":
            LibvirtManagement.createQemuXML(vm_info)
        elif vm_info['hypervisor'] == "Virtualbox":
            LibvirtManagement.createVirtualboxXML(vm_info)
        elif vm_info['hypervisor'] == "VMWare":
            LibvirtManagement.createVMWareXML(vm_info)
        return redirect('/manager/listing')
    return render(request, 'form.html', {'form': form})

@login_required
def customEdit(request,id):
    instance = get_object_or_404(customVM, id=id)
    form = XMLForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        vm = customVM.objects.get(id=id)
        LibvirtManagement.delVM(vm)
        vm_info = form.cleaned_data
        if vm_info['hypervisor'] == "QEMU":
            LibvirtManagement.createQemuXML(vm_info)
        elif vm_info['hypervisor'] == "Virtualbox":
            LibvirtManagement.createVirtualboxXML(vm_info)
        return redirect('/manager/listing')
    return render(request, 'form.html', {'form': form})

@login_required
def logout_view(request):
    # call upon djangos default logout functionality, redirects to same page
    logout(request)

@login_required
def startVM_View(request,id):
    get_object_or_404(VM, id=id)
    machine = VM.objects.get(id=id)
    # pylint: disable=no-member
    LibvirtManagement.startVM(machine)
    VM.objects.filter(id=id).update(state='ON')
    return redirect('/manager/listing')

@login_required
def startContainer(request,id):
    get_object_or_404(container, id=id)
    machine = container.objects.get(id=id)
    # pylint: disable=no-member
    LibvirtManagement.startVM(machine)
    container.objects.filter(id=id).update(state='ON')
    return redirect('/manager/containers')

@login_required
def startcustomVM_View(request,id):
    get_object_or_404(customVM, id=id)
    # pylint: disable=no-member
    machine = customVM.objects.get(id=id)
    LibvirtManagement.startVM(machine)
    customVM.objects.filter(id=id).update(state='ON')
    return redirect('/manager/listing')

@login_required
def stopVM_View(request,id):

    # check if VM exists in database, if not 404
    get_object_or_404(VM, id=id)
    machine = VM.objects.get(id=id)
    action = "forceoff"

    # runs stopVM function with action specified
    LibvirtManagement.stopVM(machine, action)

    # sets state to off in GUI
    VM.objects.filter(id=id).update(state='OFF')
    return redirect('/manager/listing')

@login_required
def stopContainer(request,id):

    # check if container exists in database, if not 404
    get_object_or_404(container, id=id)
    machine = container.objects.get(id=id)
    action = "forceoff"
    # runs stopVM function with action specified
    LibvirtManagement.stopVM(machine, action)

    container.objects.filter(id=id).update(state='OFF')
    return redirect('/manager/containers')

@login_required
def AdvancedMode(request):
    
    # gets user id, if user is in advanced mode, set value to false, otherwise set to true.
    userid = request.user.id
    user = User.objects.get(pk=userid)
    if user.profile.advanced_mode == False:
        user.profile.advanced_mode = True
    else:
        user.profile.advanced_mode = False 
    # save data
    user.save()

    # return user to same previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def stopcustomVM_View(request,id):
    get_object_or_404(customVM, id=id)
    # pylint: disable=no-member
    machine = customVM.objects.get(id=id)
    action = "forceoff"
    LibvirtManagement.stopVM(machine, action)
    customVM.objects.filter(id=id).update(state='OFF')
    return redirect('/manager/listing')

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
def shutdowncustomVM(request, id):
    get_object_or_404(customVM, id=id)
    # pylint: disable=no-member
    machine = customVM.objects.get(id=id)
    action = "shutdown"
    LibvirtManagement.stopVM(machine, action)
    customVM.objects.filter(id=id).update(state='OFF')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def restartcustomVM(request, id):
    get_object_or_404(customVM, id=id)
    # pylint: disable=no-member
    machine = customVM.objects.get(id=id)
    action = "reset"
    LibvirtManagement.stopVM(machine, action)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def viewStatsPerVM(request,id):

    # get variety of stats for vm, qemu only functionality for now
    get_object_or_404(VM, id=id)
    machine = VM.objects.get(id=id)
    
    cpu_stats = LibvirtManagement.getGuestCPUStats(machine)
    disk_stats = LibvirtManagement.getDiskStats(machine)
    memory_stats = LibvirtManagement.getMemoryStats(machine)
    network_stats = LibvirtManagement.getNetworkStats(machine)
    # calculate memory utilisation percentage by difference of ram / total
    try:
        free_mem = float(memory_stats['unused'])
        total_mem = float(memory_stats['available'])
        util_mem = ((total_mem-free_mem) / total_mem)*100
    except:
        util_mem = 0
    
    context = {
        'cpu_stats': cpu_stats,
        'disk_stats': disk_stats,
        'memory_stats': memory_stats,
        'memory_usage': util_mem,
        'network_stats': network_stats,
    }
    template = loader.get_template('stats.html')
    return HttpResponse(template.render(context, request))

@login_required
def viewStatsPerCustomVM(request,id):
    get_object_or_404(customVM, id=id)
    machine = customVM.objects.get(id=id)
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
    # Get percentage of memory used by host with psutil
    mem_percent = psutil.virtual_memory()[2]

    disk_usage = round(shutil.disk_usage("/")[1] / shutil.disk_usage("/")[0] * 100)
    context = {
        'cpu_usage': cpu_usage,
        'mem_usage': mem_percent,
        'disk_usage': disk_usage,
    }
    template = loader.get_template('host_stats.html')
    return HttpResponse(template.render(context, request))

@login_required
def vnc_proxy_http(request,id):

    # get the vnc port to connect to per hypervisor
    machine = get_object_or_404(VM, id=id)
    VMport = LibvirtManagement.getVNCPort(machine)

    # run websockify using command line with idle timeout and VM port on localhost
    os.system("./statics/novnc/utils/launch.sh --idle-timeout 15 --vnc localhost:" + VMport + " &")
    template = loader.get_template('novnc/vnc.html')
    context = {
        'vm': machine,
    }
    return HttpResponse(template.render(context, request))

@login_required
def profilePage(request):
    template = loader.get_template('profile.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def customvnc_proxy_http(request,id):
    machine = get_object_or_404(customVM, id=id)
    VMport = LibvirtManagement.getVNCPort(machine)
    os.system("./statics/novnc/utils/launch.sh --idle-timeout 15 --vnc localhost:" + VMport + " &")
    template = loader.get_template('novnc/customvnc.html')
    context = {
        'vm': machine,
    }
    return HttpResponse(template.render(context, request))