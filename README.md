# BandaskApp - Home Heating Control System

A DIY home automation system for managing furnace, hot water preparation, and heating using a Raspberry Pi with Unipi1.1 hardware interface and a 10" touch display.

## Project Overview

BandaskApp is designed to control a heat storage tank system with the following capabilities:

- **Summer Mode**: Domestic hot water (DHW) management only
- **Winter Mode**: Both DHW and hydronic heating water (HHW) management
- **Photovoltaic Heating**: Control of solar heating system
- **Touch Interface**: Full-screen kiosk mode interface for 10" display
- **Hardware Integration**: Direct control of Unipi1.1 relays and sensors

## System Architecture

```
Touch Display (10") 
    ↓ (HTTP/WebSocket)
Django Application
    ↓ (REST API)
EVOK Interface
    ↓ (Hardware)
Unipi1.1 → Sensors/Actuators
```

## Hardware Components

- **Raspberry Pi**: Main computing unit
- **Unipi1.1**: Hardware interface for sensors and actuators
- **10" Touch Display**: User interface in kiosk mode
- **Heat Storage Tank (Bandaska)**: Central thermal storage unit
- **Temperature Sensors**: Multiple DS18B20 sensors for monitoring
- **Relays**: Control pumps, furnace, and photovoltaic heating

## Technical Documentation

This project is organized into several technical specification documents:

### 1. [Project Overview](01_project_overview.md)
High-level description of the BandaskApp system, architecture, and core functionality.

### 2. [Hardware Specification](02_hardware_specification.md)
Detailed hardware components, sensor IDs, relay mappings, and temperature thresholds.

### 3. [Software Architecture](03_software_architecture.md)
Django project structure, models, views, and application flow.

### 4. [User Interface Specification](04_user_interface_specification.md)
Touch-friendly interface design, Bootstrap components, and responsive layout.

### 5. [Implementation Phases](05_implementation_phases.md)
Detailed development phases, milestones, and project timeline.

### 6. [Technical Requirements](06_technical_requirements.md)
System requirements, dependencies, environment setup, and deployment.

### 7. [Blind Spots and Edge Cases](07_blind_spots_and_edge_cases.md)
Critical missing specifications, error handling, safety procedures, and risk mitigation.

## Quick Start

### Prerequisites
- Raspberry Pi with Raspberry Pi OS
- Python 3.9+
- Conda or virtual environment
- Unipi1.1 hardware (or simulator for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BandaskApp
   ```

2. **Set up environment**
   ```bash
   conda create -n bandaskapp python=3.9
   conda activate bandaskapp
   pip install -r requirements.txt
   ```

3. **Configure settings**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open browser to `http://localhost:8000`
   - For kiosk mode: `http://localhost:8000/?kiosk=1`

## Development

### Project Structure
```
bandaskapp/
├── manage.py
├── requirements.txt
├── bandaskapp/          # Django project settings
├── core/               # Main application logic
├── hardware/           # Hardware integration and simulator
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
└── systemd/            # Systemd service files
```

### Key Features

#### Temperature Control Logic
- **DHW Control**: Furnace starts at 45°C, stops at 60°C
- **HHW Control**: Furnace starts at 40°C, stops at 50°C
- **PVE Control**: Heater stops when bottom tank reaches 80°C
- **Safety Limits**: Temperature validation (0-100°C, max 20°C jump/5s)
- **Cooldown Periods**: Furnace 30s, Pump 5s between switches

#### Operating Modes
- **Summer**: DHW only operation
- **Winter**: DHW + HHW operation
- **Photovoltaic**: Solar heating control
- **Automatic**: Full automatic control
- **Manual**: Manual relay control with override

#### Hardware Integration
- **EVOK API**: REST API for Unipi1.1 communication
- **Simulator**: Development environment with hardware simulation
- **Real-time Control**: Immediate response to temperature changes
- **Error Handling**: API connectivity monitoring, state synchronization
- **Warning System**: Visual alerts for sensor issues and API problems

## Deployment

### Production Setup
1. **Systemd Service**: Configure auto-startup
2. **Kiosk Mode**: Full-screen touch interface
3. **Logging**: Comprehensive system logging
4. **Monitoring**: Health checks and performance monitoring

### Configuration
- **Environment Variables**: Hardware mode, API endpoints
- **Temperature Thresholds**: Configurable via web interface
- **Operating Modes**: Dynamic mode switching
- **Safety Limits**: Built-in safety mechanisms

## Testing

### Hardware Simulator
### Data Storage
- **Database**: SQLite with 1 week retention
- **TSV Files**: Daily raw data files with gzip compression
- **Logs**: System and warning logs with timestamps

### Hardware Simulator
The project includes a comprehensive hardware simulator for development and testing:

- **Temperature Simulation**: Realistic temperature progression
- **Relay Simulation**: State management and control
- **Error Simulation**: Communication failures and sensor errors
- **Mode Simulation**: Summer/winter mode switching

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Hardware Tests**: Real hardware validation
- **UI Tests**: User interface functionality

## Contributing

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Use Django best practices
- Write comprehensive tests
- Document all code changes

### Code Quality
- Minimum 80% test coverage
- Comprehensive error handling
- Clear documentation
- Performance optimization

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support and questions:
- Check the documentation in the technical specification files
- Review the troubleshooting guide
- Check system logs for error information
- Verify hardware connections and configuration

## Roadmap

### Future Enhancements
- **WebSocket Support**: Real-time updates
- **Mobile Interface**: Remote monitoring and control
- **Data Analytics**: Historical data analysis
- **Integration**: Smart home system integration
- **Alerts**: Email/SMS notifications
- **Backup Systems**: Redundant control systems

---

**Note**: This is a DIY project designed for personal use. Ensure proper safety measures when working with heating systems and electrical components.
