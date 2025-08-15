# BandaskApp - Technical Project Overview

## Project Description
BandaskApp is a DIY home automation system for managing furnace, hot water preparation, and heating using a Raspberry Pi with Unipi1.1 hardware interface and a 10" touch display.

## System Architecture

### Hardware Stack
- **Raspberry Pi** - Main computing unit
- **Unipi1.1** - Hardware interface for sensors and actuators
- **10" Touch Display** - User interface in kiosk mode
- **Heat Storage Tank (Bandaska)** - Central thermal storage unit
- **Temperature Sensors** - Multiple DS18B20 sensors for monitoring
- **Relays** - Control pumps, furnace, and photovoltaic heating
- **Furnace** - Primary heat source
- **Pumps** - Hydronic heating circulation
- **Photovoltaic Heater** - Secondary heat source (resistor in bottom of tank)

### Software Stack
- **Python 3.9+** - Primary programming language
- **Django 4.x** - Web framework for backend and frontend
- **Bootstrap 5** - UI framework for responsive touch interface
- **Conda** - Environment management
- **Systemd** - Service management for auto-startup
- **EVOK API** - Hardware communication interface

### Communication Architecture
```
Touch Display (10") 
    ↓ (HTTP/WebSocket)
Django Application
    ↓ (REST API)
EVOK Interface
    ↓ (Hardware)
Unipi1.1 → Sensors/Actuators
```

## Core Functionality

### Summer Mode (DHW Only)
- Monitor domestic hot water temperature (Thermometer-DHW-1)
- Control furnace based on DHW_Temp_Low (45°C) and DHW_Temp_High (60°C)
- Maintain hot water availability

### Winter Mode (DHW + HHW)
- Summer mode functionality plus:
- Monitor hydronic heating water (Thermometer-HHW-1)
- Control heating pump via relay
- Furnace control based on both DHW and HHW temperature requirements
- HHW_Temp_Low (40°C) and HHW_Temp_High (50°C)

### Photovoltaic Heating (PVE)
- Monitor bottom tank temperature (Thermometer-HHW-5)
- Control photovoltaic heater relay when temperature reaches 80°C
- Prevent overcharging of heat storage tank

## Development Approach
- **Backend**: Django models, views, and business logic
- **Frontend**: Django templates with Bootstrap for touch interface
- **Data Refresh**: 2-10 second polling intervals (configurable)
- **Real-time**: Immediate response to user interactions
- **Deployment**: Single Django instance as systemd service (starts after evok.service with 10s delay)
- **Testing**: Hardware simulator for development and testing
- **Operation Modes**: Automatic and manual mode with relay control
- **Data Storage**: 1 week retention in SQLite, daily TSV files with gzip compression

## Project Phases
1. **Phase 1**: Project setup and hardware simulator
2. **Phase 2**: Core Django application structure
3. **Phase 3**: Hardware integration and control logic
4. **Phase 4**: User interface and touch controls
5. **Phase 5**: System integration and deployment
