from django.urls import path

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('listing', views.listing, name='listing'),
    path('<int:id>/edit', views.edit, name='edit'),
    path('<int:id>/customedit', views.customEdit, name='edit'),
    path('add', views.add, name='add'),
    path('profile', views.profilePage, name='profile'),
    path('createDisk', views.createDisk, name='createDisk'),
    path('uploadISO', views.uploadISO, name='uploadISO'),
    path('home', views.home, name='home'),
    path('ISO', views.ISOPage, name='ISO'),
    path('Disks', views.DiskPage, name='Disks'),
    path('containers', views.containers, name='Containers'),
    path('addContainer', views.addContainer, name='Containers'),
    path('<int:id>/viewStats', views.viewStatsPerVM, name='viewStats'),
    path('<int:id>/startVM', views.startVM_View, name='startVM'),
    path('<int:id>/startContainer', views.startContainer, name='startContainer'),
    path('<int:id>/startCustomVM', views.startcustomVM_View, name='startVM'),
    path('<int:id>/stopVM', views.stopVM_View, name='stopVM'),
    path('<int:id>/stopContainer', views.stopContainer, name='stopContainer'),
    path('<int:id>/stopcustomVM', views.stopcustomVM_View, name='stopVM'),
    path('<int:id>/shutdownVM', views.shutdownVM, name='shutdownVM'),
    path('<int:id>/shutdowncustomVM', views.shutdowncustomVM, name='shutdownVM'),
    path('<int:id>/restartVM', views.restartVM, name='restartVM'),
    path('<int:id>/restartcustomVM', views.restartcustomVM, name='restartVM'),
    path('<int:id>/viewCustomStats', views.viewStatsPerCustomVM, name='viewStats'),
    path('viewStats', views.viewHostStats, name='viewHostStats'),
    path('toggleAdvancedMode', views.AdvancedMode, name='toggleAdvancedMode'),
    path('<int:id>/vnc', views.vnc_proxy_http, name='vnc'),
    path('<int:id>/customvnc', views.customvnc_proxy_http, name='vnc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)