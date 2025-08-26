from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logs/', views.logs, name='logs'),
    path('settings/', views.settings_view, name='settings'),
    path('api/settings/', views.settings_api, name='settings_api'),
    path('api/status/', views.api_status, name='api_status'),
    path('control/', views.ControlView.as_view(), name='control'),
]

