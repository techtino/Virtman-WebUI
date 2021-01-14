from django.shortcuts import render
from .models import VM
from django.template import loader
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from . import functions

class HomePageView(TemplateView):
    template_name = "index.html"

@login_required
def listing(request):
    VM_list = VM.objects.order_by('vm_id')[:5]
    template = loader.get_template('listing.html')
    context = {
        'VM_list': VM_list,
    }
    return HttpResponse(template.render(context, request))
@login_required
def edit(request, vm_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    num_of_vms = VM.objects.order_by('vm_id')[:5].count()
    if vm_id <= num_of_vms:
        return HttpResponse("VM Exists")
    else:
        raise Http404("VM does not exist!")

def logout(request):
    django_logout(request)
    return redirect('/')