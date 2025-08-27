#!/usr/bin/env python3
"""
EVOK API Simulator for BandaskApp Development
Simulates the Unipi1.1 EVOK API for testing purposes with realistic temperature cycling
"""
import json
import time
import threading
import math
import sys
import select
import tty
import termios
import os
import django
from datetime import datetime
from flask import Flask, jsonify, request

# Setup Django environment to access settings
import sys
import os

# Add the parent directory to Python path to find the Django project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')
django.setup()
from django.conf import settings

app = Flask(__name__)

# Get configuration from Django settings
CONFIG = settings.BANDASKAPP_CONFIG
FURNACE_RELAY_ID = CONFIG['FURNACE_RELAY_ID']
PUMP_RELAY_ID = CONFIG['PUMP_RELAY_ID']
HEATING_CONTROL_UNIT_ID = CONFIG['HEATING_CONTROL_UNIT_ID']
CONTROL_DHW_ID = CONFIG['CONTROL_DHW_ID']
CONTROL_HHW_ID = CONFIG['CONTROL_HHW_ID']

class EVOKSimulator:
    def __init__(self):
        # Temperature sensors - Initialize from new array-based configuration
        self.sensors = {}
        
        # Process thermometer configuration from settings
        for i, thermometer in enumerate(CONFIG['THERMOMETERS']):
            if thermometer['id'] != 'NONE':
                # Generate address based on index for compatibility
                address = thermometer['id'] #f"28.95DCD5090000.{35 + i:02d}"
                
                self.sensors[thermometer['id']] = {
                    'dev': 'temp',
                    'circuit': thermometer['id'],
                    'address': address,
                    'value': 15.0,  # Start below 45°C threshold
                    'lost': False,
                    'time': time.time(),
                    'type': 'DS18B20'
                }


        # Relays - Furnace relay starts OFF
        self.relays = {
            FURNACE_RELAY_ID: {  # Furnace relay
                'dev': 'ro',
                'circuit': FURNACE_RELAY_ID,
                'value': 0  # OFF
            },
            PUMP_RELAY_ID: {  # Furnace relay
                'dev': 'ro',
                'circuit': PUMP_RELAY_ID,
                'value': 0  # OFF
            }
        }

        # Relays - Furnace relay starts OFF
        self.inputs = {
            HEATING_CONTROL_UNIT_ID: {  # Heating control unit input
                'dev': 'di',
                'circuit': HEATING_CONTROL_UNIT_ID,
                'value': 0  # OFF
            }
        }
        
        # Simulation parameters
        self.heating_rate = 2.0  # degrees per second when furnace is ON
        self.cooling_rate = 1.0  # degrees per second when furnace is OFF
        self.ambient_temp = 20.0  # ambient temperature
        
        # Temperature cycling parameters
        self.simulation_mode = 'auto'  # 'auto' or 'manual'
        self.cycle_start_time = time.time()
        self.cycle_period = 60  # 2 minutes for full cycle (30-70°C) - much faster!
        self.temp_min = 30.0
        self.temp_max = 70.0
        self.temp_center = (self.temp_min + self.temp_max) / 2  # 50°C
        self.temp_amplitude = (self.temp_max - self.temp_min) / 2  # 20°C
        self.manual_temp_adjustment = 0.0
        
        # Keyboard input handling
        self.old_settings = None
        self.setup_keyboard()
        
        # Heating control unit cycling parameters
        self.heating_control_cycle_start = time.time()
        self.heating_control_cycle_period = 15  # 15 seconds per state
        self.heating_control_manual_state = None  # None = auto cycling, 0/1 = manual state
        
        # Start background threads
        self.simulation_thread = threading.Thread(target=self._simulate_temperature, daemon=True)
        self.simulation_thread.start()
        
        self.heating_control_thread = threading.Thread(target=self._simulate_heating_control, daemon=True)
        self.heating_control_thread.start()
        
        self.keyboard_thread = threading.Thread(target=self._handle_keyboard, daemon=True)
        self.keyboard_thread.start()
        
        # Start heartbeat thread to monitor simulation
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
        
        print("EVOK Simulator started")
        # Display control configuration
        print(f"Control DHW ID: {CONTROL_DHW_ID}")
        if CONTROL_HHW_ID != CONTROL_DHW_ID:
            print(f"Control HHW ID: {CONTROL_HHW_ID} (separate from DHW)")
        else:
            print(f"Control HHW ID: {CONTROL_HHW_ID} (same as DHW)")
        print(f"Furnace Relay: {FURNACE_RELAY_ID}")
        print("")
        print("🎛️  SIMULATOR CONTROLS:")
        print("   M - Toggle between Auto/Manual mode")
        print("   ↑ - Increase temperature (+1°C) [Manual mode]")
        print("   ↓ - Decrease temperature (-1°C) [Manual mode]")
        print("   A - Reset to auto cycle")
        print("   H - Toggle heating control unit state")
        print("   Q - Quit simulator")
        print("")
        print(f"🔄 Auto mode: Cycling between {self.temp_min}°C - {self.temp_max}°C (sin wave, {self.cycle_period/60:.1f} min cycle)")
        print("")
    
    def setup_keyboard(self):
        """Setup keyboard input for interactive control"""
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except:
            # Not running in a terminal that supports this
            self.old_settings = None
    
    def cleanup_keyboard(self):
        """Restore keyboard settings"""
        if self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass
    
    def _handle_keyboard(self):
        """Handle keyboard input for manual control"""
        if not self.old_settings:
            return
            
        while True:
            try:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    if key.lower() == 'q':
                        print("\n🛑 Quitting simulator...")
                        self.cleanup_keyboard()
                        import os
                        os._exit(0)
                        
                    elif key.lower() == 'm':
                        self.simulation_mode = 'manual' if self.simulation_mode == 'auto' else 'auto'
                        mode_name = "🎮 MANUAL" if self.simulation_mode == 'manual' else "🔄 AUTO"
                        print(f"\r{datetime.now().strftime('%H:%M:%S')} - Mode: {mode_name}")
                        
                    elif key.lower() == 'a':
                        self.simulation_mode = 'auto'
                        self.manual_temp_adjustment = 0.0
                        self.cycle_start_time = time.time()
                        print(f"\r{datetime.now().strftime('%H:%M:%S')} - Reset to AUTO mode")
                        
                    elif key.lower() == 'h':
                        # Toggle heating control unit state
                        current_state = self.inputs[HEATING_CONTROL_UNIT_ID]['value']
                        new_state = 1 - current_state  # Toggle between 0 and 1
                        self.heating_control_manual_state = new_state
                        self.inputs[HEATING_CONTROL_UNIT_ID]['value'] = new_state
                        state_name = "ON" if new_state else "OFF"
                        print(f"\r{datetime.now().strftime('%H:%M:%S')} - Heating Control Unit: {state_name} (Manual)")
                        
                    elif key == '\x1b':  # ESC sequence for arrow keys
                        key = sys.stdin.read(2)
                        if key == '[A':  # Up arrow
                            if self.simulation_mode == 'manual':
                                self.manual_temp_adjustment += 1.0
                                if CONTROL_DHW_ID in self.sensors:
                                    new_temp = self.sensors[CONTROL_DHW_ID]['value'] + self.manual_temp_adjustment
                                    print(f"\r{datetime.now().strftime('%H:%M:%S')} - Manual: ↑ {new_temp:.1f}°C")
                        elif key == '[B':  # Down arrow
                            if self.simulation_mode == 'manual':
                                self.manual_temp_adjustment -= 1.0
                                if CONTROL_DHW_ID in self.sensors:
                                    new_temp = self.sensors[CONTROL_DHW_ID]['value'] + self.manual_temp_adjustment
                                    print(f"\r{datetime.now().strftime('%H:%M:%S')} - Manual: ↓ {new_temp:.1f}°C")
                                
            except:
                time.sleep(0.1)
    
    def _get_auto_cycle_temperature(self):
        """Calculate temperature based on sinusoidal cycle"""
        current_time = time.time()
        elapsed_time = current_time - self.cycle_start_time
        
        # Calculate position in cycle (0 to 2π)
        cycle_position = (elapsed_time / self.cycle_period) * 2 * math.pi
        
        # Calculate temperature using sine wave
        # sin(0) = 0, sin(π/2) = 1, sin(π) = 0, sin(3π/2) = -1, sin(2π) = 0
        temp_variation = math.sin(cycle_position) * self.temp_amplitude
        target_temp = self.temp_center + temp_variation
        
        return target_temp
    
    def _heartbeat_monitor(self):
        """Monitor thread to ensure simulation is running and restart if needed"""
        last_heartbeat = time.time()
        while True:
            try:
                current_time = time.time()
                
                # Check if simulation thread is alive
                if not self.simulation_thread.is_alive():
                    print("⚠️  Simulation thread died, restarting...")
                    self.simulation_thread = threading.Thread(target=self._simulate_temperature, daemon=True)
                    self.simulation_thread.start()
                    last_heartbeat = current_time
                
                # Print heartbeat every 30 seconds
                if current_time - last_heartbeat > 30:
                    print(f"💓 Simulator heartbeat: {datetime.now().strftime('%H:%M:%S')} - All threads alive")
                    last_heartbeat = current_time
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ Heartbeat monitor error: {e}")
                time.sleep(5)
    
    def _simulate_heating_control(self):
        """Background thread to simulate heating control unit cycling"""
        while True:
            try:
                # Only auto-cycle if not in manual mode
                if self.heating_control_manual_state is None:
                    current_time = time.time()
                    elapsed_time = current_time - self.heating_control_cycle_start
                    
                    # Calculate current state based on 15-second intervals
                    cycle_position = int(elapsed_time / self.heating_control_cycle_period) % 2
                    new_state = cycle_position  # 0 or 1
                    
                    old_state = self.inputs[HEATING_CONTROL_UNIT_ID]['value']
                    if old_state != new_state:
                        self.inputs[HEATING_CONTROL_UNIT_ID]['value'] = new_state
                        state_name = "ON" if new_state else "OFF"
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Heating Control Unit: {state_name} (Auto-cycle)")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ Heating control simulation error: {e}")
                time.sleep(5)
    
    def _simulate_temperature(self):
        """Background thread to simulate realistic temperature changes"""
        while True:
            try:
                # Use CONTROL_DHW_ID for temperature simulation
                if CONTROL_DHW_ID not in self.sensors:
                    time.sleep(1)
                    continue
                dhw_sensor = self.sensors[CONTROL_DHW_ID]
                furnace_relay = self.relays[FURNACE_RELAY_ID]
                
                current_temp = dhw_sensor['value']
                furnace_on = furnace_relay['value'] == 1
                
                if self.simulation_mode == 'auto':
                    # Auto mode: Follow sinusoidal cycle
                    new_temp = self._get_auto_cycle_temperature()

                    
                elif self.simulation_mode == 'manual':
                    # Manual mode: Apply manual adjustments
                    new_temp = current_temp + self.manual_temp_adjustment
               
                    # Apply furnace heating/cooling in manual mode too
                    if furnace_on:
                        temp_change = self.heating_rate  # Heat up
                    else:
                        temp_change = -self.cooling_rate  # Cool down towards ambient
               
                    new_temp = new_temp + temp_change
                    
                
                # Clamp temperature to reasonable bounds
                new_temp = max(15.0, min(new_temp, 90.0))
                
                # Update sensor
                old_temp = dhw_sensor['value']
                dhw_sensor['value'] = round(new_temp, 1)
                dhw_sensor['time'] = time.time()
                # Update CONTROL_HHW_ID if it's different from CONTROL_DHW_ID
                if CONTROL_HHW_ID != CONTROL_DHW_ID and CONTROL_HHW_ID in self.sensors:
                    self.sensors[CONTROL_HHW_ID]['value'] = dhw_sensor['value']
                    self.sensors[CONTROL_HHW_ID]['time'] = dhw_sensor['time']
                
                # Update other enabled thermometers with calculated values (excluding control sensors)
                for i, thermometer in enumerate(CONFIG['THERMOMETERS']):
                    if (i > 0 and thermometer['id'] != 'NONE' and 
                        thermometer['id'] in self.sensors and 
                        thermometer['id'] != CONTROL_DHW_ID and 
                        thermometer['id'] != CONTROL_HHW_ID):
                        # Generic simulation for any number of thermometers (excluding control sensors)
                        # Simulate each thermometer as a function of the main (DHW) sensor, with decreasing value and amplitude
                        # Example: Each subsequent sensor is further from the heat source
                        offset = 5 * i  # 5°C offset per sensor index
                        scale = max(0.2, 1.0 - 0.2 * i)  # Decrease scale for each sensor, min 0.2
                        self.sensors[thermometer['id']]['value'] = (dhw_sensor['value'] - offset) * scale
                        self.sensors[thermometer['id']]['time'] = dhw_sensor['time']

                self.manual_temp_adjustment = 0.0

                
                # Log temperature changes
                if abs(new_temp - old_temp) > 0.1:
                    if self.simulation_mode == 'auto':
                        cycle_progress = ((time.time() - self.cycle_start_time) / self.cycle_period) * 100
                        status = f"AUTO-CYCLE ({cycle_progress:.1f}%)"
                        if furnace_on:
                            status += " + HEATING"
                    else:
                        status = "MANUAL"
                        if furnace_on:
                            status += " + HEATING"
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {CONTROL_DHW_ID}: {new_temp:.1f}°C ({status})")
                    if CONTROL_HHW_ID != CONTROL_DHW_ID and CONTROL_HHW_ID in self.sensors:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {CONTROL_HHW_ID}: {new_temp:.1f}°C (copied from DHW)")
                
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                print(f"🔄 Continuing simulation...")
            
            time.sleep(1)  # Update every second
    
    def get_temperature(self, circuit_id):
        """Get temperature sensor data"""
        if circuit_id in self.sensors:
            return self.sensors[circuit_id].copy()
        return None
    
    def get_relay(self, circuit_id):
        """Get relay state"""
        if circuit_id in self.relays:
            return self.relays[circuit_id].copy()
        return None
    
    def set_relay(self, circuit_id, value):
        """Set relay state"""
        if circuit_id in self.relays:
            old_value = self.relays[circuit_id]['value']
            self.relays[circuit_id]['value'] = int(value)
            
            # Log relay changes
            if old_value != int(value):
                status = "ON" if int(value) else "OFF"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Furnace relay: {status}")
            
            return {
                'success': True,
                'result': self.relays[circuit_id].copy()
            }
        return {'success': False, 'error': 'Relay not found'}
    
    def get_digital_input(self, circuit_id):
        """Get digital input state"""
        if circuit_id in self.inputs:
            # Return full EVOK-compatible response
            return {
                'dev': 'di',
                'circuit': circuit_id,
                'value': self.inputs[circuit_id]['value'],
                'debounce': 30,
                'counter_modes': ['Enabled', 'Disabled'],
                'counter_mode': 'Enabled',
                'counter': 0,
                'mode': 'Simple',
                'modes': ['Simple', 'DirectSwitch']
            }
        return None

