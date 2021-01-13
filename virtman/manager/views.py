from django.shortcuts import render
from .models import VM
from django.template import loader
# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Landing page. Login:")

def listing(request):

    latest_question_list = VM.objects.order_by('vm_id')[:5]
    template = loader.get_template('listing.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))
    
def edit(request, vm_id):
    if vm_id == 1:
        return HttpResponse("id %s." % vm_id)
    else:
        return HttpResponse("VM with id %s" % vm_id + " does not exist!")