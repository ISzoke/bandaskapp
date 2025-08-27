#!/bin/bash
# BandaskApp - Complete Deployment Script for New Hardware
# This script sets up BandaskApp on new hardware from scratch

set -e  # Exit on any error

echo "============================================================"
echo "🚀 BandaskApp - Complete Deployment Script for New Hardware"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root!"
    print_info "Please run as a regular user with sudo privileges if needed."
    exit 1
fi

print_header "Step 1: System Requirements Check"
echo "============================================================"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 not found! Please install Python 3.9 or higher."
    print_info "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    print_info "On CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

# Check if conda is available
if command -v conda &> /dev/null; then
    print_status "Conda found"
    CONDA_AVAILABLE=true
else
    print_warning "Conda not found - will use system Python"
    print_info "Consider installing Miniconda for better environment management:"
    print_info "  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    print_info "  bash Miniconda3-latest-Linux-x86_64.sh"
    CONDA_AVAILABLE=false
fi

# Check if git is available
if command -v git &> /dev/null; then
    print_status "Git found"
else
    print_warning "Git not found - will continue without version control"
    print_info "Install with: sudo apt install git (Ubuntu/Debian) or sudo yum install git (CentOS/RHEL)"
fi

print_header "Step 2: Environment Setup"
echo "============================================================"

# Create or activate conda environment
if [ "$CONDA_AVAILABLE" = true ]; then
    if conda info --envs | grep -q "bandaskapp"; then
        print_status "Conda environment 'bandaskapp' found"
    else
        print_info "Creating conda environment 'bandaskapp'..."
        conda create -n bandaskapp python=3.9 -y
        print_status "Conda environment 'bandaskapp' created"
    fi
    
    # Activate conda environment
    print_info "Activating conda environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate bandaskapp
    print_status "Conda environment activated"
else
    print_info "Using system Python - creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    source venv/bin/activate
    print_status "Virtual environment activated"
fi

print_header "Step 3: Dependencies Installation"
echo "============================================================"

# Install Python dependencies
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    print_info "Please ensure you're in the correct directory."
    exit 1
fi

print_header "Step 4: Database Setup"
echo "============================================================"

# Check if database exists
if [ -f "db.sqlite3" ]; then
    print_warning "Existing database found: db.sqlite3"
    read -p "Do you want to reset the database? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting database..."
        rm -f db.sqlite3
        print_status "Old database removed"
    else
        print_info "Keeping existing database"
    fi
fi

# Run database migrations
print_info "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
print_status "Database migrations completed"

print_header "Step 5: Hardware Configuration"
echo "============================================================"

# Check if settings.py has hardware configuration
if grep -q "BANDASKAPP_CONFIG" bandaskapp/settings.py; then
    print_status "Hardware configuration found in settings.py"
else
    print_error "No hardware configuration found in settings.py!"
    print_info "Please configure BANDASKAPP_CONFIG before continuing."
    exit 1
fi

# Setup hardware configuration
print_info "Setting up hardware configuration..."
python manage.py setup_hardware
print_status "Hardware configuration completed"

print_header "Step 6: System Validation"
echo "============================================================"

# Check Django configuration
print_info "Validating Django configuration..."
python manage.py check
print_status "Django configuration valid"

# Test database connection
print_info "Testing database connection..."
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database connection successful')"
print_status "Database connection successful"

# Check hardware status
print_info "Checking hardware configuration..."
python manage.py shell -c "
from core.models import TemperatureSensor, Relay, SystemState
sensors = TemperatureSensor.objects.filter(is_active=True)
relays = Relay.objects.filter(is_active=True)
system_state = SystemState.load()
print(f'Active sensors: {sensors.count()}')
print(f'Active relays: {relays.count()}')
print(f'System mode: {system_state.control_mode}')
"
print_status "Hardware configuration verified"

print_header "Step 7: Service Setup"
echo "============================================================"

# Create systemd service files (optional)
if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
    print_info "Creating systemd service files..."
    
    # Create monitor service (runs first)
    cat > /tmp/bandaskapp-monitor.service << EOF
