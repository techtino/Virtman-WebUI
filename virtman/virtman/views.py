from django.shortcuts import redirect

def redirect_view(request):
    response = redirect('/manager/home')
    return response