from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logs/', views.logs, name='logs'),
    path('settings/', views.settings, name='settings'),
    path('api/status/', views.api_status, name='api_status'),
    path('control/', views.ControlView.as_view(), name='control'),
]