[Unit]
Description=BandaskApp Monitor Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python manage.py monitor --interval 5
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create web server service (depends on monitor)
    cat > /tmp/bandaskapp.service << EOF
[Unit]
Description=BandaskApp Heating Control System
After=network.target bandaskapp-monitor.service
Requires=bandaskapp-monitor.service
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    print_status "Systemd service files created:"
    print_status "  - /tmp/bandaskapp-monitor.service (monitor service)"
    print_status "  - /tmp/bandaskapp.service (web server service)"
    print_info "To install:"
    print_info "  sudo mv /tmp/bandaskapp-monitor.service /etc/systemd/system/"
    print_info "  sudo mv /tmp/bandaskapp.service /etc/systemd/system/"
    print_info "  sudo systemctl daemon-reload"
    print_info "  sudo systemctl enable bandaskapp-monitor bandaskapp"
    print_info "  sudo systemctl start bandaskapp-monitor bandaskapp"
else
    print_warning "Cannot create systemd services (need sudo privileges)"
fi

print_header "Step 8: Deployment Complete!"
echo "============================================================"
echo ""
echo -e "${GREEN}🎉 BandaskApp has been successfully deployed!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. ${BLUE}Start the application:${NC}"
echo "   ${YELLOW}Option A - Using systemd services (recommended for production):${NC}"
echo "     sudo systemctl start bandaskapp-monitor"
echo "     sudo systemctl start bandaskapp"
echo "     sudo systemctl status bandaskapp-monitor bandaskapp"
echo ""
echo "   ${YELLOW}Option B - Manual startup (for development/testing):${NC}"
echo "     ${YELLOW}Terminal 1 - Web Interface:${NC}"
echo "       conda activate bandaskapp  # or: source venv/bin/activate"
echo "       cd $(pwd)"
echo "       python manage.py runserver 0.0.0.0:8000"
echo ""
echo "     ${YELLOW}Terminal 2 - Monitoring Service:${NC}"
echo "       conda activate bandaskapp  # or: source venv/bin/activate"
echo "       cd $(pwd)"
echo "       python manage.py monitor"
echo ""
echo "     ${YELLOW}Terminal 3 - Hardware Simulator (if testing):${NC}"
echo "       conda activate bandaskapp  # or: source venv/bin/activate"
echo "       cd $(pwd)"
echo "       python hardware/simulator.py"
echo ""
echo "2. ${BLUE}Access the web interface:${NC}"
echo "   http://localhost:8000"
echo ""
echo "3. ${BLUE}Check system status:${NC}"
echo "   python manage.py shell -c \"from core.models import SystemState; print(SystemState.load())\""
echo ""
echo "4. ${BLUE}Manage systemd services:${NC}"
echo "   ${YELLOW}Check service status:${NC}"
echo "     sudo systemctl status bandaskapp-monitor bandaskapp"
echo "   ${YELLOW}View service logs:${NC}"
echo "     sudo journalctl -u bandaskapp-monitor -f"
echo "     sudo journalctl -u bandaskapp -f"
echo "   ${YELLOW}Restart services:${NC}"
echo "     sudo systemctl restart bandaskapp-monitor bandaskapp"
echo "   ${YELLOW}Stop services:${NC}"
echo "     sudo systemctl stop bandaskapp bandaskapp-monitor"
echo ""
echo "5. ${BLUE}View logs:${NC}"
echo "   python manage.py shell -c \"from core.models import SystemLog; [print(f'{l.timestamp}: {l.level} - {l.message}') for l in SystemLog.objects.order_by('-timestamp')[:10]]\""
echo ""
echo "6. ${BLUE}Restart hardware setup if needed:${NC}"
echo "   python manage.py setup_hardware"
echo ""
echo "7. ${BLUE}Reset database completely if needed:${NC}"
echo "   python manage.py reset_database --force"
echo ""
echo "============================================================"
echo -e "${GREEN}🚀 Your BandaskApp is ready to control your heating system!${NC}"
echo "============================================================"

# Optional: Start the application
read -p "Do you want to start the application now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting BandaskApp..."
    print_info "Press Ctrl+C to stop"
    python manage.py runserver 0.0.0.0:8000
fi

