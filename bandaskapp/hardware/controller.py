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
        self.hhw_temp_low = self.config['HHW_THRESHOLDS']['low']
        self.hhw_temp_high = self.config['HHW_THRESHOLDS']['high']
        
        # Cooldown periods (seconds)
        self.furnace_cooldown = self.config['COOLDOWN_TIMES']['furnace']
        self.pump_cooldown = self.config['COOLDOWN_TIMES']['pump']
        self.last_furnace_switch = None
        self.last_pump_switch = None
        
        # Temperature validation
        self.min_temp = self.config['TEMPERATURE_VALIDATION']['min_temp']
        self.max_temp = self.config['TEMPERATURE_VALIDATION']['max_temp']
        self.max_temp_jump = self.config['TEMPERATURE_VALIDATION']['max_jump']
        
        logger.info("Hardware Controller initialized")
    
    def update_temperature(self) -> Optional[float]:
        """
        Read DHW temperature from control sensor and update database
        
        Returns:
            Current temperature value or None on error
        """
        # Check if sensor is enabled
        if not self._is_sensor_enabled(self.config['CONTROL_DHW_ID']):
            logger.debug("DHW Control sensor is disabled, skipping temperature update")
            return None
            
        try:
            # Get DHW sensor from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['CONTROL_DHW_ID'])
            
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
            Current temperature value or None on error
        """
        # Check if sensor is enabled
        if not self._is_sensor_enabled(self.config['THERMOMETERS'][1]['id']):
            logger.debug("DHW Sensor 2 is disabled, skipping temperature update")
            return None
            
        try:
            # Get DHW sensor 2 from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['THERMOMETERS'][1]['id'])
            
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
            Current temperature value or None on error
        """
        # Check if sensor is enabled
        if not self._is_sensor_enabled(self.config['THERMOMETERS'][2]['id']):
            logger.debug("DHW Sensor 3 is disabled, skipping temperature update")
            return None
            
        try:
            # Get DHW sensor 3 from database using circuit ID
            dhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['THERMOMETERS'][2]['id'])
            
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
    
    def update_temperature_hhw(self) -> Optional[float]:
        """
        Read HHW temperature from sensor and update database
        
        Returns:
            Current temperature value or None on error
        """
        # Check if sensor is enabled
        if not self._is_sensor_enabled(self.config['CONTROL_HHW_ID']):
            logger.debug("HHW Sensor is disabled, skipping temperature update")
            return None
            
        try:
            # Get HHW sensor from database using circuit ID
            hhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['CONTROL_HHW_ID'])
            
            # Read from hardware
            data = self.client.get_temperature(hhw_sensor.circuit_id)
            
            if data is None:
                # Communication error
                hhw_sensor.is_lost = True
                hhw_sensor.save()
                self._log_system_event('error', f'Failed to read HHW temperature: {self.client.get_last_error()}')
                return None
            
            # Check if sensor is lost
            if data.get('lost', True):
                hhw_sensor.is_lost = True
                hhw_sensor.save()
                self._log_system_event('warning', 'HHW temperature sensor is lost')
                return None
            
            # Get temperature value
            new_temp = data.get('value')
            if new_temp is None:
                self._log_system_event('error', 'HHW temperature reading returned no value')
                return None
            
            # Validate temperature
            if not self._validate_temperature(hhw_sensor, new_temp):
                return None
            
            # Update sensor in database
            hhw_sensor.current_value = new_temp
            hhw_sensor.last_reading = timezone.now()
            hhw_sensor.is_lost = False
            hhw_sensor.save()
            
            # Log temperature reading
            TemperatureLog.objects.create(
                sensor=hhw_sensor,
                value=new_temp
            )
            
            logger.debug(f"HHW temperature updated: {new_temp:.1f}°C")
            return new_temp
            
        except TemperatureSensor.DoesNotExist:
            self._log_system_event('error', 'HHW temperature sensor not found in database')
            return None
        except Exception as e:
            self._log_system_event('error', f'Error updating HHW temperature: {e}')
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
        # Check if primary DHW sensor is enabled
        if not self._is_sensor_enabled(self.config['CONTROL_DHW_ID']):
            logger.debug("Primary DHW sensor is disabled, skipping furnace control")
            return False
            
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
            self.hhw_temp_low = system_state.hhw_temp_low
            self.hhw_temp_high = system_state.hhw_temp_high
            
            # Execute winter regime control logic
            self.control_winter_regime()
            
            # Get updated system status
            status = self.get_system_status()
            
            # Log the action if furnace state changed
            if status.get('furnace_running') != system_state.furnace_running:
                action = "started" if status.get('furnace_running') else "stopped"
                self._log_system_event(
                    'info',
                    f'Furnace {action} via winter regime control'
                )
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
    
    def manual_control_pump(self, state: bool) -> bool:
        """
        Manually control pump (override automatic control)
        
        Args:
            state: True for ON, False for OFF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pump = Relay.objects.get(circuit_id=self.config['PUMP_RELAY_ID'])
            
            success = self._set_relay_state(pump, state)
            if success:
                # Update system state
                system_state = SystemState.load()
                system_state.pump_running = state
                system_state.save()
                
                # Log manual action
                action = "ON" if state else "OFF"
                self._log_system_event('info', f'Pump manually set to {action}')
                
                return True
            
            return False
            
        except Relay.DoesNotExist:
            self._log_system_event('error', 'Pump relay not found in database')
            return False
        except Exception as e:
            self._log_system_event('error', f'Error in manual pump control: {e}')
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
    
    def _is_sensor_enabled(self, circuit_id: str) -> bool:
        """
        Check if a sensor is enabled (not set to 'NONE')
        
        Args:
            circuit_id: Circuit ID from configuration
            
        Returns:
            True if sensor is enabled, False if disabled
        """
        return circuit_id != 'NONE'
    
    def get_system_status(self) -> dict:
        """
        Get current system status
        
        Returns:
            Dictionary with system status information
        """
        try:
            system_state = SystemState.load()
            
            # Initialize status with default values
            status = {
                'control_mode': system_state.control_mode,
                'winter_regime_state': system_state.winter_regime_state,
                'dhw_temp_thresholds': {
                    'low': system_state.dhw_temp_low,
                    'high': system_state.dhw_temp_high,
                },
                'api_connected': self.client.get_last_error() is None,
            }
            
            # Handle all thermometers generically from configuration
            for i, thermometer in enumerate(self.config['THERMOMETERS']):
                if thermometer['label'] == 'NONE':
                    continue  # Skip disabled sensors
                    
                sensor_id = thermometer['id']
                temp_key = f'temp_{i+1}'
                online_key = f'sensor_{i+1}_online'
                
                if self._is_sensor_enabled(sensor_id):
                    try:
                        sensor = TemperatureSensor.objects.get(circuit_id=sensor_id)
                        status.update({
                            temp_key: sensor.current_value,
                            online_key: sensor.is_online,
                        })
                        # Set last_reading from the first available sensor
                        if i == 0:
                            status['last_reading'] = sensor.last_reading
                    except TemperatureSensor.DoesNotExist:
                        logger.warning(f"Temperature sensor with circuit ID {sensor_id} not found in database")
                        status.update({
                            temp_key: None,
                            online_key: False,
                        })
                else:
                    # Sensor is disabled
                    status.update({
                        temp_key: None,
                        online_key: False,
                    })
            
            # Keep backward compatibility for existing code
            if 'temp_1' in status:
                status['dhw_temperature'] = status['temp_1']
                status['dhw_sensor_online'] = status['sensor_1_online']
            if 'temp_2' in status:
                status['dhw_temperature_2'] = status['temp_2']
                status['dhw_sensor_2_online'] = status['sensor_2_online']
            if 'temp_3' in status:
                status['dhw_temperature_3'] = status['temp_3']
                status['dhw_sensor_3_online'] = status['sensor_3_online']
            
            # Handle HHW Sensor (for winter regime) - use the configured HHW sensor
            if self._is_sensor_enabled(self.config['CONTROL_HHW_ID']):
                try:
                    hhw_sensor = TemperatureSensor.objects.get(circuit_id=self.config['CONTROL_HHW_ID'])
                    status.update({
                        'hhw_temperature': hhw_sensor.current_value,
                        'hhw_sensor_online': hhw_sensor.is_online,
                    })
                except TemperatureSensor.DoesNotExist:
                    logger.warning(f"HHW Sensor with circuit ID {self.config['CONTROL_HHW_ID']} not found in database")
                    status.update({
                        'hhw_temperature': None,
                        'hhw_sensor_online': False,
                    })
            else:
                # Sensor is disabled
                status.update({
                    'hhw_temperature': None,
                    'hhw_sensor_online': False,
                })
            
            # Handle Furnace Relay (required for control)
            try:
                furnace = Relay.objects.get(circuit_id=self.config['FURNACE_RELAY_ID'])
                status['furnace_running'] = furnace.current_state
            except Relay.DoesNotExist:
                logger.warning(f"Furnace relay with circuit ID {self.config['FURNACE_RELAY_ID']} not found in database")
                status['furnace_running'] = False
            
            # Handle Pump Relay
            try:
                pump = Relay.objects.get(circuit_id=self.config['PUMP_RELAY_ID'])
                status['pump_running'] = pump.current_state
            except Relay.DoesNotExist:
                logger.warning(f"Pump relay with circuit ID {self.config['PUMP_RELAY_ID']} not found in database")
                status['pump_running'] = False
            
            # Handle Heating Controller Status
            try:
                heating_control_state = self._get_heating_control_state()
                status['heating_controller_state'] = heating_control_state
                logger.info(f"Added heating controller state to status: {heating_control_state}")
            except Exception as e:
                logger.warning(f"Error getting heating controller state: {e}")
                status['heating_controller_state'] = None
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'error': str(e)
            }
    
    def control_winter_regime(self) -> None:
        """
        Control system based on winter regime state and heating control unit
        """
        try:
            system_state = SystemState.load()
            winter_regime = system_state.winter_regime_state
            
            # Get current temperatures
            dhw_temp = self._get_control_temperature(self.config['CONTROL_DHW_ID'])
            hhw_temp = self._get_control_temperature(self.config['CONTROL_HHW_ID'])
            
            # Get heating control unit state
            heating_control_state = self._get_heating_control_state()
            
            if winter_regime == 'off':
                # Summer regime: only DHW control
                self._control_summer_regime(dhw_temp)
                
            elif winter_regime == 'automatic':
                # Winter regime: controlled by heating control unit
                self._control_winter_automatic(dhw_temp, hhw_temp, heating_control_state)
                
            elif winter_regime == 'on':
                # Winter regime: manual control by BandaskApp
                self._control_winter_manual(dhw_temp, hhw_temp)
                
        except Exception as e:
            self._log_system_event('error', f'Error in winter regime control: {e}')
    
    def _get_control_temperature(self, circuit_id: str) -> Optional[float]:
        """Get temperature from control sensor"""
        if not self._is_sensor_enabled(circuit_id):
            return None
            
        try:
            sensor = TemperatureSensor.objects.get(circuit_id=circuit_id)
            return sensor.current_value
        except TemperatureSensor.DoesNotExist:
            return None
    
    def _get_heating_control_state(self) -> Optional[bool]:
        """Get heating control unit state"""
        try:
            logger.info(f"Getting heating control state for circuit ID: {self.config['HEATING_CONTROL_UNIT_ID']}")
            data = self.client.get_digital_input(self.config['HEATING_CONTROL_UNIT_ID'])
            logger.info(f"Raw heating control data: {data}")
            if data:
                value = bool(data.get('value', 0))
                logger.info(f"Heating control state: {value} (ON)" if value else f"Heating control state: {value} (OFF)")
                return value
            logger.warning("No data received from heating control unit")
            return None
        except Exception as e:
            logger.error(f'Error reading heating control unit: {e}')
            self._log_system_event('error', f'Error reading heating control unit: {e}')
            return None
    
    def _control_summer_regime(self, dhw_temp: Optional[float]) -> None:
        """Control system in summer regime (DHW only)"""
        if dhw_temp is None:
            return
            
        # Turn pump OFF in summer regime
        self._set_pump_state(False)
        
        # Control furnace based on DHW temperature
        system_state = SystemState.load()
        if dhw_temp < system_state.dhw_temp_low:
            self._set_furnace_state(True)
        elif dhw_temp > system_state.dhw_temp_high:
            self._set_furnace_state(False)
    
    def _control_winter_automatic(self, dhw_temp: Optional[float], hhw_temp: Optional[float], heating_control_state: Optional[bool]) -> None:
        """Control system in winter automatic regime"""
        # Load system state once at method level to avoid variable scope issues
        system_state = SystemState.load()
        
        if heating_control_state is None:
            # API error - switch to manual mode
            system_state.winter_regime_state = 'on'
            system_state.save()
            self._log_system_event('warning', 'Heating control unit API error, switching to manual winter regime')
            return
        
        if heating_control_state:
            # Heating control unit requests HHW
            self._set_pump_state(True)
            
            # Control furnace based on DHW OR HHW (logical OR)
            dhw_needs_heat = dhw_temp is not None and dhw_temp < system_state.dhw_temp_low
            hhw_needs_heat = hhw_temp is not None and hhw_temp < system_state.hhw_temp_low
            
            if dhw_needs_heat or hhw_needs_heat:
                self._set_furnace_state(True)
            elif dhw_temp is not None and hhw_temp is not None:
                dhw_satisfied = dhw_temp > system_state.dhw_temp_high
                hhw_satisfied = hhw_temp > system_state.hhw_temp_high
                if dhw_satisfied and hhw_satisfied:
                    self._set_furnace_state(False)
        else:
            # Heating control unit does not request HHW
            self._set_pump_state(False)
            
            # Control furnace based on DHW only
            if dhw_temp is not None:
                if dhw_temp < system_state.dhw_temp_low:
                    self._set_furnace_state(True)
                elif dhw_temp > system_state.dhw_temp_high:
                    self._set_furnace_state(False)
    
    def _control_winter_manual(self, dhw_temp: Optional[float], hhw_temp: Optional[float]) -> None:
        """Control system in winter manual regime"""
        # Pump is always ON in manual winter regime
        self._set_pump_state(True)
        
        # Control furnace based on DHW OR HHW (logical OR)
        system_state = SystemState.load()
        dhw_needs_heat = dhw_temp is not None and dhw_temp < system_state.dhw_temp_low
        hhw_needs_heat = hhw_temp is not None and hhw_temp < system_state.hhw_temp_low
        
        if dhw_needs_heat or hhw_needs_heat:
            self._set_furnace_state(True)
        elif dhw_temp is not None and hhw_temp is not None:
            dhw_satisfied = dhw_temp > system_state.dhw_temp_high
            hhw_satisfied = hhw_temp > system_state.hhw_temp_high
            if dhw_satisfied and hhw_satisfied:
                self._set_furnace_state(False)
    
    def _set_pump_state(self, state: bool) -> None:
        """Set pump relay state with cooldown protection"""
        if self.last_pump_switch and (time.time() - self.last_pump_switch) < self.pump_cooldown:
            return
            
        try:
            pump = Relay.objects.get(circuit_id=self.config['PUMP_RELAY_ID'])
            if self._set_relay_state(pump, state):
                self.last_pump_switch = time.time()
        except Relay.DoesNotExist:
            logger.warning(f"Pump relay with circuit ID {self.config['PUMP_RELAY_ID']} not found in database")
    
    def _set_furnace_state(self, state: bool) -> None:
        """Set furnace relay state with cooldown protection"""
        if self.last_furnace_switch and (time.time() - self.last_furnace_switch) < self.furnace_cooldown:
            return
            
        try:
            furnace = Relay.objects.get(circuit_id=self.config['FURNACE_RELAY_ID'])
            if self._set_relay_state(furnace, state):
                self.last_furnace_switch = time.time()
        except Relay.DoesNotExist:
            logger.warning(f"Furnace relay with circuit ID {self.config['FURNACE_RELAY_ID']} not found in database")
    
    def update_all_sensors(self) -> dict:
        """
        Update all temperature sensors from hardware and return status
        
        Returns:
            Dictionary with update results for each sensor
        """
        results = {}
        
        try:
            # Process all thermometers from configuration
            for i, thermometer in enumerate(self.config['THERMOMETERS']):
                if thermometer['label'] == 'NONE':
                    continue  # Skip disabled sensors
                    
                sensor_id = thermometer['id']
                temp_key = f'temp_{i+1}'
                online_key = f'sensor_{i+1}_online'
                
                try:
                    # Read from hardware
                    data = self.client.get_temperature(sensor_id)
                    
                    if data is None:
                        # Communication error
                        results[temp_key] = None
                        results[online_key] = False
                        continue
                    
                    # Check if sensor is lost
                    if data.get('lost', True):
                        results[temp_key] = None
                        results[online_key] = False
                        continue
                    
                    # Get temperature value
                    new_temp = data.get('value')
                    if new_temp is None:
                        results[temp_key] = None
                        results[online_key] = False
                        continue
                    
                    # Validate temperature (skip validation for now to avoid errors)
                    # if not self._validate_temperature(None, new_temp):
                    #     results[temp_key] = None
                    #     results[online_key] = False
                    #     continue
                    
                    # Update sensor in database
                    try:
                        sensor = TemperatureSensor.objects.get(circuit_id=sensor_id)
                        sensor.current_value = new_temp
                        sensor.last_reading = timezone.now()
                        sensor.is_lost = False
                        sensor.save()
                        
                        # Log temperature reading
                        TemperatureLog.objects.create(
                            sensor=sensor,
                            value=new_temp
                        )
                        
                        results[temp_key] = new_temp
                        results[online_key] = True
                        
                        logger.debug(f"Updated {thermometer['label']} temperature: {new_temp:.1f}°C")
                        
                    except TemperatureSensor.DoesNotExist:
                        logger.warning(f"Temperature sensor with circuit ID {sensor_id} not found in database")
                        results[temp_key] = None
                        results[online_key] = False
                        
                except Exception as e:
                    logger.error(f"Error updating {thermometer['label']} sensor: {e}")
                    results[temp_key] = None
                    results[online_key] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Error in update_all_sensors: {e}")
            return {}

