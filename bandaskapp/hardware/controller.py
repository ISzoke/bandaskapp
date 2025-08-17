import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from django.utils import timezone
from django.conf import settings

from core.models import TemperatureSensor, Relay, SystemState, SystemLog, TemperatureLog
from .client import EVOKClient

logger = logging.getLogger(__name__)

class HardwareController:
    """Controller for managing hardware operations and control logic"""
    
    def __init__(self, client: Optional[EVOKClient] = None):
        self.client = client or EVOKClient()
        
        # Get configuration from settings
        self.config = settings.BANDASKAPP_CONFIG
        
        # Temperature thresholds (can be overridden by SystemState)
        self.dhw_temp_low = self.config['DHW_THRESHOLDS']['low']
        self.dhw_temp_high = self.config['DHW_THRESHOLDS']['high']
        
        # Cooldown periods (seconds)
        self.furnace_cooldown = self.config['COOLDOWN_TIMES']['furnace']
        self.last_furnace_switch = None
        
        # Temperature validation
        self.min_temp = self.config['TEMPERATURE_VALIDATION']['min_temp']
        self.max_temp = self.config['TEMPERATURE_VALIDATION']['max_temp']
        self.max_temp_jump = self.config['TEMPERATURE_VALIDATION']['max_jump']
        
        logger.info("Hardware Controller initialized")
    
    def _is_sensor_enabled(self, circuit_id: str) -> bool:
        """Check if a sensor is enabled (not set to NONE)"""
        return circuit_id != 'NONE'
    
    def update_temperature(self) -> Optional[float]:
        """
        Read DHW temperature from sensor and update database
        
        Returns:
            Current temperature value or None on error or if sensor is disabled
        """
        circuit_id = self.config['THERMOMETER_DHW_1_ID']
        
        # Skip if sensor is disabled
        if not self._is_sensor_enabled(circuit_id):
            logger.debug("DHW temperature sensor 1 is disabled (NONE)")
            return None
        
        try:
            # Get DHW sensor from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=circuit_id)
            
            # Read from hardware
            data = self.client.get_temperature(dhw_sensor.circuit_id)
            
            if data is None:
                # Communication error
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('error', f'Failed to read DHW temperature: {self.client.get_last_error()}')
                return None
            
            # Check if sensor is lost
            if data.get('lost', True):
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('warning', 'DHW temperature sensor is lost')
                return None
            
            # Get temperature value
            new_temp = data.get('value')
            if new_temp is None:
                self._log_system_event('error', 'DHW temperature reading returned no value')
                return None
            
            # Validate temperature
            if not self._validate_temperature(dhw_sensor, new_temp):
                return None
            
            # Update sensor in database
            dhw_sensor.current_value = new_temp
            dhw_sensor.last_reading = timezone.now()
            dhw_sensor.is_lost = False
            dhw_sensor.save()
            
            # Log temperature reading
            TemperatureLog.objects.create(
                sensor=dhw_sensor,
                value=new_temp
            )
            
            logger.debug(f"DHW temperature updated: {new_temp:.1f}°C")
            return new_temp
            
        except TemperatureSensor.DoesNotExist:
            self._log_system_event('error', 'DHW temperature sensor not found in database')
            return None
        except Exception as e:
            self._log_system_event('error', f'Error updating DHW temperature: {e}')
            return None
    
    def update_temperature_2(self) -> Optional[float]:
        """
        Read DHW temperature 2 (middle) from sensor and update database
        
        Returns:
            Current temperature value or None on error or if sensor is disabled
        """
        circuit_id = self.config['THERMOMETER_DHW_2_ID']
        
        # Skip if sensor is disabled
        if not self._is_sensor_enabled(circuit_id):
            logger.debug("DHW temperature sensor 2 is disabled (NONE)")
            return None
        
        try:
            # Get DHW sensor 2 from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=circuit_id)
            
            # Read from hardware
            data = self.client.get_temperature(dhw_sensor.circuit_id)
            
            if data is None:
                # Communication error
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('error', f'Failed to read DHW temperature 2: {self.client.get_last_error()}')
                return None
            
            # Check if sensor is lost
            if data.get('lost', True):
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('warning', 'DHW temperature sensor 2 is lost')
                return None
            
            # Get temperature value
            new_temp = data.get('value')
            if new_temp is None:
                self._log_system_event('error', 'DHW temperature 2 reading returned no value')
                return None
            
            # Validate temperature
            if not self._validate_temperature(dhw_sensor, new_temp):
                return None
            
            # Update sensor in database
            dhw_sensor.current_value = new_temp
            dhw_sensor.last_reading = timezone.now()
            dhw_sensor.is_lost = False
            dhw_sensor.save()
            
            # Log temperature reading
            TemperatureLog.objects.create(
                sensor=dhw_sensor,
                value=new_temp
            )
            
            logger.debug(f"DHW temperature 2 updated: {new_temp:.1f}°C")
            return new_temp
            
        except TemperatureSensor.DoesNotExist:
            self._log_system_event('error', 'DHW temperature sensor 2 not found in database')
            return None
        except Exception as e:
            self._log_system_event('error', f'Error updating DHW temperature 2: {e}')
            return None
    
    def update_temperature_3(self) -> Optional[float]:
        """
        Read DHW temperature 3 (bottom) from sensor and update database
        
        Returns:
            Current temperature value or None on error or if sensor is disabled
        """
        circuit_id = self.config['THERMOMETER_DHW_3_ID']
        
        # Skip if sensor is disabled
        if not self._is_sensor_enabled(circuit_id):
            logger.debug("DHW temperature sensor 3 is disabled (NONE)")
            return None
        
        try:
            # Get DHW sensor 3 from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=circuit_id)
            
            # Read from hardware
            data = self.client.get_temperature(dhw_sensor.circuit_id)
            
            if data is None:
                # Communication error
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('error', f'Failed to read DHW temperature 3: {self.client.get_last_error()}')
                return None
            
            # Check if sensor is lost
            if data.get('lost', True):
                dhw_sensor.is_lost = True
                dhw_sensor.save()
                self._log_system_event('warning', 'DHW temperature sensor 3 is lost')
                return None
            
            # Get temperature value
            new_temp = data.get('value')
            if new_temp is None:
                self._log_system_event('error', 'DHW temperature 3 reading returned no value')
                return None
            
            # Validate temperature
            if not self._validate_temperature(dhw_sensor, new_temp):
                return None
            
            # Update sensor in database
            dhw_sensor.current_value = new_temp
            dhw_sensor.last_reading = timezone.now()
            dhw_sensor.is_lost = False
            dhw_sensor.save()
            
            # Log temperature reading
            TemperatureLog.objects.create(
                sensor=dhw_sensor,
                value=new_temp
            )
            
            logger.debug(f"DHW temperature 3 updated: {new_temp:.1f}°C")
            return new_temp
            
        except TemperatureSensor.DoesNotExist:
            self._log_system_event('error', 'DHW temperature sensor 3 not found in database')
            return None
        except Exception as e:
            self._log_system_event('error', f'Error updating DHW temperature 3: {e}')
            return None
    
    def _validate_temperature(self, sensor: TemperatureSensor, new_temp: float) -> bool:
        """
        Validate temperature reading for anomalies
        
        Args:
            sensor: Temperature sensor model instance
            new_temp: New temperature reading
            
        Returns:
            True if temperature is valid, False otherwise
        """
        # Check range
        if new_temp < self.min_temp or new_temp > self.max_temp:
            self._log_system_event(
                'warning', 
                f'DHW temperature out of range: {new_temp:.1f}°C (valid range: {self.min_temp}-{self.max_temp}°C)'
            )
            return False
        
        # Check for large jumps
        if sensor.current_value is not None:
            temp_diff = abs(new_temp - sensor.current_value)
            if temp_diff > self.max_temp_jump:
                self._log_system_event(
                    'warning',
                    f'DHW temperature jump detected: {temp_diff:.1f}°C (from {sensor.current_value:.1f}°C to {new_temp:.1f}°C)'
                )
                return False
        
        return True
    
    def control_furnace(self) -> bool:
        """
        Control furnace based on DHW temperature and system state
        
        Returns:
            True if control action was taken, False otherwise
        """
        try:
            # Get system state
            system_state = SystemState.load()
            
            # Skip if in manual mode
            if system_state.control_mode == 'manual':
                logger.debug("System in manual mode, skipping automatic furnace control")
                return False
            
            # Update thresholds from system state
            self.dhw_temp_low = system_state.dhw_temp_low
            self.dhw_temp_high = system_state.dhw_temp_high
            
            # Get current temperature
            current_temp = self.update_temperature()
            if current_temp is None:
                logger.warning("Cannot control furnace: no valid temperature reading")
                return False
            
            # Get furnace relay using circuit ID
            furnace = Relay.objects.get(circuit_id=self.config['FURNACE_RELAY_ID'])
            
            # Check cooldown period
            if self._is_furnace_in_cooldown():
                logger.debug("Furnace in cooldown period, skipping control")
                return False
            
            # Determine if furnace should be running
            should_run = self._should_furnace_run(current_temp, furnace.current_state)
            
            # Only act if state should change
            if should_run == furnace.current_state:
                return False
            
            # Set relay state
            success = self._set_relay_state(furnace, should_run)
            if success:
                # Update system state
                system_state.furnace_running = should_run
                system_state.save()
                
                # Log the action
                action = "started" if should_run else "stopped"
                self._log_system_event(
                    'info',
                    f'Furnace {action} (DHW temp: {current_temp:.1f}°C, threshold: {self.dhw_temp_low}-{self.dhw_temp_high}°C)'
                )
                
                # Update cooldown timer
                self.last_furnace_switch = time.time()
                
                return True
            
            return False
            
        except Relay.DoesNotExist:
            self._log_system_event('error', 'Furnace relay not found in database')
            return False
        except Exception as e:
            self._log_system_event('error', f'Error controlling furnace: {e}')
            return False
    
    def _should_furnace_run(self, current_temp: float, current_state: bool) -> bool:
        """
        Determine if furnace should be running based on temperature and current state
        
        Args:
            current_temp: Current DHW temperature
            current_state: Current furnace state (True=ON, False=OFF)
            
        Returns:
            True if furnace should run, False otherwise
        """
        if not current_state and current_temp < self.dhw_temp_low:
            # Furnace is OFF and temperature is below low threshold - start furnace
            return True
        elif current_state and current_temp >= self.dhw_temp_high:
            # Furnace is ON and temperature reached high threshold - stop furnace
            return False
        else:
            # No change needed - maintain current state
            return current_state
    
    def _is_furnace_in_cooldown(self) -> bool:
        """Check if furnace is in cooldown period"""
        if self.last_furnace_switch is None:
            return False
        return (time.time() - self.last_furnace_switch) < self.furnace_cooldown
    
    def manual_control_furnace(self, state: bool) -> bool:
        """
        Manually control furnace (override automatic control)
        
        Args:
            state: True for ON, False for OFF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            furnace = Relay.objects.get(circuit_id=self.config['FURNACE_RELAY_ID'])
            
            success = self._set_relay_state(furnace, state)
            if success:
                # Update system state
                system_state = SystemState.load()
                system_state.furnace_running = state
                system_state.save()
                
                # Log manual action
                action = "ON" if state else "OFF"
                self._log_system_event('info', f'Furnace manually set to {action}')
                
                return True
            
            return False
            
        except Relay.DoesNotExist:
            self._log_system_event('error', 'Furnace relay not found in database')
            return False
        except Exception as e:
            self._log_system_event('error', f'Error in manual furnace control: {e}')
            return False
    
    def _set_relay_state(self, relay: Relay, state: bool) -> bool:
        """
        Set relay state and update database
        
        Args:
            relay: Relay model instance
            state: True for ON, False for OFF
            
        Returns:
            True if successful, False otherwise
        """
        # Set expected state
        relay.expected_state = state
        relay.save()
        
        # Send command to hardware
        result = self.client.set_relay_state(relay.circuit_id, state)
        
        if result and result.get('success'):
            # Update current state
            relay.current_state = state
            relay.save()
            return True
        else:
            # Hardware command failed
            error_msg = f"Failed to set {relay.name} relay: {self.client.get_last_error()}"
            self._log_system_event('error', error_msg)
            return False
    
    def sync_relay_states(self) -> None:
        """Synchronize actual vs expected relay states"""
        try:
            for relay in Relay.objects.filter(is_active=True):
                # Read actual state from hardware
                data = self.client.get_relay_state(relay.circuit_id)
                
                if data is not None:
                    actual_state = bool(data.get('value', 0))
                    
                    # Update current state
                    relay.current_state = actual_state
                    relay.save()
                    
                    # Check for mismatch
                    if actual_state != relay.expected_state:
                        self._log_system_event(
                            'warning',
                            f'Relay state mismatch for {relay.name}: expected {relay.expected_state}, actual {actual_state}'
                        )
                        
                        # Try to correct the state
                        self._set_relay_state(relay, relay.expected_state)
                
        except Exception as e:
            self._log_system_event('error', f'Error syncing relay states: {e}')
    
    def check_api_connectivity(self) -> bool:
        """
        Check API connectivity and log warnings if needed
        
        Returns:
            True if API is reachable, False otherwise
        """
        if self.client.test_connection():
            return True
        else:
            self._log_system_event('error', f'EVOK API unreachable: {self.client.get_last_error()}')
            return False
    
    def _log_system_event(self, level: str, message: str) -> None:
        """Log system event to database"""
        try:
            SystemLog.objects.create(
                level=level,
                message=message,
                component='hardware_controller'
            )
        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
    
    def get_system_status(self) -> dict:
        """
        Get current system status
        
        Returns:
            Dictionary with system status information
        """
        try:
            system_state = SystemState.load()
            furnace = Relay.objects.get(circuit_id=self.config['FURNACE_RELAY_ID'])
            
            # Initialize status with disabled sensors
            status = {
                'control_mode': system_state.control_mode,
                'furnace_running': furnace.current_state,
                'dhw_temp_thresholds': {
                    'low': system_state.dhw_temp_low,
                    'high': system_state.dhw_temp_high,
                },
                'api_connected': self.client.get_last_error() is None,
            }
            
            # Check DHW sensor 1
            if self._is_sensor_enabled(self.config['THERMOMETER_DHW_1_ID']):
                try:
                    dhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['THERMOMETER_DHW_1_ID'])
                    status.update({
                        'dhw_temperature': dhw_sensor.current_value,
                        'dhw_sensor_online': dhw_sensor.is_online,
                        'last_reading': dhw_sensor.last_reading,
                    })
                except TemperatureSensor.DoesNotExist:
                    status.update({
                        'dhw_temperature': None,
                        'dhw_sensor_online': False,
                        'last_reading': None,
                    })
            else:
                status.update({
                    'dhw_temperature': None,
                    'dhw_sensor_online': False,
                    'last_reading': None,
                })
            
            # Check DHW sensor 2
            if self._is_sensor_enabled(self.config['THERMOMETER_DHW_2_ID']):
                try:
                    dhw_sensor_2 = TemperatureSensor.objects.get(circuit_id=self.config['THERMOMETER_DHW_2_ID'])
                    status.update({
                        'dhw_temperature_2': dhw_sensor_2.current_value,
                        'dhw_sensor_2_online': dhw_sensor_2.is_online,
                    })
                except TemperatureSensor.DoesNotExist:
                    status.update({
                        'dhw_temperature_2': None,
                        'dhw_sensor_2_online': False,
                    })
            else:
                status.update({
                    'dhw_temperature_2': None,
                    'dhw_sensor_2_online': False,
                })
            
            # Check DHW sensor 3
            if self._is_sensor_enabled(self.config['THERMOMETER_DHW_3_ID']):
                try:
                    dhw_sensor_3 = TemperatureSensor.objects.get(circuit_id=self.config['THERMOMETER_DHW_3_ID'])
                    status.update({
                        'dhw_temperature_3': dhw_sensor_3.current_value,
                        'dhw_sensor_3_online': dhw_sensor_3.is_online,
                    })
                except TemperatureSensor.DoesNotExist:
                    status.update({
                        'dhw_temperature_3': None,
                        'dhw_sensor_3_online': False,
                    })
            else:
                status.update({
                    'dhw_temperature_3': None,
                    'dhw_sensor_3_online': False,
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'error': str(e)
            }

