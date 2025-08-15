# BandaskApp - Software Architecture

## Django Project Structure

```
bandaskapp/
├── manage.py
├── requirements.txt
├── bandaskapp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── apps.py
│   └── tests.py
├── hardware/
│   ├── __init__.py
│   ├── client.py
│   ├── simulator.py
│   ├── controller.py
│   └── tests.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── settings.html
│   └── components/
└── systemd/
    └── bandaskapp.service
```

## Core Models

### TemperatureSensor
```python
class TemperatureSensor(models.Model):
    name = models.CharField(max_length=50)
    circuit_id = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=50)
    purpose = models.CharField(max_length=50)
    current_value = models.FloatField(null=True, blank=True)
    last_reading = models.DateTimeField(null=True, blank=True)
    is_lost = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'temperature_sensors'
```

### Relay
```python
class Relay(models.Model):
    name = models.CharField(max_length=50)
    circuit_id = models.CharField(max_length=20, unique=True)
    purpose = models.CharField(max_length=50)
    current_state = models.BooleanField(default=False)
    last_change = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'relays'
```

### SystemState
```python
class SystemState(models.Model):
    OPERATING_MODES = [
        ('summer', 'Summer Mode'),
        ('winter', 'Winter Mode'),
        ('pve', 'Photovoltaic Mode'),
    ]
    
    CONTROL_MODES = [
        ('automatic', 'Automatic Mode'),
        ('manual', 'Manual Mode'),
    ]
    
    operating_mode = models.CharField(max_length=20, choices=OPERATING_MODES, default='summer')
    control_mode = models.CharField(max_length=20, choices=CONTROL_MODES, default='automatic')
    heating_demand = models.BooleanField(default=False)
    furnace_running = models.BooleanField(default=False)
    heating_pump_running = models.BooleanField(default=False)
    pve_heater_running = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_state'
```

### TemperatureLog
```python
class TemperatureLog(models.Model):
    sensor = models.ForeignKey(TemperatureSensor, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temperature_logs'
        indexes = [
            models.Index(fields=['sensor', 'timestamp']),
        ]
```

### SystemLog
```python
class SystemLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        indexes = [
            models.Index(fields=['level', 'timestamp']),
        ]
```

### WarningLog
```python
class WarningLog(models.Model):
    WARNING_TYPES = [
        ('api_timeout', 'API Timeout'),
        ('sensor_range', 'Sensor Out of Range'),
        ('sensor_jump', 'Temperature Jump'),
        ('relay_mismatch', 'Relay State Mismatch'),
        ('api_unreachable', 'API Unreachable'),
    ]
    
    warning_type = models.CharField(max_length=20, choices=WARNING_TYPES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'warning_logs'
        indexes = [
            models.Index(fields=['warning_type', 'timestamp']),
        ]
```

## Hardware Integration Layer

### EVOKClient
```python
class EVOKClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_temperature(self, circuit_id):
        """Read temperature from sensor"""
        
    def get_relay_state(self, circuit_id):
        """Read relay state"""
        
    def set_relay_state(self, circuit_id, value):
        """Set relay state (0 or 1)"""
```

### HardwareController
```python
class HardwareController:
    def __init__(self, client=None):
        self.client = client or EVOKClient()
        self.temperature_thresholds = {
            'dhw_low': 45.0,
            'dhw_high': 60.0,
            'hhw_low': 40.0,
            'hhw_high': 50.0,
            'pve_max': 80.0,
        }
        self.cooldown_times = {
            'furnace': 30,  # seconds
            'pump': 5,      # seconds
        }
        self.last_switch_times = {}
    
    def update_temperatures(self):
        """Update all temperature readings with validation"""
        
    def validate_temperature(self, sensor_name, value, previous_value=None):
        """Validate temperature readings for anomalies"""
        
    def control_furnace(self):
        """Control furnace based on temperature logic with cooldown"""
        
    def control_heating_pump(self, demand):
        """Control heating pump based on demand with cooldown"""
        
    def control_pve_heater(self):
        """Control photovoltaic heater"""
        
    def sync_relay_states(self):
        """Synchronize actual vs expected relay states"""
        
    def check_api_connectivity(self):
        """Check API connectivity and log warnings"""
```

## Application Views

### Dashboard View
- **URL**: `/`
- **Purpose**: Main touch interface showing system status
- **Features**:
  - Real-time temperature displays
  - System state indicators
  - Manual override controls
  - Operating mode selection
  - System logs display

### Settings View
- **URL**: `/settings/`
- **Purpose**: Configuration and threshold management
- **Features**:
  - Temperature threshold adjustment
  - Operating mode configuration
  - Hardware connection settings
  - System maintenance options

### API Views
- **URL**: `/api/status/`
- **Purpose**: JSON endpoints for AJAX updates
- **Features**:
  - Current system status
  - Temperature readings
  - Relay states
  - System logs

## Background Tasks

### Temperature Monitoring
```python
class TemperatureMonitor:
    def __init__(self, controller):
        self.controller = controller
        self.update_interval = 10  # seconds
    
    def start_monitoring(self):
        """Start background temperature monitoring"""
        
    def update_temperatures(self):
        """Update all temperature readings"""
```

### Control Logic
```python
class ControlLogic:
    def __init__(self, controller):
        self.controller = controller
    
    def evaluate_furnace_control(self):
        """Evaluate if furnace should be on/off"""
        
    def evaluate_heating_pump(self):
        """Evaluate heating pump control"""
        
    def evaluate_pve_heater(self):
        """Evaluate photovoltaic heater control"""
```

## Configuration Management

### Settings Configuration
```python
# settings.py
BANDASKAPP_CONFIG = {
    'HARDWARE_MODE': 'simulator',  # 'simulator' or 'real'
    'EVOK_BASE_URL': 'http://127.0.0.1:8080',
    'UPDATE_INTERVAL': 10,  # seconds (2-10s range)
    'TEMPERATURE_THRESHOLDS': {
        'dhw_low': 45.0,
        'dhw_high': 60.0,
        'hhw_low': 40.0,
        'hhw_high': 50.0,
        'pve_max': 80.0,
    },
    'SENSOR_CIRCUITS': {
        'dhw_1': '2895DCD509000035',
        'hhw_1': '2895DCD509000036',
        'hhw_5': '2895DCD509000037',
    },
    'RELAY_CIRCUITS': {
        'furnace': '1_01',
        'heating_pump': '1_02',
        'pve_heater': '1_03',
    },
    'COOLDOWN_TIMES': {
        'furnace': 30,  # seconds
        'pump': 5,      # seconds
    },
    'DATA_RETENTION_DAYS': 7,  # 1 week
    'TEMPERATURE_VALIDATION': {
        'min_temp': 0.0,
        'max_temp': 100.0,
        'max_jump': 20.0,  # degrees per 5s
    }
}
```

## Security Considerations
- **Local Network Only**: Application runs on local network
- **No External Access**: No internet connectivity required
- **Simple Authentication**: Basic session-based auth for settings
- **Input Validation**: All user inputs validated
- **Error Handling**: Comprehensive error handling and logging

## Performance Considerations
- **Database Optimization**: Indexed queries for temperature logs
- **Caching**: Cache frequently accessed data
- **Background Tasks**: Use Django background tasks for monitoring
- **Memory Management**: Regular cleanup of old log entries
- **Response Time**: Optimize for sub-second response times
