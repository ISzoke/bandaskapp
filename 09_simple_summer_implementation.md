# BandaskApp - Simple Summer Mode Implementation

## Overview
This is a simplified version of BandaskApp that implements only the summer mode functionality - controlling the furnace to heat domestic hot water (DHW) based on temperature readings from the upper tank sensor.

## Core Functionality
- **Single Sensor**: Monitor DHW temperature (Thermometer-DHW-1)
- **Single Relay**: Control furnace on/off (Furnace-Relay)
- **Simple Logic**: Start furnace at 45°C, stop at 60°C
- **Basic UI**: Display temperature and furnace status
- **Manual Override**: Ability to manually control furnace

## Implementation Steps

### Phase 1: Project Setup (1-2 days)

#### Step 1.1: Environment Setup
```bash
# Create conda environment
conda create -n bandaskapp python=3.9
conda activate bandaskapp

# Install minimal dependencies
pip install Django==4.2.7 requests==2.31.0 python-dateutil==2.8.2
```

#### Step 1.2: Create Django Project
```bash
# Create project structure
django-admin startproject bandaskapp
cd bandaskapp
python manage.py startapp core
python manage.py startapp hardware
```

#### Step 1.3: Basic Requirements File
```txt
# requirements.txt
Django==4.2.7
requests==2.31.0
python-dateutil==2.8.2
```

### Phase 2: Hardware Simulator (1 day)

#### Step 2.1: Create EVOK Simulator
```python
# hardware/simulator.py
import json
import time
from flask import Flask, jsonify, request

class EVOKSimulator:
    def __init__(self):
        self.sensors = {
            '2895DCD509000035': {  # DHW sensor
                'value': 42.0,  # Start below threshold
                'lost': False,
                'type': 'DS18B20'
            }
        }
        self.relays = {
            '1_01': {'value': 0}  # Furnace relay
        }
    
    def get_temperature(self, circuit_id):
        # Simulate temperature changes
        # Return sensor data
        
    def get_relay(self, circuit_id):
        # Return relay state
        
    def set_relay(self, circuit_id, value):
        # Set relay state
```

#### Step 2.2: Run Simulator
```bash
# Simple Flask server on port 8080
python hardware/simulator.py
```

### Phase 3: Core Models (1 day)

#### Step 3.1: Create Basic Models
```python
# core/models.py
from django.db import models

class TemperatureSensor(models.Model):
    name = models.CharField(max_length=50)
    circuit_id = models.CharField(max_length=20, unique=True)
    current_value = models.FloatField(null=True, blank=True)
    last_reading = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Relay(models.Model):
    name = models.CharField(max_length=50)
    circuit_id = models.CharField(max_length=20, unique=True)
    current_state = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)

class SystemState(models.Model):
    control_mode = models.CharField(
        max_length=20, 
        choices=[('automatic', 'Automatic'), ('manual', 'Manual')],
        default='automatic'
    )
    furnace_running = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
```

#### Step 3.2: Create and Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 3.3: Create Initial Data
```python
# core/management/commands/setup_hardware.py
from django.core.management.base import BaseCommand
from core.models import TemperatureSensor, Relay

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create DHW sensor
        TemperatureSensor.objects.get_or_create(
            name='DHW-1',
            circuit_id='2895DCD509000035'
        )
        
        # Create furnace relay
        Relay.objects.get_or_create(
            name='Furnace',
            circuit_id='1_01'
        )
```

### Phase 4: Hardware Integration (1-2 days)

#### Step 4.1: EVOK Client
```python
# hardware/client.py
import requests
import logging

class EVOKClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 5
    
    def get_temperature(self, circuit_id):
        try:
            url = f"{self.base_url}/json/temp/{circuit_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to read temperature {circuit_id}: {e}")
            return None
    
    def get_relay_state(self, circuit_id):
        try:
            url = f"{self.base_url}/json/ro/{circuit_id}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to read relay {circuit_id}: {e}")
            return None
    
    def set_relay_state(self, circuit_id, value):
        try:
            url = f"{self.base_url}/json/ro/{circuit_id}"
            data = {"value": int(value)}
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to set relay {circuit_id}: {e}")
            return None
```

