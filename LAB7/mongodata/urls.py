from django.urls import path
from mongodata import views

urlpatterns = [
    path('data/', views.view_data, name='view_data'),
    path('private_data/', views.view_private_data, name='view_private_data'),
    path('insert_data/', views.view_new_data, name='insert_data'),
    path('insert_private_data/', views.view_new_private_data, name='insert_private_data'),
]
