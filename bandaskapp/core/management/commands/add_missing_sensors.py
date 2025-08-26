from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import TemperatureSensor


class Command(BaseCommand):
    help = 'Add missing temperature sensors to the database'

    def handle(self, *args, **options):
        config = settings.BANDASKAPP_CONFIG
        
        # Define the sensors to create
        sensors_to_create = [
            {
                'name': 'DHW Temperature Sensor 2 (Middle)',
                'circuit_id': config['THERMOMETERS'][1]['id'],
                'location': 'DHW middle',
                'is_active': True,
                'current_value': 0.0,
                'is_lost': False,
            },
            {
                'name': 'DHW Temperature Sensor 3 (Bottom)',
                'circuit_id': config['THERMOMETERS'][2]['id'],
                'location': 'DHW bottom',
                'is_active': True,
                'current_value': 0.0,
                'is_lost': False,
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for sensor_data in sensors_to_create:
            circuit_id = sensor_data['circuit_id']
            
            try:
                # Check if sensor already exists
                sensor, created = TemperatureSensor.objects.get_or_create(
                    circuit_id=circuit_id,
                    defaults=sensor_data
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Created sensor: {sensor.name} (Circuit ID: {circuit_id})'
                        )
                    )
                    created_count += 1
                else:
                    # Update existing sensor if needed
                    sensor.name = sensor_data['name']
                    sensor.description = sensor_data['description']
                    sensor.is_active = sensor_data['is_active']
                    sensor.save()
                    
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Updated existing sensor: {sensor.name} (Circuit ID: {circuit_id})'
                        )
                    )
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error creating sensor {sensor_data["name"]}: {e}'
                    )
                )
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {created_count} sensors created, {updated_count} sensors updated'
            )
        )
        
        # List all temperature sensors
        self.stdout.write('\nCurrent temperature sensors in database:')
        all_sensors = TemperatureSensor.objects.all().order_by('name')
        for sensor in all_sensors:
            status = '🟢 Active' if sensor.is_active else '🔴 Inactive'
            online = '🟢 Online' if sensor.is_online else '🔴 Offline'
            self.stdout.write(
                f'  • {sensor.name} ({sensor.circuit_id}) - {status} - {online}'
            )