#### Step 4.2: Hardware Controller
```python
# hardware/controller.py
import time
import logging
from datetime import datetime, timedelta
from core.models import TemperatureSensor, Relay, SystemState
from .client import EVOKClient

class HardwareController:
    def __init__(self):
        self.client = EVOKClient()
        self.dhw_temp_low = 45.0
        self.dhw_temp_high = 60.0
        self.furnace_cooldown = 30  # seconds
        self.last_furnace_switch = None
    
    def update_temperature(self):
        """Read DHW temperature from sensor"""
        try:
            sensor = TemperatureSensor.objects.get(name='DHW-1')
            data = self.client.get_temperature(sensor.circuit_id)
            
            if data and not data.get('lost', True):
                sensor.current_value = data['value']
                sensor.last_reading = datetime.now()
                sensor.save()
                logging.info(f"DHW temperature: {data['value']}°C")
                return data['value']
        except Exception as e:
            logging.error(f"Error updating temperature: {e}")
        return None
    
    def control_furnace(self):
        """Control furnace based on DHW temperature"""
        try:
            # Get current system state
            system_state, _ = SystemState.objects.get_or_create(pk=1)
            
            # Skip if in manual mode
            if system_state.control_mode == 'manual':
                return
            
            # Get current temperature
            temp = self.update_temperature()
            if temp is None:
                return
            
            # Get furnace relay
            furnace = Relay.objects.get(name='Furnace')
            
            # Check cooldown period
            if (self.last_furnace_switch and 
                time.time() - self.last_furnace_switch < self.furnace_cooldown):
                return
            
            # Control logic
            should_run = False
            if temp < self.dhw_temp_low and not furnace.current_state:
                should_run = True
                logging.info(f"Starting furnace: temp {temp}°C < {self.dhw_temp_low}°C")
            elif temp >= self.dhw_temp_high and furnace.current_state:
                should_run = False
                logging.info(f"Stopping furnace: temp {temp}°C >= {self.dhw_temp_high}°C")
            else:
                return  # No change needed
            
            # Set relay state
            result = self.client.set_relay_state(furnace.circuit_id, 1 if should_run else 0)
            if result and result.get('success'):
                furnace.current_state = should_run
                furnace.save()
                
                system_state.furnace_running = should_run
                system_state.save()
                
                self.last_furnace_switch = time.time()
                
        except Exception as e:
            logging.error(f"Error controlling furnace: {e}")
    
    def manual_control_furnace(self, state):
        """Manually control furnace"""
        try:
            furnace = Relay.objects.get(name='Furnace')
            result = self.client.set_relay_state(furnace.circuit_id, 1 if state else 0)
            
            if result and result.get('success'):
                furnace.current_state = state
                furnace.save()
                
                system_state, _ = SystemState.objects.get_or_create(pk=1)
                system_state.furnace_running = state
                system_state.save()
                
                logging.info(f"Manual furnace control: {'ON' if state else 'OFF'}")
                return True
        except Exception as e:
            logging.error(f"Error in manual furnace control: {e}")
        return False
```

### Phase 5: Background Monitoring (1 day)

#### Step 5.1: Management Command for Monitoring
```python
# core/management/commands/monitor.py
import time
import logging
from django.core.management.base import BaseCommand
from hardware.controller import HardwareController

class Command(BaseCommand):
    help = 'Monitor and control heating system'
    
    def handle(self, *args, **options):
        controller = HardwareController()
        
        self.stdout.write("Starting BandaskApp monitoring...")
        
        while True:
            try:
                controller.control_furnace()
                time.sleep(10)  # Check every 10 seconds
            except KeyboardInterrupt:
                self.stdout.write("Stopping monitoring...")
                break
            except Exception as e:
                logging.error(f"Monitor error: {e}")
                time.sleep(10)
```

### Phase 6: Basic Web Interface (2 days)

#### Step 6.1: Views
```python
# core/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from core.models import TemperatureSensor, Relay, SystemState
from hardware.controller import HardwareController

def dashboard(request):
    """Main dashboard view"""
    try:
        dhw_sensor = TemperatureSensor.objects.get(name='DHW-1')
        furnace_relay = Relay.objects.get(name='Furnace')
        system_state, _ = SystemState.objects.get_or_create(pk=1)
        
        context = {
            'dhw_temp': dhw_sensor.current_value or 0,
            'furnace_running': furnace_relay.current_state,
            'control_mode': system_state.control_mode,
            'last_reading': dhw_sensor.last_reading,
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        return render(request, 'dashboard.html', {'error': str(e)})

def api_status(request):
    """API endpoint for status updates"""
    try:
        dhw_sensor = TemperatureSensor.objects.get(name='DHW-1')
        furnace_relay = Relay.objects.get(name='Furnace')
        system_state, _ = SystemState.objects.get_or_create(pk=1)
        
        return JsonResponse({
            'dhw_temp': dhw_sensor.current_value or 0,
            'furnace_running': furnace_relay.current_state,
            'control_mode': system_state.control_mode,
            'timestamp': dhw_sensor.last_reading.isoformat() if dhw_sensor.last_reading else None,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ControlView(View):
    def post(self, request):
        """Handle control actions"""
        try:
            action = request.POST.get('action')
            controller = HardwareController()
            
            if action == 'toggle_mode':
                system_state, _ = SystemState.objects.get_or_create(pk=1)
                new_mode = 'manual' if system_state.control_mode == 'automatic' else 'automatic'
                system_state.control_mode = new_mode
                system_state.save()
                
            elif action == 'manual_furnace_on':
                controller.manual_control_furnace(True)
                
            elif action == 'manual_furnace_off':
                controller.manual_control_furnace(False)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

#### Step 6.2: Templates
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>BandaskApp - Summer Mode</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .temperature-display { font-size: 3rem; font-weight: bold; }
        .status-on { color: #28a745; }
        .status-off { color: #6c757d; }
        .control-button { min-height: 60px; font-size: 1.2rem; }
    </style>
</head>
<body>
    <div class="container-fluid">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh every 10 seconds
        setInterval(function() {
            fetch('/api/status/')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dhw-temp').textContent = data.dhw_temp.toFixed(1);
                    document.getElementById('furnace-status').textContent = data.furnace_running ? 'ON' : 'OFF';
                    document.getElementById('furnace-status').className = data.furnace_running ? 'status-on' : 'status-off';
                    document.getElementById('control-mode').textContent = data.control_mode.toUpperCase();
                });
        }, 10000);
    </script>
</body>
</html>
```

