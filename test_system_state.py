#!/usr/bin/env python3
"""
Test script to check SystemState in the database
"""
import os
import sys
import django

# Add the project directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.bandaskapp.settings')
django.setup()

from core.models import SystemState

def check_system_state():
    """Check the current SystemState in the database"""
    print("Checking SystemState in database...")
    print("=" * 50)
    
    try:
        # Load the system state
        system_state = SystemState.load()
        print(f"SystemState ID: {system_state.pk}")
        print(f"Control Mode: {system_state.control_mode}")
        print(f"Winter Regime State: {system_state.winter_regime_state}")
        print(f"DHW Temp Low: {system_state.dhw_temp_low}°C")
        print(f"DHW Temp High: {system_state.dhw_temp_high}°C")
        print(f"HHW Temp Low: {system_state.hhw_temp_low}°C")
        print(f"HHW Temp High: {system_state.hhw_temp_high}°C")
        print(f"Furnace Running: {system_state.furnace_running}")
        print(f"Last Update: {system_state.last_update}")
        print(f"Created At: {system_state.created_at}")
        
        # Check if winter regime state is valid
        valid_states = ['off', 'automatic', 'on']
        if system_state.winter_regime_state not in valid_states:
            print(f"⚠️  WARNING: Winter regime state '{system_state.winter_regime_state}' is not valid!")
            print(f"   Valid states are: {valid_states}")
        else:
            print(f"✅ Winter regime state is valid: {system_state.winter_regime_state}")
            
    except Exception as e:
        print(f"❌ Error checking SystemState: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_system_state()
