# Disabled Sensors Implementation

This document describes the implementation of support for disabled temperature sensors using the `NONE` configuration value.

## Overview

The system now supports disabling individual temperature sensors by setting their circuit ID to `NONE` in the configuration. When a sensor is disabled:

1. **No API calls** are made to read from that sensor
2. **No temperature data** is displayed in the UI for that sensor
3. **No mini-graphs** are shown for disabled sensors
4. **Furnace control is skipped** if the primary DHW sensor (DHW 1) is disabled

## Configuration

In `settings.py`, sensors can be disabled by setting their ID to `'NONE'`:

```python
BANDASKAPP_CONFIG = {
    'THERMOMETER_DHW_1_ID': '2895DCD509000035',  # Enabled
    'THERMOMETER_DHW_2_ID': 'NONE',              # Disabled
    'THERMOMETER_DHW_3_ID': 'NONE',              # Disabled
    # ... other settings
}
```

## Changes Made

### 1. Hardware Controller (`hardware/controller.py`)

- Added `_is_sensor_enabled()` method to check if a sensor is enabled
- Updated `update_temperature()`, `update_temperature_2()`, and `update_temperature_3()` methods to skip disabled sensors
- Updated `get_system_status()` method to handle disabled sensors gracefully
- Disabled sensors return `None` for temperature values and `False` for online status

### 2. Views (`core/views.py`)

- Added sensor enabled status to context data for templates
- Added sensor enabled status to API responses
- Both dashboard and API status endpoints now include `dhw_sensor_X_enabled` flags

### 3. Dashboard Template (`templates/dashboard.html`)

- Added conditional rendering for each sensor section using `{% if dhw_sensor_X_enabled %}`
- Added fallback message when no sensors are enabled
- Updated JavaScript functions to only create mini-graphs for enabled sensors
- Updated temperature update functions to handle missing elements gracefully

### 4. Base Template (`templates/base.html`)

- Updated AJAX status updates to respect sensor enabled flags
- Mini-graph updates only occur for enabled sensors
- Temperature display updates only occur for enabled sensors

### 5. Management Command (`core/management/commands/monitor.py`)

- Updated monitoring cycle to skip disabled sensors
- Added logging for disabled sensors
- Furnace control is skipped if DHW 1 sensor is disabled
- System status logging shows only enabled sensors

## Behavior Changes

### When Sensors Are Disabled

1. **No Hardware Communication**: The system will not attempt to read from disabled sensors
2. **UI Elements Hidden**: Temperature displays and mini-graphs for disabled sensors are not shown
3. **No Data Updates**: AJAX updates skip disabled sensors
4. **Graceful Degradation**: The system continues to function with remaining enabled sensors

### When All Sensors Are Disabled

1. **Warning Message**: A clear message is displayed indicating no sensors are enabled
2. **No Temperature Data**: No temperature information is shown
3. **No Mini-Graphs**: No graphs are displayed
4. **System Still Functional**: Other system features (relays, logs, settings) remain available

## Testing

A test script `test_disabled_sensors.py` has been created to verify the implementation:

```bash
cd bandaskapp
python test_disabled_sensors.py
```

This script tests:
- Sensor enabled status checks
- Temperature update methods
- System status retrieval
- Configuration loading

## Benefits

1. **Flexibility**: Easy to disable sensors without code changes
2. **Performance**: No unnecessary API calls to disabled sensors
3. **User Experience**: Clear indication of which sensors are available
4. **Maintenance**: Easy to temporarily disable problematic sensors
5. **Scalability**: Can easily add/remove sensors by changing configuration

## Future Enhancements

1. **Dynamic Configuration**: Could add web interface to enable/disable sensors
2. **Sensor Groups**: Could support enabling/disabling groups of sensors
3. **Fallback Sensors**: Could implement automatic fallback to backup sensors
4. **Configuration Validation**: Could add validation to ensure at least one sensor is enabled

## Notes

- The simulator (`simulator.py`) was not modified as requested
- The system gracefully handles missing database entries for disabled sensors
- All changes are backward compatible - existing configurations continue to work
- The implementation follows the existing code patterns and style
