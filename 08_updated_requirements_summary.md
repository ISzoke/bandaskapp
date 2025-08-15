# BandaskApp - Updated Requirements Summary

## Key Changes Based on User Feedback

### 1. Error Handling and Resilience

#### Hardware Communication Failures
- **API Unreachable**: Display warning with last access time, play alarm sound
- **State Synchronization**: Check actual vs expected relay states on startup and API recovery
- **Cooldown Periods**: 
  - `SWITCH_COOLDOWN_TIME_FURNACE = 30s`
  - `SWITCH_COOLDOWN_TIME_PUMP = 5s`
- **Temperature Validation**:
  - Range validation: 0-100°C
  - Jump detection: >20°C per 5s
  - Blinking red warnings for out-of-range values
- **Warning System**: Visual warning log with exclamation mark, clickable for detailed view

#### Database Simplification
- **Non-Critical**: Database used only for historical logging and graph data
- **No Complex Recovery**: Simple backup procedures only

### 2. Safety and Control

#### Emergency Procedures
- **Automatic/Manual Mode**: Switch on display for mode selection
- **Manual Override**: Direct relay control in manual mode
- **Temperature Safety**: Same as hardware communication failures

### 3. Data Management

#### Log Retention
- **Database**: 1 week retention in SQLite
- **TSV Files**: Daily raw hardware data files
- **Compression**: Previous day TSV files gzipped automatically
- **Simple Backup**: Basic database backup, no special treatment

### 4. Network and Communication

#### Local Operation
- **Localhost Only**: Everything runs on localhost
- **No Internet**: Device works without internet connection
- **API Polling**: 2-10 second intervals (configurable)
- **No Rate Limits**: EVOK API has no usage limits

### 5. User Interface Simplification

#### Touch Interface
- **No Special Handling**: Touch screen failures not addressed
- **Fixed Display**: Landscape orientation, no special configuration needed

### 6. System Integration

#### Operating System
- **Frozen Image**: System image prevents updates for long-term stability
- **No Updates**: Designed to run for years without human intervention
- **Service Dependencies**: Starts after `evok.service` with 10s delay

### 7. Performance and Resources

#### Resource Management
- **Not a Problem**: Memory and resource management not critical
- **Single User**: No concurrent access handling needed

### 8. Configuration Management

#### Single Environment
- **Single RPi**: No environment-specific configurations
- **No Dynamic Updates**: Runtime configuration changes not needed

### 9. Testing and Validation

#### Hardware Testing
- **Limited Scale**: Real hardware testing in limited scope
- **Simulator Testing**: Integration testing with hardware simulator

### 10. Security Simplification

#### Access Control
- **No Authentication**: User access control not needed
- **No Network Security**: No internet connection, no security measures

## Updated Technical Specifications

### New Models Added
```python
# WarningLog model for tracking system warnings
class WarningLog(models.Model):
    WARNING_TYPES = [
        ('api_timeout', 'API Timeout'),
        ('sensor_range', 'Sensor Out of Range'),
        ('sensor_jump', 'Temperature Jump'),
        ('relay_mismatch', 'Relay State Mismatch'),
        ('api_unreachable', 'API Unreachable'),
    ]
```

### Enhanced SystemState Model
```python
# Added control modes
CONTROL_MODES = [
    ('automatic', 'Automatic Mode'),
    ('manual', 'Manual Mode'),
]
```

### Updated Configuration
```python
BANDASKAPP_CONFIG = {
    # ... existing config ...
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

### Enhanced Hardware Controller
```python
class HardwareController:
    def __init__(self, client=None):
        # ... existing init ...
        self.cooldown_times = {
            'furnace': 30,  # seconds
            'pump': 5,      # seconds
        }
        self.last_switch_times = {}
    
    def validate_temperature(self, sensor_name, value, previous_value=None):
        """Validate temperature readings for anomalies"""
        
    def sync_relay_states(self):
        """Synchronize actual vs expected relay states"""
        
    def check_api_connectivity(self):
        """Check API connectivity and log warnings"""
```

## Updated User Interface

### New UI Elements
- **Control Mode Switch**: Automatic/Manual mode selection
- **Warning Display**: Blinking red indicators for critical issues
- **Warning Log Viewer**: Clickable warning list with timestamps
- **Manual Override Controls**: Direct relay control in manual mode

### Enhanced Dashboard
- **Warning Badge**: Exclamation mark for active warnings
- **Blinking Indicators**: Red blinking for sensor and API issues
- **Status Synchronization**: Real-time relay state verification

## Updated Systemd Service
```ini
[Unit]
Description=BandaskApp Django Application
After=evok.service
Wants=evok.service

[Service]
# ... existing config ...
ExecStartPre=/bin/sleep 10
```

## Data Storage Strategy

### Database (SQLite)
- **Purpose**: Historical logging and graph data
- **Retention**: 1 week
- **Backup**: Simple database dump

### TSV Files
- **Purpose**: Raw hardware data
- **Frequency**: Daily files
- **Compression**: Previous day files gzipped
- **Location**: `data/tsv/` directory

### Logs
- **System Logs**: Application events
- **Warning Logs**: System warnings with timestamps
- **Retention**: Configurable

## Implementation Priorities

### Phase 1 (Critical)
1. **Warning System**: Visual alerts and logging
2. **Cooldown Logic**: Prevent rapid relay switching
3. **Temperature Validation**: Range and jump detection
4. **State Synchronization**: Actual vs expected relay states

### Phase 2 (Important)
1. **Manual Mode**: Override controls
2. **TSV Data Storage**: Daily file creation and compression
3. **Service Dependencies**: Proper startup order
4. **Alarm Sounds**: Audio alerts for critical warnings

### Phase 3 (Enhancement)
1. **Warning Log Viewer**: Detailed warning display
2. **Data Retention**: Automatic cleanup
3. **Backup Procedures**: Simple backup scripts

## Key Simplifications Made

1. **No Authentication**: Single-user system
2. **No Network Security**: Localhost only
3. **No Dynamic Configuration**: Static settings
4. **No Complex Recovery**: Simple error handling
5. **No Touch Calibration**: Fixed display setup
6. **No Resource Monitoring**: Not critical for this use case
7. **No Concurrent Access**: Single user interface
8. **No Internet Dependencies**: Offline operation

## Safety Features Maintained

1. **Temperature Validation**: Prevents dangerous readings
2. **Cooldown Periods**: Prevents equipment damage
3. **State Synchronization**: Prevents unexpected behavior
4. **Warning System**: Immediate visibility of issues
5. **Manual Override**: Emergency control capability
6. **Emergency Stop**: Critical safety feature

This updated specification reflects a simplified, robust system focused on reliability and safety rather than complex features, perfect for a long-term DIY installation.



