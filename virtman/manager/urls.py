from django.urls import path

from . import views

urlpatterns = [
    path('listing', views.listing, name='listing'),
    path('<int:vm_id>/edit', views.edit, name='edit'),
    path('logout', views.logout, name='logout'),
    path('add', views.add, name='add'),
]