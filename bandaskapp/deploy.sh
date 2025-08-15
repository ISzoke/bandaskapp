#!/bin/bash
# BandaskApp Summer Mode - Deployment Script

echo "============================================================"
echo "BandaskApp Summer Mode - Deployment Script"
echo "============================================================"

# Check if conda environment exists
if ! conda info --envs | grep -q "bandaskapp"; then
    echo "❌ Conda environment 'bandaskapp' not found!"
    echo "Please run: conda create -n bandaskapp python=3.9"
    exit 1
fi

echo "✓ Conda environment found"

# Activate conda environment
echo "Activating conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate bandaskapp

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Setup hardware configuration
echo "Setting up hardware configuration..."
python manage.py setup_hardware

# Run system tests
echo "Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "============================================================"
    echo ""
    echo "To start BandaskApp:"
    echo ""
    echo "1. Start hardware simulator (in separate terminal):"
    echo "   conda activate bandaskapp"
    echo "   cd $(pwd)"
    echo "   python hardware/simulator.py"
    echo ""
    echo "2. Start monitoring service (in separate terminal):"
    echo "   conda activate bandaskapp" 
    echo "   cd $(pwd)"
    echo "   python manage.py monitor"
    echo ""
    echo "3. Start web interface (in separate terminal):"
    echo "   conda activate bandaskapp"
    echo "   cd $(pwd)" 
    echo "   python manage.py runserver 0.0.0.0:8000"
    echo ""
    echo "4. Access web interface:"
    echo "   http://localhost:8000"
    echo ""
    echo "============================================================"
    echo "🏠 BandaskApp Summer Mode is ready!"
    echo "============================================================"
else
    echo "❌ Deployment failed - system tests did not pass"
    exit 1
fi

