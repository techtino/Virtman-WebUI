from django.shortcuts import render
from .models import VM
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from . import LibvirtManagement
from .forms import VMForm
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory

class HomePageView(TemplateView):
    template_name = "index.html"

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
           return redirect('/manager/listing')
    else:
        form = VMForm()
        return render(request, 'add.html', {'form': form})

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
    
    LibvirtManagement.createQemuVM(name, cpus, RAM)
    return redirect('/manager/listing')


@login_required
def stopVM_View(request,id):
    get_object_or_404(VM, id=id)
    # pylint: disable=no-member
    machine = VM.objects.get(id=id)
    name = machine.name
    
    LibvirtManagement.shutdownVM(name)
    return redirect('/manager/listing')