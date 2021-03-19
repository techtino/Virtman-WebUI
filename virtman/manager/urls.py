from django.urls import path

from . import views

urlpatterns = [
    path('listing', views.listing, name='listing'),
    path('<int:id>/edit', views.edit, name='edit'),
    path('add', views.add, name='add'),
    path('createDisk', views.createDisk, name='createDisk'),
    path('uploadISO', views.uploadISO, name='uploadISO'),
    path('home', views.home, name='home'),
    path('<int:id>/startVM', views.startVM_View, name='startVM'),
    path('<int:id>/delete', views.delete, name='delete'),
    path('<int:id>/stopVM', views.stopVM_View, name='stopVM')
]