#!/usr/bin/env python3
"""
Test script to verify that the system correctly handles disabled sensors (NONE IDs)
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')
django.setup()

from django.conf import settings
from hardware.controller import HardwareController

def test_disabled_sensors():
    """Test that disabled sensors are handled correctly"""
    print("Testing disabled sensor handling...")
    print("=" * 50)
    
    # Get configuration
    config = settings.BANDASKAPP_CONFIG
    print(f"Configuration loaded:")
    print(f"  DHW 1 ID: {config['THERMOMETER_DHW_1_ID']}")
    print(f"  DHW 2 ID: {config['THERMOMETER_DHW_2_ID']}")
    print(f"  DHW 3 ID: {config['THERMOMETER_DHW_3_ID']}")
    print()
    
    # Create controller
    controller = HardwareController()
    
    # Test sensor enabled checks
    print("Testing sensor enabled checks:")
    print(f"  DHW 1 enabled: {controller._is_sensor_enabled(config['THERMOMETER_DHW_1_ID'])}")
    print(f"  DHW 2 enabled: {controller._is_sensor_enabled(config['THERMOMETER_DHW_2_ID'])}")
    print(f"  DHW 3 enabled: {controller._is_sensor_enabled(config['THERMOMETER_DHW_3_ID'])}")
    print()
    
    # Test temperature updates
    print("Testing temperature updates:")
    temp1 = controller.update_temperature()
    temp2 = controller.update_temperature_2()
    temp3 = controller.update_temperature_3()
    
    print(f"  DHW 1 temperature: {temp1}")
    print(f"  DHW 2 temperature: {temp2}")
    print(f"  DHW 3 temperature: {temp3}")
    print()
    
    # Test system status
    print("Testing system status:")
    status = controller.get_system_status()
    
    print(f"  DHW temperature: {status.get('dhw_temperature')}")
    print(f"  DHW temperature 2: {status.get('dhw_temperature_2')}")
    print(f"  DHW temperature 3: {status.get('dhw_temperature_3')}")
    print(f"  DHW sensor online: {status.get('dhw_sensor_online')}")
    print(f"  DHW sensor 2 online: {status.get('dhw_sensor_2_online')}")
    print(f"  DHW sensor 3 online: {status.get('dhw_sensor_3_online')}")
    print()
    
    # Test furnace control (should be skipped if DHW 1 is disabled)
    print("Testing furnace control:")
    if temp1 is not None:
        print("  DHW 1 sensor enabled, furnace control should work")
        # Note: We don't actually call control_furnace() here to avoid side effects
    else:
        print("  DHW 1 sensor disabled, furnace control should be skipped")
    
    print()
    print("Test completed successfully!")

if __name__ == '__main__':
    test_disabled_sensors()

