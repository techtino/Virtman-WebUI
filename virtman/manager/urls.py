from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listing', views.listing, name='listing'),
    path('<int:vm_id>/edit', views.edit, name='edit'),
]