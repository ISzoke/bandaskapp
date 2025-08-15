from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),
    path('logs/', views.logs, name='logs'),
    path('settings/', views.settings, name='settings'),
    path('api/status/', views.api_status, name='api_status'),
    path('api/temperature-history/', views.api_temperature_history, name='api_temperature_history'),
    path('api/temperature-history-hourly/', views.api_temperature_history_hourly, name='api_temperature_history_hourly'),
    path('control/', views.ControlView.as_view(), name='control'),
]

