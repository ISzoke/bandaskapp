# 🚀 BandaskApp Deployment Guide for New Hardware

This guide provides step-by-step instructions for deploying BandaskApp on new hardware systems.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 7+, RHEL 7+)
- **Python**: Python 3.9 or higher
- **Memory**: Minimum 512MB RAM
- **Storage**: Minimum 1GB free space
- **Network**: Internet access for package installation

### Hardware Requirements
- **Temperature Sensors**: DS18B20 sensors with EVOK interface
- **Relays**: Compatible relay modules (1_01, 1_02 format)
- **Control Unit**: EVOK-compatible hardware controller
- **Network**: Ethernet or WiFi connection

## 🛠️ Quick Deployment (Automated)

The easiest way to deploy is using the automated deployment script:

```bash
# 1. Clone or copy the BandaskApp to your new hardware
git clone <your-repo-url> bandaskapp
cd bandaskapp

# 2. Run the deployment script
./deploy.sh
```

The script will automatically:
- Check system requirements
- Set up Python environment
- Install dependencies
- Configure database
- Set up hardware configuration
- Validate the installation

## 📝 Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot, follow these steps:

### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y  # CentOS/RHEL

# Install required system packages
sudo apt install python3 python3-pip python3-venv git -y  # Ubuntu/Debian
# OR
sudo yum install python3 python3-pip git -y  # CentOS/RHEL
```

### Step 2: Python Environment Setup

#### Option A: Using Conda (Recommended)
```bash
# Install Miniconda if not available
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create and activate environment
conda create -n bandaskapp python=3.9 -y
conda activate bandaskapp
```

#### Option B: Using Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Application Setup

```bash
# Navigate to application directory
cd bandaskapp

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Hardware Configuration

```bash
# Setup hardware configuration
python manage.py setup_hardware

# Verify configuration
python manage.py shell -c "
from core.models import TemperatureSensor, Relay
print(f'Sensors: {TemperatureSensor.objects.count()}')
print(f'Relays: {Relay.objects.count()}')
"
```

### Step 5: System Validation

```bash
# Check Django configuration
python manage.py check

# Test database connection
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK')"

# Verify hardware setup
python manage.py shell -c "
from core.models import SystemState
state = SystemState.load()
print(f'System mode: {state.control_mode}')
print(f'DHW thresholds: {state.dhw_temp_low}°C - {state.dhw_temp_high}°C')
"
```

## 🔧 Configuration

### Hardware Configuration

Edit `bandaskapp/settings.py` to configure your hardware:

```python
BANDASKAPP_CONFIG = {
    'THERMOMETERS': [
        {
            'id': 'YOUR_SENSOR_ID_1',  # Replace with actual sensor ID
            'label': 'DHW Top',        # Display name
            'color': '#ff6b6b'         # UI color
        },
        # Add more sensors as needed
    ],
    'FURNACE_RELAY_ID': '1_01',       # Your furnace relay ID
    'PUMP_RELAY_ID': '1_02',          # Your pump relay ID
    'EVOK_BASE_URL': 'http://127.0.0.1:8080',  # Your EVOK API URL
    # ... other settings
}
```

### Environment Variables (Optional)

Create `.env` file for sensitive configuration:

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-server-ip,localhost
```

## 🚀 Starting the Application

### Development Mode

```bash
# Terminal 1: Web Interface
conda activate bandaskapp  # or: source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Monitoring Service
conda activate bandaskapp  # or: source venv/bin/activate
python manage.py monitor

# Terminal 3: Hardware Simulator (for testing)
conda activate bandaskapp  # or: source venv/bin/activate
python hardware/simulator.py
```

### Production Mode

```bash
# Create systemd service
sudo mv /tmp/bandaskapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bandaskapp
sudo systemctl start bandaskapp

# Check status
sudo systemctl status bandaskapp
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Errors
```bash
# Reset database completely
python manage.py reset_database --force

# Re-run migrations
python manage.py makemigrations
python manage.py migrate
```

#### 2. Hardware Configuration Issues
```bash
# Re-setup hardware
python manage.py setup_hardware

# Check hardware status
python manage.py shell -c "
from core.models import TemperatureSensor, Relay
for s in TemperatureSensor.objects.all():
    print(f'{s.name}: {s.circuit_id} - Active: {s.is_active}')
"
```

#### 3. Permission Issues
```bash
# Fix file permissions
chmod +x deploy.sh
chmod -R 755 .
chmod 644 db.sqlite3  # if exists
```

#### 4. Port Already in Use
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill process or use different port
python manage.py runserver 0.0.0.0:8001
```

### Logs and Debugging

```bash
# View system logs
python manage.py shell -c "
from core.models import SystemLog
for log in SystemLog.objects.order_by('-timestamp')[:20]:
    print(f'{log.timestamp}: {log.level} - {log.message}')
"

# Check Django logs
tail -f /var/log/syslog | grep bandaskapp
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check system status
python manage.py shell -c "
from core.models import SystemState, TemperatureSensor, Relay
state = SystemState.load()
sensors = TemperatureSensor.objects.filter(is_active=True)
relays = Relay.objects.filter(is_active=True)
print(f'System: {state.control_mode}')
print(f'Sensors: {sensors.count()}')
print(f'Relays: {relays.count()}')
"

# Check sensor status
python manage.py shell -c "
from core.models import TemperatureSensor
for s in TemperatureSensor.objects.all():
    status = 'Online' if s.is_online else 'Offline'
    print(f'{s.name}: {status} - {s.current_value}°C')
"
```

### Backup and Recovery

```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp bandaskapp/settings.py settings.py.backup.$(date +%Y%m%d_%H%M%S)

# Restore from backup
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3
```

## 🔐 Security Considerations

### Production Security

```bash
# Change Django secret key
python manage.py shell -c "
from django.core.management.utils import get_random_secret_key
print(f'SECRET_KEY = \"{get_random_secret_key()}\"')
"

# Disable debug mode
# Set DEBUG = False in settings.py

# Configure allowed hosts
# Set ALLOWED_HOSTS = ['your-server-ip', 'your-domain.com']

# Use HTTPS in production
# Configure reverse proxy (nginx/apache) with SSL
```

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 8000/tcp  # Django development server
sudo ufw allow 22/tcp     # SSH
sudo ufw enable
```

## 📚 Additional Resources

### Useful Commands

```bash
# View all available management commands
python manage.py help

# Check Django version
python manage.py --version

# Create superuser (for admin access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Test the application
python manage.py test
```

### Configuration Files

- `bandaskapp/settings.py` - Main Django settings
- `requirements.txt` - Python dependencies
- `deploy.sh` - Automated deployment script
- `core/management/commands/` - Custom management commands

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** using the commands above
2. **Verify hardware configuration** in settings.py
3. **Test database connectivity**
4. **Check system requirements**
5. **Review this deployment guide**

## 🎯 Success Checklist

- [ ] System requirements met
- [ ] Python environment configured
- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Hardware configured
- [ ] System validated
- [ ] Application starting
- [ ] Web interface accessible
- [ ] Monitoring service running
- [ ] Hardware communication working

---

**🎉 Congratulations!** Your BandaskApp is now deployed and ready to control your heating system.

For additional support or questions, refer to the project documentation or create an issue in the project repository.
