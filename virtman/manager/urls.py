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
    path('<int:id>/stopVM', views.stopVM_View, name='stopVM'),
    path('<int:id>/shutdownVM', views.shutdownVM, name='shutdownVM'),
    path('<int:id>/restartVM', views.restartVM, name='restartVM'),
    path('<int:id>/viewStats', views.viewStatsPerVM, name='viewStats'),
    path('viewStats', views.viewHostStats, name='viewHostStats'),
    path('toggleAdvancedMode', views.AdvancedMode, name='toggleAdvancedMode')
]