#!/usr/bin/env python3
"""
Script to change the thermometer ID in BandaskApp configuration
Usage: python change_thermometer_id.py NEW_THERMOMETER_ID
"""
import sys
import os

def change_thermometer_id(new_id):
    """Change the thermometer ID in Django settings"""
    settings_file = 'bandaskapp/bandaskapp/settings.py'
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Find and replace the thermometer ID
    old_pattern = "'THERMOMETER_DHW_1_ID':"
    
    if old_pattern not in content:
        print("❌ THERMOMETER_DHW_1_ID not found in settings")
        return False
    
    # Find the current ID
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "'THERMOMETER_DHW_1_ID':" in line:
            # Extract current ID
            current_id = line.split("'")[3]
            print(f"📍 Current thermometer ID: {current_id}")
            
            # Replace with new ID
            lines[i] = line.replace(current_id, new_id)
            print(f"✅ Changed to new ID: {new_id}")
            break
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Updated {settings_file}")
    return True

def update_database(old_id, new_id):
    """Update the database record with new circuit ID"""
    print("\n🔄 Updating database...")
    
    # Setup Django
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')
    django.setup()
    
    from core.models import TemperatureSensor
    
    try:
        # Find sensor with old ID
        sensor = TemperatureSensor.objects.get(circuit_id=old_id)
        print(f"📍 Found sensor: {sensor.name} with ID {sensor.circuit_id}")
        
        # Update to new ID
        sensor.circuit_id = new_id
        sensor.save()
        
        print(f"✅ Updated sensor {sensor.name} to new ID: {new_id}")
        return True
        
    except TemperatureSensor.DoesNotExist:
        print(f"⚠️  No sensor found with ID: {old_id}")
        print("   You may need to run: python manage.py setup_hardware")
        return False
    except Exception as e:
        print(f"❌ Database update failed: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python change_thermometer_id.py NEW_THERMOMETER_ID")
        print("Example: python change_thermometer_id.py 28A1B2C3D4E5F678")
        sys.exit(1)
    
    new_id = sys.argv[1]
    
    print(f"🎯 Changing thermometer ID to: {new_id}")
    print("="*60)
    
    # Get current ID from settings
    old_id = None
    settings_file = 'bandaskapp/bandaskapp/settings.py'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            for line in f:
                if "'THERMOMETER_DHW_1_ID':" in line:
                    old_id = line.split("'")[3]
                    break
    
    # Step 1: Update settings
    if not change_thermometer_id(new_id):
        sys.exit(1)
    
    # Step 2: Update database (if old ID was found)
    if old_id and old_id != new_id:
        update_database(old_id, new_id)
    
    print("\n🎊 Thermometer ID change complete!")
    print("\n📋 Next steps:")
    print("1. Restart the simulator: python hardware/simulator.py")
    print("2. Restart the Django server: python manage.py runserver")
    print("3. Check that the new ID appears in the simulator output")
    print("\n✨ The system will now use the new thermometer ID everywhere!")

if __name__ == '__main__':
    main()

