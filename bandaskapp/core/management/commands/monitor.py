import time
import logging
import signal
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

from hardware.controller import HardwareController
from core.models import SystemLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bandaskapp.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Monitor and control the heating system'
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.controller = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Monitoring interval in seconds (default: 10)'
        )
        parser.add_argument(
            '--sync-interval',
            type=int,
            default=300,  # 5 minutes
            help='Relay state sync interval in seconds (default: 300)'
        )
    
    def handle(self, *args, **options):
        self.interval = options['interval']
        self.sync_interval = options['sync_interval']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting BandaskApp monitoring (interval: {self.interval}s)...')
        )
        
        # Initialize hardware controller
        self.controller = HardwareController()
        
        # Log startup
        SystemLog.objects.create(
            level='info',
            message=f'BandaskApp monitoring started (interval: {self.interval}s)',
            component='monitor'
        )
        
        # Sync relay states on startup
        self.stdout.write('Synchronizing relay states on startup...')
        self.controller.sync_relay_states()
        
        # Main monitoring loop
        last_sync_time = time.time()
        
        try:
            while self.running:
                loop_start = time.time()
                
                try:
                    # Main control logic
                    self._monitoring_cycle()
                    
                    # Periodic relay state sync
                    if (time.time() - last_sync_time) >= self.sync_interval:
                        self.stdout.write('Performing periodic relay state sync...')
                        self.controller.sync_relay_states()
                        last_sync_time = time.time()
                    
                except Exception as e:
                    error_msg = f"Error in monitoring cycle: {e}"
                    logger.error(error_msg)
                    SystemLog.objects.create(
                        level='error',
                        message=error_msg,
                        component='monitor'
                    )
                
                # Sleep for the remaining interval time
                loop_duration = time.time() - loop_start
                sleep_time = max(0, self.interval - loop_duration)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Received interrupt signal'))
        
        self._shutdown()
    
    def _monitoring_cycle(self):
        """Execute one monitoring cycle"""
        
        # Check API connectivity
        if not self.controller.check_api_connectivity():
            logger.warning("EVOK API connectivity issues detected")
            return
        
        # Update temperature readings from enabled sensors only
        temp1 = self.controller.update_temperature()
        if temp1 is not None:
            logger.info(f"DHW Top temperature: {temp1:.1f}°C")
        else:
            logger.debug("DHW Top temperature sensor is disabled or unavailable")
        
        temp2 = self.controller.update_temperature_2()
        if temp2 is not None:
            logger.info(f"DHW Middle temperature: {temp2:.1f}°C")
        else:
            logger.debug("DHW Middle temperature sensor is disabled or unavailable")
        
        temp3 = self.controller.update_temperature_3()
        if temp3 is not None:
            logger.info(f"DHW Bottom temperature: {temp3:.1f}°C")
        else:
            logger.debug("DHW Bottom temperature sensor is disabled or unavailable")
        
        # Execute furnace control logic (only if DHW 1 is enabled)
        if temp1 is not None:
            control_action = self.controller.control_furnace()
            if control_action:
                status = self.controller.get_system_status()
                furnace_state = "ON" if status.get('furnace_running') else "OFF"
                logger.info(f"Furnace control action: {furnace_state}")
        else:
            logger.debug("Skipping furnace control - DHW Top sensor is disabled")
        
        # Log system status periodically (every 10 cycles)
        if hasattr(self, '_cycle_count'):
            self._cycle_count += 1
        else:
            self._cycle_count = 1
        
        if self._cycle_count % 10 == 0:
            status = self.controller.get_system_status()
            enabled_sensors = []
            if status.get('dhw_temperature') is not None:
                enabled_sensors.append(f"DHW Top={status.get('dhw_temperature', 0):.1f}°C")
            if status.get('dhw_temperature_2') is not None:
                enabled_sensors.append(f"DHW Middle={status.get('dhw_temperature_2', 0):.1f}°C")
            if status.get('dhw_temperature_3') is not None:
                enabled_sensors.append(f"DHW Bottom={status.get('dhw_temperature_3', 0):.1f}°C")
            
            sensor_status = ", ".join(enabled_sensors) if enabled_sensors else "No enabled sensors"
            logger.info(f"System status: Mode={status.get('control_mode')}, "
                       f"Furnace={status.get('furnace_running')}, "
                       f"Sensors: {sensor_status}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
        self.stdout.write(self.style.WARNING(f'Received {signal_name} signal, shutting down...'))
        self.running = False
    
    def _shutdown(self):
        """Perform graceful shutdown"""
        self.stdout.write(self.style.SUCCESS('Shutting down BandaskApp monitoring...'))
        
        # Log shutdown
        SystemLog.objects.create(
            level='info',
            message='BandaskApp monitoring stopped',
            component='monitor'
        )
        
        self.stdout.write(self.style.SUCCESS('BandaskApp monitoring stopped successfully'))


