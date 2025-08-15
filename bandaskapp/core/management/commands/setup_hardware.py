from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import TemperatureSensor, Relay, SystemState, SystemLog

class Command(BaseCommand):
    help = 'Set up initial hardware configuration for BandaskApp'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up BandaskApp hardware configuration...'))
        
        # Get configuration
        config = settings.BANDASKAPP_CONFIG
        
        # Create DHW temperature sensor
        dhw_sensor, created = TemperatureSensor.objects.get_or_create(
            circuit_id=config['THERMOMETER_DHW_1_ID'],
            defaults={
                'name': 'DHW-1',
                'location': 'Upper tank',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created DHW temperature sensor: {dhw_sensor.name}')
        else:
            self.stdout.write(f'✓ DHW temperature sensor already exists: {dhw_sensor.name}')
        
        # Create furnace relay
        furnace_relay, created = Relay.objects.get_or_create(
            circuit_id=config['FURNACE_RELAY_ID'],
            defaults={
                'name': 'Furnace',
                'purpose': 'Control furnace on/off for DHW heating',
                'current_state': False,
                'expected_state': False,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f'✓ Created furnace relay: {furnace_relay.name}')
        else:
            self.stdout.write(f'✓ Furnace relay already exists: {furnace_relay.name}')
        
        # Create system state
        system_state = SystemState.load()  # Uses singleton pattern
        self.stdout.write(f'✓ System state initialized: {system_state.control_mode} mode')
        
        # Log the setup
        SystemLog.objects.create(
            level='info',
            message='Hardware configuration setup completed',
            component='setup'
        )
        
        # Display current configuration
        self.stdout.write(self.style.SUCCESS('\nCurrent Hardware Configuration:'))
        self.stdout.write(f'  Temperature Sensors: {TemperatureSensor.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  Relays: {Relay.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  Control Mode: {system_state.control_mode}')
        self.stdout.write(f'  DHW Thresholds: {system_state.dhw_temp_low}°C - {system_state.dhw_temp_high}°C')
        
        self.stdout.write(self.style.SUCCESS('\nHardware setup completed successfully!'))