```html
<!-- templates/dashboard.html -->
{% extends 'base.html' %}

{% block content %}
<div class="row mt-3">
    <div class="col-12">
        <h1>BandaskApp - Summer Mode</h1>
    </div>
</div>

<div class="row mt-4">
    <!-- Temperature Display -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>DHW Temperature</h3>
            </div>
            <div class="card-body text-center">
                <div class="temperature-display">
                    <span id="dhw-temp">{{ dhw_temp|floatformat:1 }}</span>°C
                </div>
                <p class="text-muted">Target: 45-60°C</p>
            </div>
        </div>
    </div>
    
    <!-- System Status -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>System Status</h3>
            </div>
            <div class="card-body">
                <p><strong>Furnace:</strong> <span id="furnace-status" class="{% if furnace_running %}status-on{% else %}status-off{% endif %}">{% if furnace_running %}ON{% else %}OFF{% endif %}</span></p>
                <p><strong>Control Mode:</strong> <span id="control-mode">{{ control_mode|upper }}</span></p>
                <p><strong>Last Reading:</strong> {{ last_reading|date:"H:i:s" }}</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <!-- Control Panel -->
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3>Control Panel</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-2">
                        <button class="btn btn-primary control-button w-100" onclick="toggleMode()">
                            Toggle Mode<br><small>(Auto/Manual)</small>
                        </button>
                    </div>
                    <div class="col-md-4 mb-2">
                        <button class="btn btn-success control-button w-100" onclick="manualFurnaceOn()">
                            Furnace ON<br><small>(Manual)</small>
                        </button>
                    </div>
                    <div class="col-md-4 mb-2">
                        <button class="btn btn-danger control-button w-100" onclick="manualFurnaceOff()">
                            Furnace OFF<br><small>(Manual)</small>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function sendControl(action) {
    fetch('/control/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'action=' + action
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    });
}

function toggleMode() { sendControl('toggle_mode'); }
function manualFurnaceOn() { sendControl('manual_furnace_on'); }
function manualFurnaceOff() { sendControl('manual_furnace_off'); }
</script>
{% endblock %}
```

#### Step 6.3: URLs
```python
# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/status/', views.api_status, name='api_status'),
    path('control/', views.ControlView.as_view(), name='control'),
]
```

```python
# bandaskapp/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

### Phase 7: Testing and Deployment (1 day)

#### Step 7.1: Basic Settings
```python
# bandaskapp/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'hardware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'bandaskapp.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

#### Step 7.2: Run Commands
```bash
# Setup database
python manage.py migrate
python manage.py setup_hardware

# Start hardware simulator (in separate terminal)
python hardware/simulator.py

# Start monitoring (in separate terminal)
python manage.py monitor

# Start web server
python manage.py runserver 0.0.0.0:8000
```

## Testing Checklist

- [ ] Hardware simulator responds to API calls
- [ ] Temperature reading updates in database
- [ ] Furnace turns ON when temp < 45°C
- [ ] Furnace turns OFF when temp >= 60°C
- [ ] Web interface shows current temperature
- [ ] Manual mode allows furnace control
- [ ] Automatic mode resumes control logic
- [ ] Cooldown period prevents rapid switching

## Success Criteria

1. **Temperature Monitoring**: DHW temperature displays and updates every 10 seconds
2. **Automatic Control**: Furnace automatically starts/stops based on temperature
3. **Manual Override**: Ability to manually control furnace
4. **Web Interface**: Touch-friendly interface showing status
5. **Logging**: System events logged to file
6. **Stability**: Runs continuously without crashes

## Estimated Timeline: 5-7 days

This simplified version provides the core functionality needed for summer mode operation while keeping the implementation straightforward and testable.
