# BandaskApp - Hardware Specification

## Hardware Components

### Temperature Sensors (DS18B20)
All sensors communicate via EVOK API at `http://127.0.0.1:8080/json/temp/{circuit}`

| Sensor Name | Circuit ID | Location | Purpose | Temperature Range |
|-------------|------------|----------|---------|-------------------|
| Thermometer-DHW-1 | `2895DCD509000035` | Upper tank | Domestic Hot Water monitoring | 0-100°C |
| Thermometer-HHW-1 | `2895DCD509000036` | Middle tank | Hydronic Heating Water monitoring | 0-100°C |
| Thermometer-HHW-5 | `2895DCD509000037` | Bottom tank | Photovoltaic heating control | 0-100°C |

### Relays (Digital Outputs)
All relays controlled via EVOK API at `http://127.0.0.1:8080/json/ro/{circuit}`

| Relay Name | Circuit ID | Purpose | Default State |
|------------|------------|---------|---------------|
| Furnace-Relay | `1_01` | Control furnace on/off | OFF (0) |
| Heating-Pump | `1_02` | Control hydronic heating pump | OFF (0) |
| PVE-Heater | `1_03` | Control photovoltaic heater | OFF (0) |

### Temperature Thresholds

#### Domestic Hot Water (DHW)
- **DHW_Temp_Low**: 45°C - Start furnace when below this temperature
- **DHW_Temp_High**: 60°C - Stop furnace when above this temperature

#### Hydronic Heating Water (HHW)
- **HHW_Temp_Low**: 40°C - Start furnace when below this temperature
- **HHW_Temp_High**: 50°C - Stop furnace when above this temperature

#### Photovoltaic Heating (PVE)
- **PVE_Temp_Max**: 80°C - Stop photovoltaic heater when above this temperature

## API Endpoints

### Temperature Reading
```python
GET http://127.0.0.1:8080/json/temp/{circuit}
Headers: {"Accept": "text/html, application/json"}

Response:
{
    "dev": "temp",
    "circuit": "2895DCD509000035",
    "address": "28.95DCD5090000.35",
    "value": 22.8,
    "lost": false,
    "time": 246690.722,
    "type": "DS18B20"
}
```

### Relay State Reading
```python
GET http://127.0.0.1:8080/json/ro/{circuit}
Headers: {"Accept": "text/html, application/json"}

Response:
{
    "dev": "ro",
    "circuit": "1_01",
    "value": 0
}
```

### Relay State Setting
```python
POST http://127.0.0.1:8080/json/ro/{circuit}
Headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
Payload: {"value": 0}

Response:
{
    "success": true,
    "result": {
        "circuit": "1_01",
        "dev": "ro",
        "value": 0
    }
}
```

## Hardware Simulator Requirements

### Simulator Features
- **Summer Mode Simulation**: DHW temperature cycling between 40-65°C
- **Winter Mode Simulation**: Both DHW and HHW temperature cycling
- **Photovoltaic Simulation**: Bottom tank temperature simulation
- **Relay State Simulation**: Maintain relay states and respond to commands
- **Realistic Timing**: Temperature changes over time periods
- **Error Simulation**: Occasional sensor failures or communication errors

### Simulator API
- Must provide identical REST API as real EVOK
- Must support all temperature sensors and relays
- Must maintain state between requests
- Must provide realistic temperature progression
- Must support both GET and POST operations

## System States

### Operating Modes
1. **Summer Mode**: DHW only operation
2. **Winter Mode**: DHW + HHW operation
3. **Photovoltaic Mode**: PVE heating control

### Control Logic
- **Furnace Control**: ON if DHW < DHW_Temp_Low OR HHW < HHW_Temp_Low
- **Furnace Control**: OFF if DHW >= DHW_Temp_High AND HHW >= HHW_Temp_High
- **Heating Pump**: ON when heating demand signal received
- **PVE Heater**: OFF when Thermometer-HHW-5 >= PVE_Temp_Max

## Error Handling
- **Sensor Failures**: Detect "lost" status in temperature readings
- **Communication Errors**: Handle network timeouts and connection failures
- **Invalid States**: Prevent conflicting relay states
- **Temperature Anomalies**: Detect unrealistic temperature readings (<0°C, >100°C, jumps >20°C/5s)
- **API Unreachable**: Display warning with last access time, play alarm sound
- **State Synchronization**: Check actual vs expected relay states on startup and API recovery
- **Cooldown Periods**: SWITCH_COOLDOWN_TIME_FURNACE = 30s, SWITCH_COOLDOWN_TIME_PUMP = 5s
