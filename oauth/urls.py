from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authorize/', views.authorize, name='authorize'),
    path('callback/', views.callback, name='callback'),
    path('refresh/', views.refresh_access_token, name='refresh'),
    path('account/', views.get_xero_data, name='account'),
    path('save/', views.save_xero_data, name='save')
]