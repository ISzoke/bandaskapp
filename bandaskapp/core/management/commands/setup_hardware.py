from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import TemperatureSensor, Relay, SystemState, SystemLog

class Command(BaseCommand):
    help = 'Set up initial hardware configuration for BandaskApp'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up BandaskApp hardware configuration...'))
        
        # Get configuration
        config = settings.BANDASKAPP_CONFIG
        
        # Clear existing hardware to start fresh
        self.stdout.write('Clearing existing hardware configuration...')
        TemperatureSensor.objects.all().delete()
        Relay.objects.all().delete()
        
        # Create all thermometers from the configuration array
        self.stdout.write('Creating temperature sensors...')
        active_sensors = 0
        for i, thermometer in enumerate(config['THERMOMETERS']):
            # Skip sensors labeled as 'NONE' (not shown in UI)
            if thermometer['label'] == 'NONE':
                continue
                
            # Create sensor name based on label
            sensor_name = thermometer['label'].replace(' ', '-')
            
            sensor = TemperatureSensor.objects.create(
                name=sensor_name,
                circuit_id=thermometer['id'],
                location=thermometer['label'],
                is_active=True,
            )
            
            self.stdout.write(f'✓ Created temperature sensor: {sensor.name} ({sensor.circuit_id})')
            active_sensors += 1
        
        # Create relays dynamically from configuration
        self.stdout.write('Creating relays...')
        relays_created = 0
        
        # Create furnace relay if configured
        if 'FURNACE_RELAY_ID' in config:
            furnace_relay = Relay.objects.create(
                name='Furnace',
                circuit_id=config['FURNACE_RELAY_ID'],
                purpose='Control furnace on/off for DHW and HHW heating',
                current_state=False,
                expected_state=False,
                is_active=True,
            )
            self.stdout.write(f'✓ Created furnace relay: {furnace_relay.name} ({furnace_relay.circuit_id})')
            relays_created += 1
        
        # Create pump relay if configured
        if 'PUMP_RELAY_ID' in config:
            pump_relay = Relay.objects.create(
                name='Pump',
                circuit_id=config['PUMP_RELAY_ID'],
                purpose='Control circulation pump for heating system',
                current_state=False,
                expected_state=False,
                is_active=True,
            )
            self.stdout.write(f'✓ Created pump relay: {pump_relay.name} ({pump_relay.circuit_id})')
            relays_created += 1
        
        # Create system state with new thresholds
        system_state = SystemState.load()  # Uses singleton pattern
        system_state.dhw_temp_low = config['DHW_THRESHOLDS']['low']
        system_state.dhw_temp_high = config['DHW_THRESHOLDS']['high']
        system_state.hhw_temp_low = config['HHW_THRESHOLDS']['low']
        system_state.hhw_temp_high = config['HHW_THRESHOLDS']['high']
        system_state.save()
        
        self.stdout.write(f'✓ System state initialized: {system_state.control_mode} mode')
        self.stdout.write(f'✓ DHW Thresholds: {system_state.dhw_temp_low}°C - {system_state.dhw_temp_high}°C')
        self.stdout.write(f'✓ HHW Thresholds: {system_state.hhw_temp_low}°C - {system_state.hhw_temp_high}°C')
        
        # Log the setup
        SystemLog.objects.create(
            level='info',
            message=f'Hardware configuration setup completed with {active_sensors} sensors and {relays_created} relays',
            component='setup'
        )
        
        # Display current configuration
        self.stdout.write(self.style.SUCCESS('\nCurrent Hardware Configuration:'))
        self.stdout.write(f'  Temperature Sensors: {active_sensors}')
        self.stdout.write(f'  Relays: {relays_created}')
        self.stdout.write(f'  Control Mode: {system_state.control_mode}')
        
        # Show all sensors
        self.stdout.write('\nTemperature Sensors:')
        for sensor in TemperatureSensor.objects.filter(is_active=True):
            self.stdout.write(f'  - {sensor.name}: {sensor.circuit_id} ({sensor.location})')
        
        # Show all relays
        self.stdout.write('\nRelays:')
        for relay in Relay.objects.filter(is_active=True):
            self.stdout.write(f'  - {relay.name}: {relay.circuit_id} ({relay.purpose})')
        
        self.stdout.write(self.style.SUCCESS('\nHardware setup completed successfully!'))
        self.stdout.write(self.style.WARNING('\nNote: You may need to restart the application for changes to take effect.'))