# Global simulator instance
simulator = EVOKSimulator()

@app.route('/json/temp/<circuit_id>', methods=['GET'])
def get_temperature(circuit_id):
    """EVOK API endpoint for temperature reading"""
    data = simulator.get_temperature(circuit_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Sensor not found'}), 404

@app.route('/json/ro/<circuit_id>', methods=['GET'])
def get_relay(circuit_id):
    """EVOK API endpoint for relay state reading"""
    data = simulator.get_relay(circuit_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Relay not found'}), 404

@app.route('/json/ro/<circuit_id>', methods=['POST'])
def set_relay(circuit_id):
    """EVOK API endpoint for relay state setting"""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({'success': False, 'error': 'Missing value parameter'}), 400
        
        result = simulator.set_relay(circuit_id, data['value'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/json/di/<circuit_id>', methods=['GET'])
def get_digital_input(circuit_id):
    """EVOK API endpoint for digital input reading"""
    data = simulator.get_digital_input(circuit_id)
    if data:
        return jsonify(data)
    return jsonify({'error': 'Digital input not found'}), 404

@app.route('/json/di/<circuit_id>', methods=['POST'])
def set_digital_input(circuit_id):
    """EVOK API endpoint for digital input setting (for simulator/testing)"""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({'success': False, 'error': 'Missing value parameter'}), 400
        
        # For simulator, we can directly set the input value
        if circuit_id == HEATING_CONTROL_UNIT_ID:
            simulator.inputs[circuit_id]['value'] = int(data['value'])
            # Reset manual override if setting value
            simulator.heating_control_manual_state = int(data['value'])
            return jsonify({'success': True, 'result': simulator.inputs[circuit_id]})
        
        return jsonify({'success': False, 'error': 'Digital input not supported'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for debugging"""
    cycle_progress = 0
    target_temp = 0
    
    if simulator.simulation_mode == 'auto':
        elapsed_time = time.time() - simulator.cycle_start_time
        cycle_progress = (elapsed_time / simulator.cycle_period) * 100
        target_temp = simulator._get_auto_cycle_temperature()
    
    return jsonify({
        'status': 'running',
        'simulation_mode': simulator.simulation_mode,
        'cycle_info': {
            'progress_percent': round(cycle_progress, 1),
            'target_temperature': round(target_temp, 1),
            'cycle_period_minutes': simulator.cycle_period / 60,
            'temp_range': f"{simulator.temp_min}°C - {simulator.temp_max}°C"
        },
        'manual_adjustment': simulator.manual_temp_adjustment,
        'heating_control': {
            'current_state': simulator.inputs[HEATING_CONTROL_UNIT_ID]['value'],
            'manual_override': simulator.heating_control_manual_state is not None,
            'cycle_period_seconds': simulator.heating_control_cycle_period
        },
        'sensors': simulator.sensors,
        'relays': simulator.relays,
        'inputs': simulator.inputs,
        'timestamp': datetime.now().isoformat()
    })


# https://unipitechnology.stoplight.io/docs/evok/qwveyanfg1gys-evok
if __name__ == '__main__':
    print("="*60)
    print("BandaskApp EVOK Simulator - Enhanced Version")
    print("="*60)
    print("API Endpoints:")
    # Display control temperature sensor endpoints
    print(f"  Control DHW Temperature: http://localhost:8080/json/temp/{CONTROL_DHW_ID}")
    if CONTROL_HHW_ID != CONTROL_DHW_ID:
        print(f"  Control HHW Temperature: http://localhost:8080/json/temp/{CONTROL_HHW_ID}")
    print(f"  All Temperature Sensors: Available at http://localhost:8080/json/temp/<circuit_id>")
    print(f"  Furnace Relay (GET):      http://localhost:8080/json/ro/{FURNACE_RELAY_ID}")
    print(f"  Furnace Relay (POST):     http://localhost:8080/json/ro/{FURNACE_RELAY_ID}")
    print(f"  Pump Relay (GET):         http://localhost:8080/json/ro/{PUMP_RELAY_ID}")
    print(f"  Pump Relay (POST):        http://localhost:8080/json/ro/{PUMP_RELAY_ID}")
    print(f"  Heating Control (GET):    http://localhost:8080/json/di/{HEATING_CONTROL_UNIT_ID}")
    print(f"  Heating Control (POST):   http://localhost:8080/json/di/{HEATING_CONTROL_UNIT_ID}")
    print("  Status:                   http://localhost:8080/status")
    print("="*60)
    
    try:
        print("🚀 Starting EVOK Simulator in infinite loop mode...")
        app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped by user")
    except Exception as e:
        print(f"❌ Simulator error: {e}")
        print("🔄 Restarting simulator in 5 seconds...")
        time.sleep(5)
        # Restart the simulator
        os.execv(sys.executable, ['python'] + sys.argv)
    finally:
        if simulator:
            simulator.cleanup_keyboard()

