#!/usr/bin/env python3
"""
Test script to verify that disabled sensors (NONE) don't break the system
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bandaskapp'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')
django.setup()

from hardware.controller import HardwareController
from core.models import TemperatureSensor, Relay, SystemState

def test_disabled_sensors():
    """Test that disabled sensors don't break the system"""
    print("🧪 Testing Disabled Sensors Fix...")
    
    try:
        # Create controller
        controller = HardwareController()
        
        print(f"✅ Controller created successfully")
        print(f"📋 Configuration:")
        print(f"   DHW 1 ID: {controller.config['THERMOMETER_DHW_1_ID']}")
        print(f"   DHW 2 ID: {controller.config['THERMOMETER_DHW_2_ID']}")
        print(f"   DHW 3 ID: {controller.config['THERMOMETER_DHW_3_ID']}")
        
        # Test sensor enabled checks
        print(f"\n🔍 Testing sensor enabled checks:")
        print(f"   DHW 1 enabled: {controller._is_sensor_enabled(controller.config['THERMOMETER_DHW_1_ID'])}")
        print(f"   DHW 2 enabled: {controller._is_sensor_enabled(controller.config['THERMOMETER_DHW_2_ID'])}")
        print(f"   DHW 3 enabled: {controller._is_sensor_enabled(controller.config['THERMOMETER_DHW_3_ID'])}")
        
        # Test system status with disabled sensors
        print(f"\n📊 Testing system status with disabled sensors:")
        status = controller.get_system_status()
        
        if 'error' in status:
            print(f"❌ System status failed: {status['error']}")
            return False
        
        print(f"✅ System status retrieved successfully")
        print(f"   Control mode: {status.get('control_mode')}")
        print(f"   DHW temp: {status.get('dhw_temperature')}")
        print(f"   DHW temp 2: {status.get('dhw_temperature_2')}")
        print(f"   DHW temp 3: {status.get('dhw_temperature_3')}")
        print(f"   DHW sensor online: {status.get('dhw_sensor_online')}")
        print(f"   DHW sensor 2 online: {status.get('dhw_sensor_2_online')}")
        print(f"   DHW sensor 3 online: {status.get('dhw_sensor_3_online')}")
        
        # Test temperature update methods with disabled sensors
        print(f"\n🌡️  Testing temperature update methods:")
        
        temp1 = controller.update_temperature()
        print(f"   update_temperature(): {temp1}")
        
        temp2 = controller.update_temperature_2()
        print(f"   update_temperature_2(): {temp2}")
        
        temp3 = controller.update_temperature_3()
        print(f"   update_temperature_3(): {temp3}")
        
        # Test furnace control with disabled sensors
        print(f"\n🔥 Testing furnace control:")
        furnace_control = controller.control_furnace()
        print(f"   control_furnace(): {furnace_control}")
        
        print(f"\n✅ All tests passed! Disabled sensors are handled gracefully.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_state():
    """Check current database state"""
    print(f"\n🗄️  Database State:")
    
    try:
        # Check temperature sensors
        sensors = TemperatureSensor.objects.all()
        print(f"   Temperature sensors: {sensors.count()}")
        for sensor in sensors:
            print(f"     - {sensor.name}: {sensor.circuit_id} (active: {sensor.is_active})")
        
        # Check relays
        relays = Relay.objects.all()
        print(f"   Relays: {relays.count()}")
        for relay in relays:
            print(f"     - {relay.name}: {relay.circuit_id} (active: {relay.is_active})")
        
        # Check system state
        system_state = SystemState.load()
        print(f"   System state: {system_state.control_mode} mode")
        print(f"   DHW thresholds: {system_state.dhw_temp_low}°C - {system_state.dhw_temp_high}°C")
        
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Disabled Sensors Fix for BandaskApp")
    print("=" * 50)
    
    # Check database state first
    test_database_state()
    
    # Run the main test
    success = test_disabled_sensors()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Disabled sensors are handled correctly!")
    else:
        print("💥 FAILURE: There are still issues with disabled sensors")
    
    sys.exit(0 if success else 1)
