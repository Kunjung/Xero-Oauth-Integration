from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authorize/', views.authorize_in_xero, name='authorize'),
    path('revoke/', views.revoke_token, name='revoke'),
    path('callback/', views.callback, name='callback'),
    path('refresh/', views.refresh_access_token, name='refresh'),
    path('account/', views.get_account_data_from_xero, name='account'),
    path('save/', views.save_account_data_to_local_db, name='save')
]